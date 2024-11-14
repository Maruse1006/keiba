import pandas as pd
import time
from tqdm.notebook import tqdm
import requests
from io import StringIO

def scrape_race_results(race_id_list, pre_race_results={}):
    race_results = pre_race_results.copy()
    headers = {"User-Agent": "Mozilla/5.0"}  # User-Agentを追加
    
    for race_id in tqdm(race_id_list):
        if race_id in race_results.keys():
            continue
        time.sleep(1)  # アクセス間隔
        try:
            url = "https://db.netkeiba.com/race/" + race_id
            print(f"Accessing URL: {url}")  # URLの確認
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # HTTPエラーがあれば例外を発生

            # StringIOでHTMLコンテンツをラップしてから渡す
            html_content = StringIO(response.text)
            race_results[race_id] = pd.read_html(html_content)[0]
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for race_id {race_id}: {e}")
            continue
        except IndexError:
            print(f"IndexError for race_id {race_id}: Table not found on the page.")
            continue
        except AttributeError:
            print(f"AttributeError for race_id {race_id}: Invalid structure.")
            continue
        except Exception as e:
            print(f"Unexpected error for race_id {race_id}: {e}")
            break
    return race_results

# レースIDのリストを作成
race_id_list = []
for place in range(1, 11):  # 1から10
    for kai in range(1, 6):  # 1から5
        for day in range(1, 13):  # 1から12
            for r in range(1, 13):  # 1から12
                race_id = f"2019{str(place).zfill(2)}{str(kai).zfill(2)}{str(day).zfill(2)}{str(r).zfill(2)}"
                race_id_list.append(race_id)

# スクレイピング実行
test3 = scrape_race_results(race_id_list)

# データが空かをチェックして保存
if test3:  # 空でない場合にのみ処理
    results = pd.concat([test3[key] for key in test3], sort=False)
    results.to_pickle('results.pickle')
else:
    print("No data was collected. Check the race IDs or the website availability.")
