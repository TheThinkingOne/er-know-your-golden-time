from app.clients.eternal_return_client import EternalReturnClient
from datetime import datetime;

import holidays


## 분석 로직 수행
class AnalysisService:

    def __init__(self):
        self.er_client = EternalReturnClient()

        # 대한민국 공휴일 정보
        self.kr_holidays = holidays.KR()

    ## 랭크게임 데이터 수집
    async def collect_rank_games(
        self,
        nickname: str,
        analysis_count: int | None = 100
    ) -> dict:
        """
        분석할 랭크 전적 횟수를 선택해주세요:
        - 50  : 최근 랭크 50게임
        - 100 : 최근 랭크 100게임
        - 150 : 최근 랭크 150게임
        """

        # 1. 닉네임으로 userId 조회
        user_id = await self.er_client.get_user_id(nickname)

        rank_games = []

        # pagination용 next 값(10게임 이후 다음 게임 id를 입력해야 10게임 넘게 가져올 수 있음)
        next_game_id = None

        # 가장 최근 랭크 게임의 seasonId를 현재 시즌으로 판단
        target_season_id = None


        while True:

            # 2. 경기 목록 한 페이지 조회
            response = await self.er_client.get_games(
                user_id=user_id,
                next_game_id=next_game_id
            )

            games = response.get("userGames", [])

            # 더 이상 경기 데이터가 없으면 종료
            if not games:
                break


            # 이전 시즌 랭크게임을 만났는지 체크
            older_season_found = False


            # 3. 한 페이지의 경기들을 하나씩 검사
            for game in games:

                matching_mode = game.get("matchingMode")

                # 랭크게임이 아니면 무시
                if matching_mode != 3:
                    continue


                season_id = game.get("seasonId")

                # 처음 발견한 랭크게임의 시즌을
                # 현재 분석 대상 시즌으로 지정
                if target_season_id is None:
                    target_season_id = season_id


                # 현재 시즌이 아닌 랭크게임을 발견하면
                # 이전 시즌까지 내려온 것으로 판단
                if season_id != target_season_id:
                    older_season_found = True
                    break


                # 현재 시즌 랭크게임 추가
                rank_games.append(game)


                # 사용자가 요청한 게임 수를 모두 모았으면 종료
                if (
                    analysis_count is not None
                    and len(rank_games) >= analysis_count
                ):
                    return self._build_result(
                        nickname=nickname,
                        user_id=user_id,
                        season_id=target_season_id,
                        requested_count=analysis_count,
                        games=rank_games
                    )


            # 이전 시즌까지 내려왔으면 pagination 종료
            if older_season_found:
                break


            # 4. 다음 페이지 커서 확인
            next_game_id = response.get("next")

            # next가 없다면 마지막 페이지
            if not next_game_id:
                break


        # 요청한 수량보다 실제 게임이 적거나
        # max 조회인 경우 여기까지 내려옴
        return self._build_result(
            nickname=nickname,
            user_id=user_id,
            season_id=target_season_id,
            requested_count=analysis_count,
            games=rank_games
        )


    def _build_result(
        self,
        nickname: str,
        user_id: str,
        season_id: int | None,
        requested_count: int | None,
        games: list
    ) -> dict:
        """
        수집한 경기 정보와 메타데이터를 응답 형태로 변환합니다.
        """

        return {
            "nickname": nickname,
            "userId": user_id,
            "seasonId": season_id,
            # "requestedGameCount": (
            #     requested_count
            #     if requested_count is not None
            #     else "max"
            # ),
            "requestedGameCount": requested_count,
            "analyzedGameCount": len(games),

            # 시간대별 RP 분석
            "timeSlotAnalysis": self._analyze_time_slots(games),
            "timeSlotDayTypeAnalysis": self._analyze_time_slots_by_day_type(games),

            # 아직 개발 중이라 원본 게임도 유지
            "games": games
        }


    def _parse_start_datetime(self, start_dtm: str) -> datetime:
        """
        Eternal Return API의 startDtm 문자열을
        Python datetime 객체로 변환합니다.

        예:
        2026-09-26T16:33:59.059+0900
        """

        return datetime.strptime(
            start_dtm,
            "%Y-%m-%dT%H:%M:%S.%f%z"
        )

    
    def _get_time_slot(self, game_datetime: datetime) -> str:
        """
        게임 시작 시간을 3시간 단위 구간으로 분류합니다.
        """

        hour = game_datetime.hour

        slot_start = (hour // 3) * 3
        slot_end = slot_start + 3

        return f"{slot_start:02d}-{slot_end:02d}"


    def _get_day_type(self, game_datetime: datetime) -> str:
        """
        게임 날짜를 평일 / 주말·공휴일로 분류하여 분석합니다.
        """

        game_date = game_datetime.date()

        # 토요일(5), 일요일(6)
        if game_datetime.weekday() >= 5:
            return "weekend_or_holiday"

        # 대한민국 공휴일
        if game_date in self.kr_holidays:
            return "weekend_or_holiday"

        return "weekday"


    ## 시간대별 RP 분석 함수
    def _analyze_time_slots(self, games: list) -> list:
        """
        랭크게임을 3시간 단위 시간대로 나누고
        RP 변화량, 평균 순위, 승률, top3 비율 등을 집계합니다.
        """

        time_slots = {
            "00-03": [],
            "03-06": [],
            "06-09": [],
            "09-12": [],
            "12-15": [],
            "15-18": [],
            "18-21": [],
            "21-24": []
        }

        # 1. 게임들을 시간대별로 분류
        for game in games:

            start_dtm = game.get("startDtm")

            if not start_dtm:
                continue

            game_datetime = self._parse_start_datetime(start_dtm)

            time_slot = self._get_time_slot(game_datetime)

            time_slots[time_slot].append(game)


        results = []

        # 2. 각 시간대별 통계 계산
        for time_slot, slot_games in time_slots.items():

            game_count = len(slot_games)

            # 플레이 기록이 없는 시간대
            if game_count == 0:
                results.append({
                    "timeSlot": time_slot,
                    "gameCount": 0,
                    "totalRpGain": 0,
                    "averageRpGain": None,
                    "averageRank": None,
                    "winRate": None,
                    "sampleStatus": "no_data"
                })

                continue


            total_rp_gain = sum(
                game.get("mmrGain", 0)
                for game in slot_games
            )

            average_rp_gain = total_rp_gain / game_count


            total_rank = sum(
                game.get("gameRank", 0)
                for game in slot_games
            )

            average_rank = total_rank / game_count


            win_count = sum(
                1
                for game in slot_games
                if game.get("victory") == 1
            )

            win_rate = (win_count / game_count) * 100


            results.append({
                "timeSlot": time_slot,
                "gameCount": game_count,

                "totalRpGain": total_rp_gain,

                "averageRpGain": round(
                    average_rp_gain,
                    2
                ),

                "averageRank": round(
                    average_rank,
                    2
                ),

                "winCount": win_count,

                "winRate": round(
                    win_rate,
                    2
                ),

                "sampleStatus": self._get_sample_status(
                    game_count
                )
            })


        return results


    ## 표본 보정 함수

    def _get_sample_status(self, game_count: int) -> str:
        """
        개별 시간대의 표본 상태를 반환합니다.
        """

        # 랭크게임 0판
        if game_count == 0:
            return "no_data"

        # 게임 3판 이하(포본 매우 부족)
        if game_count < 3:
            return "very_low"

        # 게임 5게임 미만(표본 부족)
        if game_count < 5:
            return "low"

        return "normal"


    ## 시간대별로 평일 / 주말, 공휴일 구분해서 RP 통계 계산
    def _analyze_time_slots_by_day_type(self, games: list) -> list:
        """
        시간대별로 평일 / 주말·공휴일을 구분해서
        RP 통계를 계산한다.
        """

        groups = {}

        for game in games:

            start_dtm = game.get("startDtm")

            if not start_dtm:
                continue

            game_datetime = self._parse_start_datetime(start_dtm)

            time_slot = self._get_time_slot(game_datetime)
            day_type = self._get_day_type(game_datetime)

            key = (time_slot, day_type)

            if key not in groups:
                groups[key] = []

            groups[key].append(game)

        results = []

        for (time_slot, day_type), group_games in groups.items():

            game_count = len(group_games)

            total_rp_gain = sum(
                game.get("mmrGain", 0)
                for game in group_games
            )

            average_rp_gain = total_rp_gain / game_count

            average_rank = sum(
                game.get("gameRank", 0)
                for game in group_games
            ) / game_count

            win_count = sum(
                1
                for game in group_games
                if game.get("victory") == 1
            )

            win_rate = (win_count / game_count) * 100

            results.append({
                "timeSlot": time_slot,
                "dayType": day_type,
                "gameCount": game_count,
                "totalRpGain": total_rp_gain,
                "averageRpGain": round(average_rp_gain, 2),
                "averageRank": round(average_rank, 2),
                "winCount": win_count,
                "winRate": round(win_rate, 2),
                "sampleStatus": self._get_sample_status(game_count)
            })

        return results


analysis_service = AnalysisService()