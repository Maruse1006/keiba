import pickle

pickle_filename = "results_5.pickle"

# ファイル内容を確認
with open(pickle_filename, 'rb') as f:
    data = pickle.load(f)

print(data)  # データ構造を確認
