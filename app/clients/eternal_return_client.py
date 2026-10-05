import httpx

from app.core.config import settings


class EternalReturnClient:

    def __init__(self):
        self.base_url = settings.ER_API_BASE_URL

        ## 환경세팅에 저장해놓은 이터널리턴 api key 값 불러오기
        self.headers = {
            "x-api-key": settings.ER_API_KEY
        }

    async def get_user_id(self, nickname: str) -> str:
        """
        분석을 진행할 인게임 닉네임을 입력해주세요.
        """

        ## 아래부턴 이리 공식 api의 엔드포인트 구조
        url = f"{self.base_url}/v1/user/nickname"

        params = {
            "query": nickname
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                headers=self.headers,
                params=params
            )

        response.raise_for_status()

        data = response.json()

        user = data.get("user")

        if not user:
            raise ValueError("사용자 정보를 찾을 수 없습니다.")

        user_id = user.get("userId")

        if not user_id:
            raise ValueError("UID를 찾을 수 없거나 응답이 없습니다.")

        return user_id

    async def get_games(
        self,
        user_id: str,
        next_game_id: int | None = None
    ) -> dict:
        """
        조회된 경기 목록 한 페이지
        """

        url = f"{self.base_url}/v1/user/games/uid/{user_id}"

        params = {}

        if next_game_id is not None:
            params["next"] = next_game_id

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                headers=self.headers,
                params=params
            )

        response.raise_for_status()

        return response.json()