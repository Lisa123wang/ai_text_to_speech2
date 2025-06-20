#!/usr/bin/env python3
import re
import requests
import sys
import subprocess
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
import shutil


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# 预编译正则，减少重复编译开销
_SENTENCE_PATTERN = re.compile(r'.+?(?<!\b[A-Za-z])[\.\!\?](?=\s|$)')
_PUNCT_PATTERN    = re.compile(r'(?:,|—)\s*')
_CONN_PATTERN     = re.compile(r'\s+(?:and|but|or|so|yet|nor|because|although|though|if|while|for)\b')

def split_text_phrases(text, max_words=12, short_threshold_words=6):
    """
    英文句子按“单词数”拆分，并在多段拆分后重读原句：
      1. 用 [.?!] 抓完整原句
      2. 如果单词数 <= max_words，直接保留
      3. 否则先按标点(逗号/破折号)拆分
         - 拆出来的片段如果单词数 >= short_threshold_words，再按连接词拆
      4. 对所有仍超长的片段按单词边界强制拆成每段不超过 max_words
      5. 末段过短就合并到前一段
      6. 如果最终拆出了多段，末尾附上原句一次
    """
    if not text or not text.strip():
        return []

    # 本地绑定加速调用
    find_sentences = _SENTENCE_PATTERN.findall
    punct_split    = _PUNCT_PATTERN.split
    conn_split     = _CONN_PATTERN.split

    result = []
    for sent in find_sentences(text):
        sent = sent.strip()
        words = sent.split()
        # 2. 单词数不超限
        if len(words) <= max_words:
            result.append(sent)
            continue

        # 3. 按标点拆
        refined = []
        for part in punct_split(sent):
            part = part.strip()
            if not part:
                continue
            pw = len(part.split())
            if pw <= max_words:
                refined.append(part)
            elif pw >= short_threshold_words:
                # 按连接词再拆
                refined.extend(s.strip() for s in conn_split(part) if s.strip())
            else:
                refined.append(part)

        # 4. 强制按单词边界拆超长段
        local_chunks = []
        append_chunk = local_chunks.append
        for seg in refined:
            seg_words = seg.split()
            if len(seg_words) <= max_words:
                append_chunk(seg)
            else:
                buf = []
                for w in seg_words:
                    if buf and len(buf) + 1 > max_words:
                        append_chunk(' '.join(buf))
                        buf = [w]
                    else:
                        buf.append(w)
                if buf:
                    append_chunk(' '.join(buf))

        # 5. 合并过短末段
        merged = []
        for seg in local_chunks:
            if not merged:
                merged.append(seg)
            else:
                if len(seg.split()) < short_threshold_words:
                    merged[-1] += ' ' + seg
                else:
                    merged.append(seg)
        local_chunks = merged

        # 6. 收集结果并原句重读
        result.extend(local_chunks)
        if len(local_chunks) > 1:
            result.append(sent)

    return [r for r in result if r.strip()]





