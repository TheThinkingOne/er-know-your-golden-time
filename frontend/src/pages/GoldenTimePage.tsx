import { useState } from "react";

import { getRankAnalysis } from "../../api/analysisApi";
import type { RankAnalysisResponse } from "../types/analysis";

function GoldenTimePage() {
  const [nickname, setNickname] = useState("");
  const [count, setCount] = useState<50 | 100 | 150>(100);

  const [analysis, setAnalysis] = useState<RankAnalysisResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!nickname.trim()) {
      setError("닉네임을 입력해주세요.");
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const result = await getRankAnalysis(nickname.trim(), count);

      setAnalysis(result);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("알 수 없는 오류가 발생했습니다.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>ER Know Your Golden Time</h1>

      <p>
        내 랭크게임 데이터를 분석해서 가장 효율적인 플레이 시간대를 찾아봅니다.
      </p>

      <div>
        <input
          type="text"
          placeholder="이터널 리턴 닉네임"
          value={nickname}
          onChange={(event) => setNickname(event.target.value)}
        />

        <select
          value={count}
          onChange={(event) =>
            setCount(Number(event.target.value) as 50 | 100 | 150)
          }
        >
          <option value={50}>최근 50판</option>
          <option value={100}>최근 100판</option>
          <option value={150}>최근 150판</option>
        </select>

        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? "분석 중..." : "분석하기"}
        </button>
      </div>

      {error && <p>{error}</p>}

      {analysis && (
        <div>
          <h2>{analysis.nickname}님의 분석 결과</h2>

          <p>시즌: {analysis.seasonId}</p>

          <p>분석 게임: {analysis.analyzedGameCount}판</p>

          <h3>시간대별 분석</h3>

          {analysis.timeSlotAnalysis.map((slot) => (
            <div key={slot.timeSlot}>
              <strong>{slot.timeSlot}</strong>

              <span> {slot.gameCount}판</span>

              <span> 평균 RP: {slot.averageRpGain ?? "-"}</span>

              <span>
                {" "}
                승률: {slot.winRate === null ? "-" : `${slot.winRate}%`}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default GoldenTimePage;
