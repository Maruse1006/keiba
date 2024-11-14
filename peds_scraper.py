import requests
import pandas as pd
from bs4 import BeautifulSoup

class Peds:
    @staticmethod
    def scrape(horse_id_list):
        headers = {"User-Agent": "Mozilla/5.0"}
        peds_dict = {}

        for horse_id in horse_id_list:
            try:
                url = "https://db.netkeiba.com/horse/ped/" + horse_id
                response = requests.get(url, headers=headers)
                
                # BeautifulSoupでHTMLをパースしてエンコードを指定
                soup = BeautifulSoup(response.content, 'html.parser')
                html = soup.prettify()

                # pandasでデータを読み込み
                df = pd.read_html(html)[0]

                # 血統データの整形
                generations = {}
                for i in range(5):
                    if i < len(df.columns):
                        generations[f"generation_{i+1}"] = df[i]
                    df = df.drop_duplicates()

                # 各世代のデータを結合し、行方向に変換
                ped = pd.concat([generations[f"generation_{i+1}"] for i in range(5)], axis=1)
                ped.columns = [f"generation_{i+1}" for i in range(len(ped.columns))]

                peds_dict[horse_id] = ped.reset_index(drop=True)
            except Exception as e:
                print(f"{horse_id}でエラーが発生しました: {e}")
                continue

        # 全ての血統データをDataFrameに結合
        if peds_dict:
            peds_df = pd.concat([peds_dict[key] for key in peds_dict], keys=peds_dict.keys())
            print(peds_df)
        else:
            print("有効なデータがありませんでした")
            return pd.DataFrame()

        return peds_df

# JSON形式で保存
if __name__ == "__main__":
    horse_id_list = ["2017101010"]  # 例として1つのID
    peds_data = Peds.scrape(horse_id_list)
    
    # データが存在する場合のみJSONに保存
    if not peds_data.empty:
        peds_data.to_json("pedigree_data.json", orient="records", force_ascii=False)  # 日本語対応
        print("JSONファイルとして保存しました: pedigree_data.json")
    else:
        print("データがありませんでした。")

