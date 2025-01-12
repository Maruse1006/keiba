import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from io import StringIO
import pickle

def scrape_race_results(race_id_list):
    race_results = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    for race_id in race_id_list:
        print(f"Processing race ID: {race_id}")
        try:
            url = f"https://db.netkeiba.com/race/{race_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to fetch page for race ID {race_id} (HTTP {response.status_code}), skipping...")
                continue
            
            response.encoding = response.apparent_encoding  # 自動エンコーディング検出
            soup = BeautifulSoup(response.text, "html.parser")

            # レース結果テーブルをDataFrameに変換
            try:
                html_string = StringIO(response.text)
                df = pd.read_html(html_string)[0]
            except ValueError:
                print(f"No tables found for race ID {race_id}, skipping...")
                continue

            # 馬IDと騎手IDの取得
            horse_id_list = [re.findall(r"\d+", a["href"])[0] for a in soup.find("table", attrs={"summary": "レース結果"}).find_all("a", attrs={"href": re.compile("^/horse")})]
            jockey_id_list = [re.findall(r"\d+", a["href"])[0] for a in soup.find("table", attrs={"summary": "レース結果"}).find_all("a", attrs={"href": re.compile("^/jockey")})]

            # DataFrameに馬IDと騎手IDを追加
            df["horse_id"] = horse_id_list
            df["jockey_id"] = jockey_id_list

            race_results[race_id] = df
            print(f"Successfully scraped race ID {race_id}.")
        
        except Exception as e:
            print(f"Unexpected error while processing race ID {race_id}: {e}")
    
    if not race_results:
        print("No data was scraped. Please check the race IDs or the website availability.")
    else:
        print(f"Scraped data for {len(race_results)} races.")
    
    return race_results

def save_to_pickle(data, filename):
    """Pickle形式でデータを保存する"""
    with open(filename, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data saved to {filename}.")

def load_from_pickle(filename):
    """Pickle形式のデータを読み込む"""
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    print(f"Data loaded from {filename}.")
    return data

if __name__ == "__main__":
    race_id_list = ["202405030211", "202305030211"]
    results = scrape_race_results(race_id_list)
    
    # Pickleとして保存
    pickle_filename = "race_results.pkl"
    save_to_pickle(results, pickle_filename)
    
    # Pickleから読み込み
    loaded_results = load_from_pickle(pickle_filename)

    # horse_id と馬名の出力
    for race_id, df in loaded_results.items():
        print(f"\nRace ID: {race_id}")
        print("Horse ID and Names:")
        for horse_id, horse_name in zip(df["horse_id"], df["馬名"]):  # 馬名は列名にある
            print(f"  Horse ID: {horse_id}, Horse Name: {horse_name}")
