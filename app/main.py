from fastapi import FastAPI

from app.routers.analysis import router as analysis_router


app = FastAPI(
    title="ER Know Your Golden Time API",
    description="이터널 리턴 랭크 전적 시간대 분석 API",
    version="0.1.0"
)


app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "message": "ER Know Your Golden Time"
    }