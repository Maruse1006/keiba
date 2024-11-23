import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from tqdm.notebook import tqdm
import re
from imblearn.under_sampling import RandomUnderSampler
from sklearn.ensemble import RandomForestClassifier

# スクレイピング関数
def scrape_race_info(race_id_list):
    race_infos = {}
    for race_id in tqdm(race_id_list):
        print(f"Processing race_id: {race_id}")
        time.sleep(1)
        try:
            url = "https://db.netkeiba.com/race/" + str(race_id)
            html = requests.get(url)
            html.encoding = "EUC-JP"
            soup = BeautifulSoup(html.text, "html.parser")

            # データ抽出
            data_intro = soup.find("div", attrs={"class": "data_intro"})
            texts = (
                data_intro.find_all("p")[0].text + data_intro.find_all("p")[1].text
                if data_intro and len(data_intro.find_all("p")) > 1 else ""
            )
            info = re.findall(r"\w+", texts)
            info_dict = {k: v for k, v in [
                ("race_type", text) for text in info if text in ["芝", "ダート"]] +
                [("course_len", int(re.findall(r"\d+", text)[0])) for text in info if "m" in text] +
                [("ground_state", text) for text in info if text in ["良", "稍重", "重", "不良"]] +
                [("weather", text) for text in info if text in ["曇", "晴", "雨", "小雨", "小雪", "雪"]] +
                [("date", text) for text in info if "年" in text]
            }
            race_infos[race_id] = info_dict
        except Exception as e:
            print(f"Error processing race_id {race_id}: {e}")
            continue
    return race_infos

# Pickleファイルの確認
if os.path.exists('results_5.pickle'):
    results = pd.read_pickle('results_5.pickle')
else:
    raise FileNotFoundError("The file 'results_5.pickle' does not exist.")

# レースID一覧を取得
if isinstance(results, pd.DataFrame):
    race_id_list = results.index.unique()
elif isinstance(results, dict):
    race_id_list = list(results.keys())
else:
    raise TypeError("Unsupported type for 'results'. Must be DataFrame or dict.")

# スクレイピング実行
race_infos = scrape_race_info(race_id_list)

# DataFrameに変換
if race_infos:
    race_infos = pd.DataFrame(race_infos).T
else:
    raise ValueError("No race information was scraped. Check the race IDs or website availability.")

# データの結合
results_addinfo = results.merge(race_infos, left_index=True, right_index=True, how="inner")

# カラム名のスペースを削除
results_addinfo.columns = results_addinfo.columns.str.replace(" ", "")

# 修正後のカラムを確認
print("\nCleaned Columns in Results Addinfo:", results_addinfo.columns)

# データ前処理関数
def preprocessing(results):
    df = results.copy()

    # 必須列の確認
    required_columns = ["着順", "性齢", "馬体重", "単勝"]
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"'{col}' カラムが存在しません。データを確認してください。")

    # データ変換
    df = df[~df["着順"].astype(str).str.contains(r"\D")]
    df["着順"] = df["着順"].astype(int)
    df["性"] = df["性齢"].str[0]
    df["年齢"] = df["性齢"].str[1:].astype(int)
    df["体重"] = df["馬体重"].str.split("(", expand=True)[0].astype(int)
    df["体重変化"] = df["馬体重"].str.split("(", expand=True)[1].str[:-1].astype(int)
    df["単勝"] = df["単勝"].astype(float)
    df["date"] = pd.to_datetime(df["date"], format="%Y年%m月%d日")

    df.drop(["タイム", "着差", "調教師", "性齢", "馬体重"], axis=1, inplace=True)
    return df

# データ前処理
try:
    results_p = preprocessing(results_addinfo)
except KeyError as e:
    print(f"Preprocessing Error: {e}")
    print("\nColumns in Results Addinfo (after cleaning):", results_addinfo.columns)
    print("\nHead of Results Addinfo (after cleaning):")
    print(results_addinfo.head())
    exit()

# データ分割
def split_data(df, test_size):
    sorted_ids = df.sort_values("date").index.unique()
    train_ids = sorted_ids[:round(len(sorted_ids) * (1 - test_size))]
    test_ids = sorted_ids[round(len(sorted_ids) * (1 - test_size)):]
    return df.loc[train_ids], df.loc[test_ids]

results_p.drop("馬名", axis=1, inplace=True)
results_d = pd.get_dummies(results_p)
results_d["rank"] = results_d["着順"].apply(lambda x: x if x < 4 else 4)
train, test = split_data(results_d, test_size=0.3)

X_train, y_train = train.drop(["着順", "date", "rank"], axis=1), train["rank"]
X_test, y_test = test.drop(["着順", "date", "rank"], axis=1), test["rank"]

# アンダーサンプリング
rank_counts = train["rank"].value_counts()
rus = RandomUnderSampler(sampling_strategy=dict(rank_counts), random_state=71)
X_train_rus, y_train_rus = rus.fit_resample(X_train, y_train)

# ランダムフォレスト予測
clf = RandomForestClassifier(random_state=0)
clf.fit(X_train_rus, y_train_rus)

# 精度を出力
print(f"Train Accuracy: {clf.score(X_train, y_train):.4f}")
print(f"Test Accuracy: {clf.score(X_test, y_test):.4f}")
