from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # CORSを有効化

@app.route('/check_payout', methods=['POST'])
def check_payout():
    try:
        print("Received a POST request at /check_payout")  # デバッグ用ログ
        data = request.json
        print(f"Received data: {data}")  # デバッグ用ログ

        # 必須データの取得と検証
        day_count = data.get('dayCount')
        place = data.get('place')
        race = data.get('race')
        round_number = data.get('round')
        combinations = data.get('combinations')
        bet_type = data.get('name')  # フロントエンドから賭けの種類

        if not (day_count and place and race and round_number and combinations and bet_type):
            print("Invalid input data")  # デバッグ用
            return jsonify({'success': False, 'error': 'Invalid input data'}), 400

        print("Starting scraping process...")  # デバッグ用ログ
        payouts = scrape_payouts(day_count, place, race, round_number)
        print(f"Scraping completed. Payouts: {payouts}")  # デバッグ用ログ

        # 払い戻し金額の計算
        payout_amount = calculate_payout(payouts, combinations, bet_type)
        print(f"Calculated payout amount: {payout_amount}")  # デバッグ用ログ

        return jsonify({'success': True, 'payout': payout_amount})
    except Exception as e:
        print(f"Error: {e}")  # デバッグ用
        return jsonify({'success': False, 'error': str(e)}), 500

def scrape_payouts(day_count, place, race, round):
    """スクレイピングして払い戻しデータを取得"""
    day_count_str = f"{int(''.join(filter(str.isdigit, day_count))):02}"  # 数字部分のみ抽出
    place_str = f"{int(place):02}"
    race_str = f"{int(race):02}"
    round_str = f"{int(''.join(filter(str.isdigit, round))):02}"  # 数字部分のみ抽出
    url = f"https://db.netkeiba.com/race/2024{place_str}{round_str}{day_count_str}{race_str}/"
    print(f"Scraping URL: {url}")  # デバッグ用

    # HTTPリクエスト
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Referer": "https://db.netkeiba.com/"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch race data. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    payouts = []
    payout_table = soup.find("dl", class_="pay_block")
    if not payout_table:
        print("No payout information found.")  # デバッグ用
        return payouts

    # 払い戻し情報の取得
    tables = payout_table.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            if not th:
                continue
            bet_type = th.text.strip()  # 賭けの種類

            cols = row.find_all("td")
            if len(cols) >= 2:
                td_combination = cols[0].text.strip()
                td_amount = cols[1].text.strip()

                combinations = td_combination.split("\n")
                amounts = td_amount.split("\n")

                for combo, amt in zip(combinations, amounts):
                    payouts.append({
                        'bet_type': bet_type,
                        'combination': combo.strip(),
                        'amount': int(amt.replace(',', '').replace('¥', '')),
                    })

    print(f"Payouts extracted: {payouts}")  # デバッグ用
    return payouts

def calculate_payout(payouts, combinations, bet_type):
    """払い戻し金額を計算"""
    for payout in payouts:
        try:
            # 条件: bet_type と combinations の両方をチェック
            if payout.get('bet_type') == bet_type and any(
                sorted(combination) == sorted(
                    map(int, filter(str.isdigit, payout['combination'].replace('→', '-').replace(' ', '-').split('-')))
                )
                for combination in combinations
            ):
                print(f"Match found: name={bet_type}, combination={payout['combination']}")
                return payout['amount']
        except ValueError:
            print(f"Skipping invalid payout combination: {payout['combination']}")
            continue

    # 該当なしの場合は0を返す
    return 0

# アプリを実行
if __name__ == '__main__':
    print("Starting Flask server...")  # デバッグ用
    app.run(host='0.0.0.0', port=8000, debug=True)