def get_silence_sec(sentence):
    # 每 10 字約 1 秒，至少 0.5 秒（減少靜音時間）
    return max(0.5, len(sentence) // 15)

# ─── 主流程 ─────────────────────────────────────────────

if len(sys.argv) < 4:
    print("Usage: python your_tts.py <input_txt_or_text> <voice> <output_mp3>")
    sys.exit(1)

arg, voice, outputfile = sys.argv[1], sys.argv[2], sys.argv[3]

# 讀取文字或檔案
if os.path.isfile(arg):
    with open(arg, 'r', encoding='utf-8') as f:
        text = f.read()
else:
    text = arg

# OpenAI API Key
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 切段
phrases = split_text_phrases(text)
tmp_dir = tempfile.gettempdir()
max_workers = 20  # 可調：同時送幾個請求

def process_phrase(idx, sent):
    """對單一段做 TTS，回傳語音+靜音檔案列表"""
    files = []
    if not sent.strip():
        return files

    # 1️⃣ 呼叫 OpenAI TTS
    payload = {"model": "tts-1", "voice": voice, "input": sent}
    resp = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
    if resp.status_code != 200:
        sys.stderr.write(f"[ERROR] segment {idx} → {resp.status_code}\n{resp.text}\n")
        sys.exit(1)

    # 2️⃣ 存語音檔
    part_mp3 = os.path.join(tmp_dir, f"part_{os.getpid()}_{idx:04d}.mp3")
    with open(part_mp3, 'wb') as fw:
        fw.write(resp.content)
    files.append(part_mp3)

    # 3️⃣ 如果不是最後一段，生成靜音檔（用更快的方法）
    if idx != len(phrases) - 1:
        sec = get_silence_sec(sent)
        silence_mp3 = os.path.join(tmp_dir, f"silence_{os.getpid()}_{idx:04d}.mp3")
        
        # 使用更快的靜音生成方法
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", 
            "-i", f"anullsrc=channel_layout=mono:sample_rate=24000",  # 降低採樣率
            "-t", str(sec), "-c:a", "libmp3lame", "-b:a", "64k",     # 降低比特率
            silence_mp3
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        files.append(silence_mp3)

    return files

# ─── 並行執行 TTS ───────────────────────────────────────
print("正在生成語音片段...")
mp3files = []
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交所有任務
    future_by_idx = {
        idx: executor.submit(process_phrase, idx, sent)
        for idx, sent in enumerate(phrases)
    }
    # 按照原始順序收結果
    for idx in range(len(phrases)):
        result = future_by_idx[idx].result()
        if result:
            mp3files.extend(result)  # extend 因為現在返回 list

print(f"生成了 {len(mp3files)} 個語音片段，開始合併...")

# ─── 快速合併方法：使用 ffmpeg filter_complex ───────────
def fast_merge_with_silence(mp3files, output_file, phrases):
    if not mp3files:
        return
    
    if len(mp3files) == 1:
        # 只有一個文件，直接複製
        shutil.copy2(mp3files[0], output_file)
        return
    
    # 構建 ffmpeg 命令
    cmd = ["ffmpeg", "-y"]
    
    # 添加所有輸入文件
    for mp3 in mp3files:
        cmd.extend(["-i", mp3])
    
    # 構建 filter_complex
    filter_parts = []
    
    for i in range(len(mp3files)):
        if i == len(mp3files) - 1:
            # 最後一個不加靜音
            filter_parts.append(f"[{i}:a]")
        else:
            # 添加靜音
            silence_sec = get_silence_sec(phrases[i])
            filter_parts.append(f"[{i}:a]")
            filter_parts.append(f"aevalsrc=0:duration={silence_sec}:sample_rate=44100[silence{i}];")
            filter_parts.append(f"[silence{i}]")
    
    # 合併所有音頻
    inputs = "".join([f"[{i}:a]" if i == len(mp3files)-1 else f"[{i}:a][silence{i}]" 
                     for i in range(len(mp3files))])
    
    # 簡化版：直接 concat
    concat_filter = "".join([f"[{i}:a]" for i in range(len(mp3files))]) + f"concat=n={len(mp3files)}:v=0:a=1[out]"
    
    cmd.extend([
        "-filter_complex", concat_filter,
        "-map", "[out]",
        "-c:a", "libmp3lame",
        "-b:a", "128k",  # 降低比特率加快處理
        output_file
    ])
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

# ─── 使用更快的合併方法：直接用 concat 協議 ───────────────
def ultra_fast_merge(mp3files, output_file):
    """最快的合併方法：使用 concat 協議，不重新編碼"""
    if not mp3files:
        return
        
    if len(mp3files) == 1:
        shutil.copy2(mp3files[0], output_file)
        return
    
    # 創建 concat 文件列表
    concat_txt = os.path.join(tmp_dir, f"concat_{os.getpid()}.txt")
    with open(concat_txt, 'w', encoding='utf-8') as f:
        for mp3_file in mp3files:
            # 轉義文件路徑中的特殊字符
            escaped_path = mp3_file.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
    
    # 使用 concat demuxer，stream copy（不重新編碼）
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", 
        "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",  # 關鍵：直接複製，不重新編碼
        output_file
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # 清理臨時文件
    try:
        os.remove(concat_txt)
    except:
        pass

# 執行合併
ultra_fast_merge(mp3files, outputfile)

# 清理臨時文件
for mp3_file in mp3files:
    try:
        os.remove(mp3_file)
    except:
        pass

print(f"合併完成：{outputfile}")