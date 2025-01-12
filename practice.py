from selenium import webdriver
from bs4 import BeautifulSoup

# ブラウザの設定
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # ヘッドレスモード（画面を表示しない）
driver = webdriver.Chrome(options=options)

# ページを開く
url = "https://db.netkeiba.com/race/202405050812"
driver.get(url)

# ページソースを取得してBeautifulSoupで解析
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# データを抽出
data_intro = soup.find("div", class_="data_intro")
if data_intro:
    race_title = data_intro.find("h1").text.strip()
    race_details = data_intro.find("p").text.strip()
    date_info = data_intro.find("p", class_="smalltxt").text.strip()

    print("Race Title:", race_title)
    print("Race Details:", race_details)
    print("Date Info:", date_info)
else:
    print("Race information not found.")
