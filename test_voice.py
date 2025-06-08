# import requests

# api_key = "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"
# url = "https://api.openai.com/v1/audio/speech"
# payload = {
#     "model": "tts-1",
#     "voice": "fable",  # "fable", "shimmer", "nova" 都是女性
#     "input": "Hello, how are you? This is a test."
# }
# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json",
# }
# response = requests.post(url, headers=headers, json=payload)
# with open("test_fable.mp3", "wb") as f:
#     f.write(response.content)
# print("done")

# import re
# import requests
# import subprocess
# import os

# text = "What's your favorite food? My favorite food is cheese. I really enjoy how flavorful it is! It pairs perfectly with so many things."

# def split_text(text):
#     return [s.strip() for s in re.split(r'(?<=[。！？.!?])', text) if s.strip()]

# api_key = "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"
# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# mp3files = []
# for idx, sentence in enumerate(split_text(text)):
#     payload = {"model": "tts-1", "voice": "fable", "input": sentence}
#     response = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
#     fname = f"part_{idx+1}.mp3"
#     with open(fname, "wb") as f:
#         f.write(response.content)
#     mp3files.append(fname)

# # 產生filelist.txt供ffmpeg合併
# with open("filelist.txt", "w", encoding="utf-8") as f:
#     for fname in mp3files:
#         f.write(f"file '{fname}'\n")

# # 用ffmpeg合併全部mp3為單一output.mp3
# outputfile = "output.mp3"
# subprocess.run([
#     "ffmpeg", "-y",
#     "-f", "concat", "-safe", "0",
#     "-i", "filelist.txt",
#     "-c", "copy",
#     outputfile
# ], check=True)

# print(f"全部完成，總合併MP3為 {outputfile}")

# # 刪除臨時檔
# os.remove("filelist.txt")
# for fname in mp3files:
#     os.remove(fname)

import re
import requests
import subprocess
import os

def split_text(text):
    return [s.strip() for s in re.split(r'(?<=[。！？.!?])', text) if s.strip()]

