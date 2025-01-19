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

        # 払い戻し金額と収支の計算
        bet_amount_per_combination = 100  # 1組み合わせあたりの掛け金
        payout_amount, total_bet_amount, profit_or_loss = calculate_payout_with_profit(payouts, combinations, bet_type, bet_amount_per_combination)
        print(f"Calculated payout amount: {payout_amount}")
        print(f"Total bet amount: {total_bet_amount}")
        print(f"Profit or loss: {profit_or_loss}")

        # DBに払戻金と収支を登録（収支がマイナスでも登録する）
        bet_entry = Bets(
            user_id=user_id,
            name=bet_type,
            amount=payout_amount,
            comment=f"収支計算: {profit_or_loss}円",
            date_info=day_count,
            location=place,
            race_number=race,
            round=round_number,
        )
        db.session.add(bet_entry)
        db.session.commit()
        print(f"Bet successfully recorded for user_id={user_id}, profit_or_loss={profit_or_loss}")

        return jsonify({
            'success': True,
            'payout': payout_amount,
            'total_bet_amount': total_bet_amount,
            'profit_or_loss': profit_or_loss
        })
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

                if bet_type == "ワイド":
                    combination_list = cols[0].decode_contents().replace("<br/>", "\n").split("\n")
                    amount_list = cols[1].decode_contents().replace("<br/>", "\n").split("\n")
                    for combo, amt in zip(combination_list, amount_list):
                        payouts.append({
                            'bet_type': bet_type,
                            'combination': combo.strip(),
                            'amount': int(amt.replace(',', '').replace('¥', ''))
                        })

    print(f"Payouts extracted: {payouts}")
    return payouts


def calculate_payout_with_profit(payouts, combinations, bet_type, bet_amount_per_combination):
    """払い戻し金額と収支を計算"""
    filtered_payouts = [payout for payout in payouts if payout.get('bet_type') == bet_type]
    print(f"[DEBUG] {bet_type} に関連するデータのみを処理: {filtered_payouts}")

    total_payout = 0
    total_bet_amount = len(combinations) * bet_amount_per_combination  # 総掛け金

    for idx, combination in enumerate(combinations, start=1):  # 外側ループの回数を記録
        # 組み合わせをソートして整形
        sorted_combination = sorted(map(str, combination))  # ソートされた組み合わせ
        expected_combination = " - ".join(sorted_combination)  # '3 - 16' 形式に整形
        print(f"[DEBUG] Loop {idx}: Expected combination for {bet_type}: {expected_combination}")
        
        for payout_idx, payout in enumerate(filtered_payouts, start=1):  # 内側ループの回数を記録
            # 払い戻しデータもソートして比較
            payout_sorted_combination = " - ".join(sorted(payout['combination'].split(" - ")))
            print(f"[DEBUG] Loop {idx}-{payout_idx}: Payout combination for {bet_type}: {payout_sorted_combination}")

            if payout_sorted_combination == expected_combination:
                print(f"[DEBUG] Match found in Loop {idx}-{payout_idx}: name={bet_type}, combination={payout['combination']}, amount={payout['amount']}")
                total_payout += payout['amount']  # 合計に加算

    # 収支計算：払い戻し金額 - 総掛け金
    profit_or_loss = total_payout - total_bet_amount

    return total_payout, total_bet_amount, profit_or_loss
