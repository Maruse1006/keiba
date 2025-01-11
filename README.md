```
for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            if not th:
                continue
            bet_type = th.text.strip()

            cols = row.find_all("td")
            if len(cols) >= 2:
                td_combination = cols[0].text.strip()
                td_amount = cols[1].text.strip()

                combinations = td_combination.split("\n")
                amounts = td_amount.split("\n")

                for combo, amt in zip(combinations, amounts):
                    # 複勝の場合は文字列を分割
                    if bet_type == "複勝":
                        combo = [x.strip() for x in combo]  # 文字列を個別に分割

                    payouts.append({
                        'bet_type': bet_type,
                        'combination': combo.strip() if bet_type != "複勝" else combo,
                        'amount': int(amt.replace(',', '').replace('¥', '')),
                    })
```
combination': ['3', '1', '6', '2']←上記のコードだと複勝のデータが整形されていない。
```
Scraping URL: https://db.netkeiba.com/race/202408070607/
Payouts extracted: [{'bet_type': '単勝', 'combination': '3', 'amount': 340}, {'bet_type': '複勝', 'combination': ['3', '1', '6', '2'], 'amount': 160530320}, {'bet_type': '枠連', 'combination': '2 - 8', 'amount': 3640}, {'bet_type': '馬連', 'combination': '3 - 16', 'amount': 5420}, {'bet_type': 'ワイド', 'combination': '3 - 162 - 32 - 16', 'amount': 17005703690}, {'bet_type': '馬単', 'combination': '3 → 16', 'amount': 8440}, {'bet_type': '三連複', 'combination': '2 - 3 - 16', 'amount': 12780}, {'bet_type': '三連単', 'combination': '3 → 16 → 2', 'amount': 55290}]
Scraping completed. Payouts: [{'bet_type': '単勝', 'combination': '3', 'amount': 340}, {'bet_type': '複勝', 'combination': ['3', '1', '6', '2'], 'amount': 160530320}, {'bet_type': '枠連', 'combination': '2 - 8', 'amount': 3640}, {'bet_type': '馬連', 'combination': '3 - 16', 'amount': 5420}, {'bet_type': 'ワイド', 'combination': '3 - 162 - 32 - 16', 'amount': 17005703690}, {'bet_type': '馬単', 'combination': '3 → 16', 'amount': 8440}, {'bet_type': '三連複', 'combination': '2 - 3 - 16', 'amount': 12780}, {'bet_type': '三連単', 'combination': '3 → 16 → 2', 'amount': 55290}]
Error: name 'td_combination' is not defined
```

・以下に変更
```
from flask import Blueprint, request, jsonify
from models import db, Bets  # models.py で定義した db と Bets をインポート
import requests
from bs4 import BeautifulSoup

check_payout_blueprint = Blueprint('check_payout', __name__)

@check_payout_blueprint.route('/check_payout', methods=['POST'])
def check_payout():
    try:
        print("Received a POST request at /check_payout")
        data = request.json
        print(f"Received data: {data}")

        # 必須データの取得と検証
        user_id = data.get('userId')
        day_count = data.get('dayCount')
        place = data.get('place')
        race = data.get('race')
        round_number = data.get('round')
        combinations = data.get('combinations')
        bet_type = data.get('name')

        if not (user_id and day_count and place and race and round_number and combinations and bet_type):
            print("Invalid input data")
            return jsonify({'success': False, 'error': 'Invalid input data'}), 400

        print("Starting scraping process...")
        payouts = scrape_payouts(day_count, place, race, round_number, user_id)
        print(f"Scraping completed. Payouts: {payouts}")

        # 払い戻し金額の計算
        payout_amount = calculate_payout(payouts, combinations, bet_type)
        print(f"Calculated payout amount: {payout_amount}")

        # DBに払戻金を登録
        if payout_amount > 0:
            bet_entry = Bets(
                user_id=user_id,
                name=bet_type,
                amount=payout_amount,
                comment="払い戻し金の記録",
                date_info=day_count,
                location=place,
                race_number=race,
                round=round_number,
            )
            db.session.add(bet_entry)
            db.session.commit()
            print(f"Bet successfully recorded for user_id={user_id}")

        return jsonify({'success': True, 'payout': payout_amount})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def scrape_payouts(day_count, place, race, round, user_id):
    """スクレイピングして払い戻しデータを取得"""
    day_count_str = f"{int(''.join(filter(str.isdigit, day_count))):02}"
    place_str = f"{int(place):02}"
    race_str = f"{int(race):02}"
    round_str = f"{int(''.join(filter(str.isdigit, round))):02}"

    url = f"https://db.netkeiba.com/race/2024{place_str}{round_str}{day_count_str}{race_str}/"
    print(f"Scraping URL: {url}")

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
        print("No payout information found.")
        return payouts

    tables = payout_table.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            if not th:
                continue
            bet_type = th.text.strip()

            cols = row.find_all("td")
            if len(cols) >= 2:
                td_combination = cols[0].text.strip()
                td_amount = cols[1].text.strip()

                # 複勝の場合の処理
                if bet_type == "複勝":
                    combination_list = cols[0].decode_contents().replace("<br/>", "\n").split("\n")
                    amount_list = cols[1].decode_contents().replace("<br/>", "\n").split("\n")
                    for combo, amt in zip(combination_list, amount_list):
                        payouts.append({
                            'bet_type': bet_type,
                            'combination': combo.strip(), 
                            'amount': int(amt.replace(',', '').replace('¥', ''))
                        })
                else:
                    # 他のベットタイプ（例: 単勝, 馬連など）
                    payouts.append({
                        'bet_type': bet_type,
                        'combination': td_combination.strip(),
                        'amount': int(td_amount.replace(',', '').replace('¥', ''))
                    })

    print(f"Payouts extracted: {payouts}")
    return payouts


def calculate_payout(payouts, combinations, bet_type):
    """払い戻し金額を計算"""
    for payout in payouts:
        try:
            # "単勝"の特別な処理
            if bet_type == "単勝":
                if any(comb == payout['combination'] for comb in combinations):
                    print(f"Match found: name={bet_type}, combination={payout['combination']}")
                    return payout['amount']

            # "複勝"の特別な処理
            if bet_type == "複勝":
                for combination in combinations:
                    if combination in payout['combination']:  # 部分一致を確認
                        print(f"Match found: name={bet_type}, combination={payout['combination']}")
                        return payout['amount']

            # 他のベットタイプの処理
            payout_combination = sorted(
                map(str.strip, payout['combination'].replace('→', '-').replace(' ', '').split('-'))
            )
            for combination in combinations:
                if sorted(map(str, combination)) == payout_combination:
                    print(f"Match found: name={bet_type}, combination={payout['combination']}")
                    return payout['amount']
        except ValueError:
            print(f"Skipping invalid payout combination: {payout['combination']}")
            continue

    return 0
```
