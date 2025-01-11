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
```
