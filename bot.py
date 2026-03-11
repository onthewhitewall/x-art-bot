import json
import random
import os
from playwright.sync_api import sync_playwright
import subprocess

# 作品データを読む
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

# 画像パス
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

# ----------------
# git push
# ----------------

subprocess.run(["git", "config", "user.name", "github-actions"])
subprocess.run(["git", "config", "user.email", "github-actions@github.com"])

subprocess.run(["git", "add", "posted.json"])
subprocess.run(["git", "commit", "-m", "update posted works"])

subprocess.run(["git", "push"])

# ----------------
# Xログイン
# ----------------

username = os.getenv("X_USERNAME")
password = os.getenv("X_PASSWORD")

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )

    page = browser.new_page(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )

    page.goto("https://x.com/login")

    # username
    page.wait_for_selector('input[name="text"]', timeout=60000)
    page.fill('input[name="text"]', username)
    page.keyboard.press("Enter")

    page.wait_for_timeout(4000)

    # 追加 username / email 確認
    if page.locator('input[name="text"]').count() > 0:
        page.fill('input[name="text"]', username)
        page.keyboard.press("Enter")

    page.wait_for_timeout(4000)

    # password が出るまで待つ
    page.wait_for_selector('input[name="password"]', timeout=60000)
    page.fill('input[name="password"]', password)
    page.keyboard.press("Enter")

    page.wait_for_timeout(6000)

    # 投稿画面
    page.goto("https://x.com/compose/post")

    page.wait_for_selector('input[type="file"]', timeout=60000)
    page.set_input_files('input[type="file"]', image_path)

    page.wait_for_selector('div[data-testid="tweetTextarea_0"]')
    page.fill('div[data-testid="tweetTextarea_0"]', text)

    page.click('div[data-testid="tweetButton"]')

    page.wait_for_timeout(5000)

    browser.close()
