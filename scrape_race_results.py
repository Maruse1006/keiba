import pandas as pd
import requests
import time
from io import StringIO

# 京都開催レースのレースIDリストを生成
def generate_kyoto_race_ids(year="2019"):
    race_id_list = []
    place = 5  # 京都競馬場のplace番号（一般的には5ですが、確認を推奨）

    for kai in range(1, 7):  # 開催回数
        for day in range(1, 13):  # 日数
            for r in range(1, 13):  # レース番号
                race_id = year + str(place).zfill(2) + str(kai).zfill(2) + str(day).zfill(2) + str(r).zfill(2)
                race_id_list.append(race_id)
                if len(race_id_list) >= 20:  # 20件分だけ生成したら終了
                    return race_id_list
    return race_id_list

# レース結果をスクレイピング
def scrape_race_results(race_id_list):
    race_results = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    for race_id in race_id_list:
        url = "https://db.netkeiba.com/race/" + race_id
        response = requests.get(url, headers=headers)
        response.encoding = "EUC-JP"  # netkeibaのページはEUC-JPエンコーディングを使用

        if response.status_code != 200:
            print(f"Failed to retrieve data for race ID {race_id}")
            continue

        try:
            # StringIOを使用してHTMLをファイルのように扱う
            tables = pd.read_html(StringIO(response.text))
            if tables:
                race_results[race_id] = tables[0]
                print(f"Data retrieved for race ID {race_id}")
            else:
                print(f"No tables found for race ID {race_id}")
        except Exception as e:
            print(f"Error parsing HTML for race ID {race_id}: {e}")
        
        time.sleep(1)  # リクエスト間の待機時間

    return race_results

# 京都競馬場（2019年）レースIDリストの生成（最初の20件のみ）
race_id_list = generate_kyoto_race_ids("2019")

# データのスクレイピング
results = scrape_race_results(race_id_list)

# データの表示
for race_id, df in results.items():
    print(f"Race ID: {race_id}")
    print(df)
