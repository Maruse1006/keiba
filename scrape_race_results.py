import pandas as pd
import requests

def scrape_race_results(race_id_list):
    race_results = {}
    for race_id in race_id_list:
        url = "https://db.netkeiba.com/race/" + race_id
        response = requests.get(url)
        response.encoding = "EUC-JP"  # netkeibaのページはEUC-JPエンコーディングを使用しています

        # HTMLテキストをDataFrameに変換
        race_results[race_id] = pd.read_html(response.text)[0]
    return race_results

# レースIDリストの例
race_id_list = ['201902010101', '201902010102', '201902010103']
test = scrape_race_results(race_id_list)

# データの表示
for race_id, df in test.items():
    print(f"Race ID: {race_id}")
    print(df)
