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
