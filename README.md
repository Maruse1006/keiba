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
実際のデータ
```
<table cellpadding="0" cellspacing="1" class="pay_table_01" summary="払い戻し">
  <tbody>
    <tr>
      <th class="tan">単勝</th>
      <td>3</td>
      <td class="txt_r">340</td>
      <td class="txt_r">1</td>
    </tr>
    <tr>
      <th class="fuku" align="center">複勝</th>
      <td>
        3<br>
        16<br>
        2
      </td>
      <td class="txt_r">
        160<br>
        530<br>
        320
      </td>
      <td class="txt_r">
        1<br>
        9<br>
        7
      </td>
    </tr>
    <tr>
      <th class="waku" align="center">枠連</th>
      <td>2 - 8</td>
      <td class="txt_r">3,640</td>
      <td class="txt_r">18</td>
    </tr>
    <tr>
      <th class="uren" align="center">馬連</th>
      <td>3 - 16</td>
      <td class="txt_r">5,420</td>
      <td class="txt_r">23</td>
    </tr>
  </tbody>
</table>

```

```
for table in tables:  # HTML内のすべてのテーブルを処理
    rows = table.find_all("tr")  # テーブル内の行を取得
    for row in rows:  # 行ごとに処理

```
・tables: BeautifulSoupで抽出したHTMLの払い戻しテーブル。<br>
・find_all("tr"): 各テーブル内の<tr>（行）を取得。<br>
・各行で必要なデータ（ベットタイプ、組み合わせ、金額）を取得して処理する。

