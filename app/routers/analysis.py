from fastapi import APIRouter, HTTPException, Query

from app.services.analysis_service import analysis_service

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

@router.get("/rank")
async def analyze_rank_games(
    nickname: str = Query(..., description="이터널 리턴 인게임 닉네임 입력"),
    count: str = Query(
        "100",
        description="분석할 랭크게임 수: 50, 100, 150 게임 내"
    )
):
    """
    현재 시즌 내의 랭크게임 데이터들을 수집합니다.

    분석할 랭크 판수:
    - 50
    - 100
    - 150
    """

    # 사용자가 입력한 count 값을
    # AnalysisService가 이해하는 값으로 변환
    if count == "50":
        analysis_count = 50

    elif count == "100":
        analysis_count = 100

    elif count == "150":
        analysis_count = 150

    else:
        raise HTTPException(
            status_code=400,
            detail="count는 50, 100, 150 중 하나여야 합니다."
        )

    try:
        result = await analysis_service.collect_rank_games(
            nickname=nickname,
            analysis_count=analysis_count
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"랭크 전적 조회 중 오류가 발생했습니다: {str(e)}"
        )