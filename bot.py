import json
import random

# 作品データ
with open("bot_output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

works = data["works"]

# 投稿履歴
try:
    with open("posted.json", "r") as f:
        posted = json.load(f)
except:
    posted = []

# 未投稿作品
remaining = [w for w in works if w["id"] not in posted]

# 全部投稿済みならリセット
if not remaining:
    posted = []
    remaining = works

# ランダム選択
work = random.choice(remaining)

# 投稿履歴更新
posted.append(work["id"])

with open("posted.json", "w") as f:
    json.dump(posted, f)

# 画像
image_path = f"images_bot/bot_{work['image']}"

# タイトル
jp = work["title_jp"]
en = work["title_en"]

if en:
    title = f"{jp} / {en}"
else:
    title = jp

# 投稿文
text = f"""ID: {work["id"]}

{title}
{work["y_created"]}

https://onthewhitewall.com
"""

print(image_path)
print(text)
