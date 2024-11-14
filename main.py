from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()

# CORSの設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  # React Nativeアプリのオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

@app.get("/api")
async def get_pedigree_data():
    try:
        # JSONファイルを読み込む
        data = pd.read_json("pedigree_data.json", orient="records")
        return JSONResponse(content=data.to_dict(orient="records"))
    except Exception as e:
        return {"error": "データの取得に失敗しました"}
