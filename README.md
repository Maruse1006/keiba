必要なライブラリー

# データ処理
pip install pandas numpy

# プログレスバー表示
pip install tqdm

# 機械学習と評価指標
pip install scikit-learn lightgbm optuna

# ウェブスクレイピング
pip install requests beautifulsoup4

# グラフ描画
pip install matplotlib

requests.get(url) の役割
**requests.get(url)**は、指定したURL（url）にアクセスし、そのURLから情報を取得します。
HTTP GETリクエスト：getメソッドは、ウェブページから情報を取得する際に一般的に使われるHTTPリクエストの一種で、「そのURLの内容をください」というリクエストをサーバーに送信します。
responseオブジェクト：リクエストが成功すると、サーバーからの応答がresponseというオブジェクトに格納されます。このオブジェクトには、サーバーから返されたデータやHTTPステータスコード、エンコーディングなどの情報が含まれています。
