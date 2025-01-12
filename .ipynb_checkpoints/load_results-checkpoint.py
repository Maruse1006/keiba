import pandas as pd

# Pickleファイルを読み込む
results = pd.read_pickle('results.pickle')

# データの内容を確認
results.head()  # 最初の数行を表示
