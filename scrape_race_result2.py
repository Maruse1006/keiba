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

            # エンコーディングの指定
            response.encoding = "EUC-JP"

            # HTMLテーブルをDataFrameとして読み込む
            try:
                html_content = StringIO(response.text)
                df = pd.read_html(html_content)[0]

                # 空のテーブルをスキップ
                if df.empty:
                    print(f"Race ID {race_id} returned an empty table. Skipping...")
                    continue

                race_results[race_id] = df
                print(f"Race ID {race_id} scraped successfully.")
            except ValueError:
                print(f"No tables found for race ID {race_id}. Skipping...")
                continue
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for race ID {race_id}: {e}")
            continue
        except IndexError:
            print(f"IndexError for race ID {race_id}: Table not found on the page.")
            continue
        except AttributeError:
            print(f"AttributeError for race ID {race_id}: Invalid structure.")
            continue
        except Exception as e:
            print(f"Unexpected error for race ID {race_id}: {e}")
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

# 最初の50件のみを処理
limited_race_id_list = race_id_list[:50]

# スクレイピング実行
test3 = scrape_race_results(limited_race_id_list)

# データが空かをチェックして保存
if test3:  # 空でない場合にのみ処理
    try:
        # スクレイピング結果を確認
        print("\nVerifying scraped results...")
        for race_id, df in test3.items():
            print(f"Race ID: {race_id}")
            print(df.head())  # 最初の5行を確認
            break  # 最初のレースIDのみ確認

        # データフレームに結合
        results = pd.concat([test3[key] for key in test3], sort=False)

        # 最初の5件を抽出
        results_5 = results.head(5)

        # 保存前のデータ確認
        print("\nDataFrame Head (First 5 rows):")
        print(results_5)

        # Pickleとして保存
        results_5.to_pickle('results_5.pickle')
        print("Results saved to 'results_5.pickle'.")
    except Exception as e:
        print(f"Error during concatenation or saving: {e}")
else:
    print("No data was collected. Check the race IDs or the website availability.")

# Pickleファイルの読み込み確認
print("\nVerifying saved Pickle file...")
try:
    loaded_results_5 = pd.read_pickle('results_5.pickle')
    print("\nLoaded DataFrame Head (5 rows):")
    print(loaded_results_5)
except Exception as e:
    print(f"Error reading pickle file: {e}")
