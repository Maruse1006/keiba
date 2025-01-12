from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Flaskアプリ全体にCORSを適用

# Pickleファイルから馬名に対応する血統データを取得
def load_pedigree_by_name(pickle_file, horse_name):
    try:
        with open(pickle_file, 'rb') as f:
            race_results = pickle.load(f)

        for race_id, df in race_results.items():
            matching_horse = df[df['馬名'] == horse_name]
            if not matching_horse.empty:
                horse_id = matching_horse["horse_id"].iloc[0]
                # 血統データをピクルファイルから取得する（仮定）
                with open("pedigree_data.pickle", "rb") as ped_file:
                    pedigree_data = pickle.load(ped_file)
                return pedigree_data.get(horse_id, None)
        return None
    except Exception as e:
        print(f"Error loading pedigree data: {e}")
        return None

@app.route('/get_pedigree', methods=['POST'])
def get_pedigree():
    data = request.json
    horse_name = data.get("horse_name")

    if not horse_name:
        return jsonify({"error": "馬名が指定されていません"}), 400

    # Pickleファイルをロードして血統データを取得
    pickle_filename = "race_results.pkl"
    pedigree_data = load_pedigree_by_name(pickle_filename, horse_name)

    if pedigree_data:
        return jsonify(pedigree_data)
    else:
        return jsonify({"error": f"馬名 {horse_name} に該当するデータが見つかりませんでした"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
