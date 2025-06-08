import re, requests, sys, subprocess, os, tempfile



def split_text_phrases(text, max_len=55):
    SEP1 = r'[.!?]'
    SEP2 = r'(,| and | but | or |且|而且|或者|但是|或是|，)'
    result = []

    # 先按句末標點分句
    sent_list = re.split(r'(?<=' + SEP1 + r')\s+', text.strip())
    for sent in sent_list:
        s = sent.strip()
        if not s:
            continue

        # 只有長句才進行細分
        if len(s) > max_len:
            # 1. 粗分：遇到逗號或連接詞就切
            segs = []
            last = 0
            for m in re.finditer(SEP2, s):
                end = m.end()
                segs.append(s[last:end].strip())
                last = end
            segs.append(s[last:].strip())

            # 2. 合併過短的片段
            merged = []
            for seg in segs:
                if not seg:
                    continue
                # 根據是否含英文判斷「短」的標準
                if re.search(r'[a-zA-Z]', seg):
                    is_short = len(seg.split()) < 3
                else:
                    is_short = len(seg) < 3
                if is_short and merged:
                    merged[-1] += ' ' + seg
                else:
                    merged.append(seg)

            # 3. 再檢查最後一片過短的，合併到前一片
            if len(merged) >= 2:
                last_seg = merged[-1]
                if (re.search(r'[a-zA-Z]', last_seg) and len(last_seg.split()) < 3) or \
                   (not re.search(r'[a-zA-Z]', last_seg) and len(last_seg) < 3):
                    merged[-2] += ' ' + merged[-1]
                    merged.pop()

            # 4. 對仍然超長的段落，再強制按長度拆一次
            chunks = []
            for chunk in merged:
                if len(chunk) > max_len:
                    words = chunk.split()
                    curlen = 0
                    curr = []
                    segments = []
                    for w in words:
                        if curlen + len(w) + 1 > max_len:
                            segments.append(' '.join(curr))
                            curr = [w]
                            curlen = len(w)
                        else:
                            curr.append(w)
                            curlen += len(w) + 1
                    if curr:
                        segments.append(' '.join(curr))

                    # 合併最後過短的子段
                    if len(segments) >= 2 and len(segments[-1].split()) < 3:
                        segments[-2] += ' ' + segments[-1]
                        segments.pop()

                    chunks.extend(segments)
                else:
                    chunks.append(chunk.strip())

            # 5. 把這些 chunk 放入結果
            result.extend(chunks)

            # 6. 只有真的拆成多段時，才再讀一次完整句
            if len(chunks) > 1:
                result.append(s)
        else:
            # 短句直接一次讀完
            result.append(s)

    # 避免空字串
    return [x for x in result if x]



def get_silence_sec(sentence):
    # 可自訂：以每15字為一秒
    return max(1, len(sentence)//10)

if len(sys.argv)<4:
    print("Usage: python your_tts.py 'text' 'voice' 'outfile'")
    sys.exit(1)

text, voice, outputfile = sys.argv[1], sys.argv[2], sys.argv[3]
api_key = "API"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 用進階分段 & 子句結尾句都會出現在語音中
phrases = split_text_phrases(text, max_len=55)

tmp_dir = tempfile.gettempdir()
mp3files = []

for idx, sent in enumerate(phrases):
    # 跳空片段
    if not sent.strip():
        continue
    payload = {"model": "tts-1", "voice": voice, "input": sent}
    response = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
    mp3 = os.path.join(tmp_dir, f"part_{os.getpid()}_{idx}.mp3")
    with open(mp3, "wb") as f:
        f.write(response.content)
    mp3files.append(mp3)
    # 靜音暫存(句末才不加)
    if idx != len(phrases) - 1:
        sec = get_silence_sec(sent)
        silence_mp3 = os.path.join(tmp_dir, f"silence_{os.getpid()}_{idx}.mp3")
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=44100",
            "-t", str(sec),
            "-q:a", "9", "-acodec", "libmp3lame", silence_mp3
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        mp3files.append(silence_mp3)

concat_txt = os.path.join(tmp_dir, f"{os.getpid()}.txt")
with open(concat_txt, "w", encoding='utf-8') as f:
    for fn in mp3files:
        f.write(f"file '{fn}'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", concat_txt,
    "-acodec", "libmp3lame", "-ar", "44100", "-ab", "192k", outputfile
], check=True)

