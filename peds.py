import pickle

def save_horse_names_and_ids(pickle_file, output_file):
    """Pickleファイルから馬名とhorse_idを抽出して保存"""
    try:
        # race_results.pkl ファイルをロード
        with open(pickle_file, 'rb') as f:
            race_results = pickle.load(f)
        
        # 馬名とhorse_idを抽出
        horse_data = {}
        for race_id, df in race_results.items():
            for _, row in df.iterrows():
                horse_data[row['馬名']] = row['horse_id']  # 馬名をキーに、horse_idを値として格納

        # 新しいpickleファイルに保存
        with open(output_file, 'wb') as f:
            pickle.dump(horse_data, f)
        print(f"馬名とhorse_idのペアを {output_file} に保存しました。")
    
    except Exception as e:
        print(f"Error processing pickle file: {e}")

if __name__ == "__main__":
    # 入力と出力のファイル名
    input_pickle = "race_results.pkl"
    output_pickle = "horse_names_and_ids.pkl"
    
    # 馬名とhorse_idを保存
    save_horse_names_and_ids(input_pickle, output_pickle)
