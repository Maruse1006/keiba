from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

<<<<<<< Updated upstream
# レースページのURL (例: Netkeibaの対象レースページ)
url = "https://db.netkeiba.com/race/202306050811/" 
=======
app = Flask(__name__)
CORS(app)  # CORSを有効化
>>>>>>> Stashed changes

# 払い戻し情報をチェックするエンドポイント
@app.route('/check_payout', methods=['POST'])
def check_payout():
    try:
        print("Received a POST request at /check_payout")  # デバッグ用ログ
        data = request.json
        print(f"Received data: {data}")  # デバッグ用ログ

        day_count = data.get('dayCount')
        place = data.get('place')
        race = data.get('race')
        round_number = data.get('round')
        combinations = data.get('combinations')

        # 入力データの検証
        if not (day_count and place and race and round_number and combinations):
            print("Invalid input data")  # デバッグ用
            return jsonify({'success': False, 'error': 'Invalid input data'}), 400

        print("Starting scraping process...")  # デバッグ用ログ
        payouts = scrape_payouts(day_count, place, race, round_number)
        print(f"Scraping completed. Payouts: {payouts}")  # デバッグ用ログ

        # フロントエンドからの組み合わせと照合
        payout_amount = 0
        for payout in payouts:
            if payout['combination'] in combinations:
                payout_amount = payout['amount']
                break

        print(f"Calculated payout amount: {payout_amount}")  # デバッグ用ログ
        return jsonify({'success': True, 'payout': payout_amount})
    except Exception as e:
        print(f"Error: {e}")  # デバッグ用にエラーを出力
        return jsonify({'success': False, 'error': str(e)}), 500

# 払い戻し情報をスクレイピングする関数
def scrape_payouts(day_count, place, race, round):
    url = f"https://db.netkeiba.com/race/2024{place}{round}{day_count}{race}/"
    print(f"Scraping URL: {url}")  # URLをログに出力

    # ユーザーエージェントの追加
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Referer": "https://db.netkeiba.com/"  # 必要に応じてリファラーを設定
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch race data. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    payouts = []
    payout_table = soup.find("dl", class_="pay_block")
    if not payout_table:
        print("No payout information found.")  # デバッグ用メッセージ
        return payouts

    # 払い戻し情報を取得
    tables = payout_table.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                payouts.append({
                    'combination': cols[0].text.strip(),  # 払い戻しの組み合わせ
                    'amount': int(cols[1].text.strip().replace('¥', '').replace(',', '')),  # 払い戻し金額
                })

    print(f"Payouts extracted: {payouts}")  # デバッグ用
    return payouts

# アプリを実行
if __name__ == '__main__':
    print("Starting Flask server...")  # デバッグ用
    app.run(host='0.0.0.0', port=8000, debug=True)
