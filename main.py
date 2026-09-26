from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("ER_API_KEY")

API_KEY = os.getenv("ER_API_KEY")


@app.get("/")
def root():
    return {"message": "ER Know Your Golden Time"}


@app.get("/player/games/by-nickname")
async def get_games_by_nickname(nickname: str):

    headers = {
        "x-api-key": API_KEY
    }

    async with httpx.AsyncClient(timeout=20.0) as client:

        # 1. 닉네임 → userId 조회
        user_response = await client.get(
            "https://open-api.bser.io/v1/user/nickname",
            headers=headers,
            params={"query": nickname}
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"UID 조회 실패: {user_response.text}"
            )

        user_data = user_response.json()

        if "user" not in user_data or "userId" not in user_data["user"]:
            raise HTTPException(
                status_code=502,
                detail=f"userId가 응답에 없습니다: {user_data}"
            )

        user_id = user_data["user"]["userId"]

        # 2. userId → 경기 목록 조회
        games_response = await client.get(
            f"https://open-api.bser.io/v1/user/games/uid/{user_id}",
            headers=headers
        )

        if games_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"경기 목록 조회 실패: {games_response.text}"
            )

        return games_response.json()