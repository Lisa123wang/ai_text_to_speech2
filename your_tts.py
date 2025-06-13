#!/usr/bin/env python3
import re
import requests
import sys
import subprocess
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

def split_text_phrases(text, max_len=55):
    SEP1 = r'[.!?]'
    SEP2 = r'(,| and | but | or | - | in | on | as | are | was，)'
    result = []

    # 1️⃣ 按句末标点分句
    sent_list = re.split(r'(?<=' + SEP1 + r')\s+', text.strip())
    for sent in sent_list:
        s = sent.strip()
        if not s:
            continue

        if len(s) > max_len:
            # 2️⃣ 第一次粗分
            segs, last = [], 0
            for m in re.finditer(SEP2, s):
                segs.append(s[last:m.end()].strip())
                last = m.end()
            segs.append(s[last:].strip())
            segs = [seg for seg in segs if seg]

            # 3️⃣ 合并过短片段
            merged = []
            for seg in segs:
                if re.search(r'[a-zA-Z]', seg):
                    is_short = len(seg.split()) < 3
                else:
                    is_short = len(seg) < 3
                if is_short and merged:
                    merged[-1] += ' ' + seg
                else:
                    merged.append(seg)
            merged = [m for m in merged if m]

            # 4️⃣ 保护性合并最后过短片段
            if len(merged) >= 2:
                last_seg = merged[-1]
                too_short = (
                    (re.search(r'[a-zA-Z]', last_seg) and len(last_seg.split()) < 3)
                    or
                    (not re.search(r'[a-zA-Z]', last_seg) and len(last_seg) < 3)
                )
                if too_short:
                    try:
                        merged[-2] += ' ' + merged.pop()
                    except IndexError:
                        pass

            # 5️⃣ 对仍然超长的 merged 段再按长度拆分
            chunks = []
            for chunk in merged:
                if len(chunk) > max_len:
                    words = chunk.split()
                    curr, curlen, parts = [], 0, []
                    for w in words:
                        if curlen + len(w) + 1 > max_len:
                            parts.append(' '.join(curr))
                            curr, curlen = [w], len(w)
                        else:
                            curr.append(w)
                            curlen += len(w) + 1
                    if curr:
                        parts.append(' '.join(curr))
                    # 5.1️⃣ 合并最后过短子段
                    if len(parts) >= 2:
                        last_p = parts[-1]
                        too_short_p = (
                            (re.search(r'[a-zA-Z]', last_p) and len(last_p.split()) < 3)
                            or
                            (not re.search(r'[a-zA-Z]', last_p) and len(last_p) < 3)
                        )
                        if too_short_p:
                            try:
                                parts[-2] += ' ' + parts.pop()
                            except IndexError:
                                pass
                    chunks.extend(parts)
                else:
                    chunks.append(chunk.strip())

            # 6️⃣ 收集
            result.extend(chunks)
            # 7️⃣ 如果拆成多段，再保留原句
            if len(chunks) > 1:
                result.append(s)
        else:
            result.append(s)

    return [x for x in result if x]

def get_silence_sec(sentence):
    # 每 10 字約 1 秒，至少 1 秒
    return max(1, len(sentence) // 10)

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
api_key = "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"  # 請替換成自己的
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 切段
phrases = split_text_phrases(text)
tmp_dir = tempfile.gettempdir()
max_workers = 20  # 可調：同時送幾個請求

def process_phrase(idx, sent):
    """對單一段做 TTS，並回傳 mp3 路徑列表（語音＋靜音）"""
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
    part_mp3 = os.path.join(tmp_dir, f"part_{os.getpid()}_{idx}.mp3")
    with open(part_mp3, 'wb') as fw:
        fw.write(resp.content)
    files.append(part_mp3)

    # 3️⃣ 如果不是最後一段，就產生並加上靜音
    if idx != len(phrases) - 1:
        sec = get_silence_sec(sent)
        silence_mp3 = os.path.join(tmp_dir, f"silence_{os.getpid()}_{idx}.mp3")
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=44100",
            "-t", str(sec),
            "-q:a", "9", "-acodec", "libmp3lame", silence_mp3
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        files.append(silence_mp3)

    return files

# ─── 並行執行 TTS ───────────────────────────────────────
mp3files = []
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交所有任務
    future_by_idx = {
        idx: executor.submit(process_phrase, idx, sent)
        for idx, sent in enumerate(phrases)
    }
    # 按照原始順序收結果
    for idx in range(len(phrases)):
        mp3files.extend(future_by_idx[idx].result())

# ─── 合併所有片段 ───────────────────────────────────────
concat_txt = os.path.join(tmp_dir, f"{os.getpid()}.txt")
with open(concat_txt, 'w', encoding='utf-8') as f:
    for fn in mp3files:
        f.write(f"file '{fn}'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", concat_txt,
    "-acodec", "libmp3lame", "-ar", "44100", "-ab", "192k", outputfile
], check=True)

print(f"合併完成：{outputfile}")
