import requests
from bs4 import BeautifulSoup

# レースページのURL (例: Netkeibaの対象レースページ)
url = "https://db.netkeiba.com/race/202306050811/"  # 適切なURLに置き換えてください

# スクレイピングヘッダーの設定
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
}

# レースデータを取得する関数
def scrape_race_data(url):
    try:
        # レースページを取得
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTPエラーがあれば例外を投げる
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # レース情報を取得
        race_info = extract_race_info(soup)
        print("レース情報:", race_info)

        # 払い戻し情報を取得
        payouts = extract_payouts(soup)
        print("\n払い戻し情報:")
        for payout in payouts:
            print(payout)

    except requests.exceptions.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")

# レース情報を抽出する関数
def extract_race_info(soup):
    race_info = {}

    # レース名
    race_name_tag = soup.find("h1")
    if race_name_tag:
        race_info["race_name"] = race_name_tag.text.strip()

    # レース詳細情報（日時、距離、天候など）
    details_tag = soup.find("p", class_="smalltxt")
    if details_tag:
        race_info["details"] = details_tag.text.strip()

    return race_info

# 払い戻し情報を抽出する関数
def extract_payouts(soup):
    payout_data = []

    # 払い戻しテーブルを取得
    payout_table = soup.find("dl", class_="pay_block")
    if not payout_table:
        print("払い戻し情報が見つかりませんでした。")
        return payout_data

    tables = payout_table.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            # 馬券種別、組み合わせ、金額を抽出
            cols = row.find_all("td")
            if len(cols) >= 3:
                payout_data.append({
                    "type": row.find("th").text.strip(),  # 馬券種別
                    "combination": cols[0].text.strip(),  # 組み合わせ
                    "amount": cols[1].text.strip(),       # 払い戻し金額
                })

    return payout_data

# 実行
if __name__ == "__main__":
    scrape_race_data(url)