def get_silence_sec(sentence):
    n = max(1, len(sentence) // 10)
    return n

api_key = "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"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

text = "what's your favorite food? My favorite food is cheese, I really enjoy how flavorful it is, and it pairs perfectly with so many things- like sandwich, salad and wine, it can really make any dish taste better.have you always like cheese?Actually, I didn't always like cheese. When I was younger, I wasn’t a big fan of it because I found the taste too strong. But as I got older, I started to appreciate it more, especially when I discovered how well it pairs with different foods. Are there any foods you dislike? I don’t really like bitter melon. I can’t quite get used to the flavor. Even though some people enjoy it, I’d rather avoid it. What are some traditional foods in your country? Bubble milk tea is a traditional and iconic drink in Taiwan, it combines chewy Boba with milk tea, creating a delicious and refreshing drink. Do you have a healthy diet? Not exactly, but I'm trying to. I mostly prefer eating meat, but I make an effort to eat vegetables from time to time for the sake of my health. Do you play any sports? I used to play basketball when I was in high school. Back then, we had regular sports classes, which made it easier to find people to play with. It was really fun, and those moments are some of my best memories from school. Do you watch sports on TV? I don’t really watch sports on TV. I usually use my phone to watch YouTube instead. I’m really into figure skating--the type that goes with music and features spins and artistic movements. I find it both enjoyable and elegant to watch. What is the most popular sport in your country? In my country, I think the most popular sport is baseball. It has a long history in Taiwan. One special thing is the cheerleading culture--it’s really lively and fun. Even a famous Korean cheerleader, Lee Da-hye, came to Taiwan and joined the cheer squad. Is it important for children to play sports? Yes. Firstly, it helps them stay healthy and active, which is essential for physical development. Secondly, sports teach valuable life skills such as teamwork, discipline, and perseverance. It also gives them a chance to make friends and reduce stress. Overall, playing sports contributes to both their physical and emotional well-being.Do you like watch TV?Not really. I don’t often watch traditional TV. Instead, I usually use my phone to watch content on platforms like YouTube and Disney+. It’s more convenient and I can choose exactly what I want to watch anytime.What are the most popular TV shows in your country? In Taiwan, Meteor Garden is really popular. People love it because of the romantic story and strong characters. It became a big hit, especially among young people, and is still remembered as a classic today.Has the internet affect your viewing habits? Yes, it has. I don’t really watch traditional TV anymore. I usually watch YouTube and Disney on my phone because it’s more convenient and I can choose what I want to watch anytime.What was your favorite TV show (when you were a child? ).I would say Mr. Bean was my favorite TV show when I was a child. I loved how funny it was, even without much speaking. It always made me laugh. Now, my favorite is The Devil Wears Prada. I love it because it shows the price of being successful--how much effort and sacrifice it takes. It’s inspiring, but also makes me think about work-life balance.what kind of TV programmes do you like to watch? I would say I like nature programmes, especially ones like BBC Nature. I enjoy learning about animals and the environment. The visuals are amazing, and it helps me relax while also learning something new.Do you like watching TV shows from other countries? Yes, I do. I especially like watching BBC nature shows. They’re really well-made and give me a chance to learn about wildlife and nature from different parts of the world.How is the weather today?It’s quite sunny today with a light breeze. It’s a perfect day to go outside and enjoy the fresh air.It’s cold and rainy today. The sky is grey, and it’s been drizzling on and off, so I’d rather stay indoors.Today is really hot, the sun is strong, and it feels a bit uncomfortable to stay outside for too long.It’s quite cloudy today. There’s no sunshine, and the sky looks a bit gloomy. I think it might rain later.What's your favorite kind of weather? I would say cloudy weather is my favorite. It’s not too hot or too cold, and the soft light feels calm and relaxing. I enjoy going for walks when the sky is grey--it feels peaceful.What is the climate like in your country? In Taiwan, the weather is mostly warm and humid. Summers are hot and sometimes rainy, especially with typhoons. Winters are short and not very cold, except in the north where it can get a bit chilly. Overall, it’s quite comfortable most of the year.Does the weather affect people's lives in your country? Yes, it does. For example, during typhoon season, schools and offices might close for safety. Also, the hot and humid summer makes people prefer staying indoors or using air conditioning. The weather really influences what people wear and how they plan their day.Do people change in summer? Yes, I think so. In summer, people usually wear lighter clothes and spend more time outdoors, like going to the beach or having barbecues. Some people also become more active or energetic because of the longer daylight hours.Is there any type of weather you really don't like? Yes, I really don’t like very hot and humid weather. It makes me feel tired and uncomfortable, and it’s hard to focus or enjoy outdoor activities. I prefer cooler or cloudy days.Does bad weather ever affect transport in your country? Yes, it does. During typhoons or heavy rain, some trains and flights get delayed or canceled. Roads can also flood, which causes traffic jams. People usually try to stay home when the weather is really bad.How important is the internet to you?The internet is extremely important to me. I rely on it for almost everything--from studying and doing research to communicating with friends and staying updated with the news. As a student, I often use online platforms to attend classes, submit assignments, and collaborate with classmates. It also helps me relax, whether that’s watching videos, listening to music, or reading articles. Honestly, I’d find it very difficult to function efficiently without internet access nowadays.How often do you use the internet? As a software engineer, I use the internet almost constantly--probably around 7 hours a day or even more. It’s an essential part of my job, whether I’m looking up documentation, collaborating with team members, or using cloud-based tools for development and testing. Even outside of work, I rely on it for learning new technologies, watching tutorials, and staying up to date with industry trends. So, I’d say I’m online nearly all the time.Do you use it for work or in your free time?I use the internet for both work and leisure. During work hours, it’s mainly for programming, researching technical issues, and communicating with colleagues. In my free time, I switch to more relaxing activities like watching videos, reading news, or exploring new tools and frameworks out of personal interest. So, it plays a big role in both my professional and personal life.What's your favorite website(app)?My favorite website and app is YouTube. I use it almost every day, both for learning and relaxation. It’s full of useful content, especially tech-related videos that help me improve my skills as a software engineer. I enjoy watching tutorials, coding sessions, and sometimes even documentaries or music videos. I like it so much that I even created a Chrome extension to improve accessibility for YouTube users.Do you think you use the internet too much? Yes, I think I do use the internet a bit too much, especially because of my work. I spend long hours in front of a screen, which can be tiring and has started to affect my eyes. Sometimes I get eye strain or headaches, so I’m trying to take more breaks and use blue light filters. It’s not easy, but I know it’s important for my health.how will the internet(AI) develop in the future? I think AI will change the way we develop software quite a lot. Instead of spending most of our time writing every line of code, developers will focus more on the overall design and logic of an application. AI tools will be able to generate routine code, so what matters most will be having good ideas, understanding user needs, and knowing how systems work. For example, we might simply explain to an AI what we want to build, and it will write much of the code for us, leaving us to handle higher-level decisions and problem-solving.Are there any positive/ negative things about the internet? On the positive side, it allows me to access information quickly and connect with people from all over the world. It also makes my work as a software engineer much more efficient. However, there are negative aspects as well. For example, spending too much time online can hurt my eyes and there’s also a risk of encountering misinformation or privacy issues. So overall, while the internet is very useful, it’s important to use it carefully.Do you care about fashion? Not really--function matters more to me than fashion. I usually choose clothes that are comfortable and practical, especially for work. I do try to look clean and well-dressed, but I don’t follow trends or worry about wearing popular brands. For me, it’s more important that my clothes suit my daily activities.What kind of things do you normally wear? I usually wear casual and comfortable clothes, like T-shirts, jeans, and sneakers. If I’m working from home, I keep it simple--something easy to move around in. But if I need to go out or attend a meeting, I’ll wear something a bit more formal, like a shirt or a jacket. Overall, I prefer clothes that are practical and fit my daily routine.Are there any traditional clothes in your country? Yes. For example, during Chinese New Year or weddings, women might wear a qipao, and men might wear a changshan. Also, Taiwan has many indigenous groups, and they have their own traditional clothes with colorful patterns. These clothes are usually worn during festivals or special events.Where do you usually purchase your clothes? I usually buy my clothes online, it’s more convenient and I can compare prices easily. Sometimes I go to stores if I want to try something on or need it quickly. I don’t shop very often, so I just buy what I need when the season changes or if something wears out.Have you ever bought clothes online? Yes. It’s really convenient, I can shop anytime and compare different styles and prices. Sometimes the size isn’t perfect, but most websites let you return or exchange items, so it’s not a big problem. I usually check reviews before buying to make sure the quality is good.Do people from your country think fashion is important? In general, I don’t think most people in Taiwan see fashion as very important. Many people prefer to wear simple and comfortable clothes instead of following the latest trends. Of course, some young people, especially in big cities like Taipei, care more about fashion and like to express themselves through their style. But overall, I’d say practicality is more important than fashion for most people in Taiwan."
sentences = split_text(text)
mp3files = []

for idx, sentence in enumerate(sentences):
    # 語音
    payload = {"model": "tts-1", "voice": "fable", "input": sentence}
    response = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
    speech_file = f"part_{idx+1}.mp3"
    with open(speech_file, "wb") as f:
        f.write(response.content)
    mp3files.append(speech_file)

    # 每句後動態靜音片段（末句不用加）
    if idx < len(sentences) - 1:
        sec = get_silence_sec(sentence)
        silence_file = f"silence_{idx+1}.mp3"
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=44100",
            "-t", str(sec), "-q:a", "9", "-acodec", "libmp3lame", silence_file
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mp3files.append(silence_file)
        print(f"產生靜音：{silence_file} ({sec}秒)")

# filelist
with open("filelist.txt", "w", encoding="utf-8") as f:
    for fname in mp3files:
        f.write(f"file '{fname}'\n")

outputfile = "output.mp3"
# 合併時務必重新編碼（可避免各段參數差異導致失效或靜音失真）
subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", "filelist.txt",
    "-acodec", "libmp3lame", "-ar", "44100", "-ab", "192k",
    outputfile
], check=True)

# 檔案清理
for f in mp3files + ["filelist.txt"]:
    os.remove(f)

print(f"完成！已產生 {outputfile}（有動態長度靜音）")