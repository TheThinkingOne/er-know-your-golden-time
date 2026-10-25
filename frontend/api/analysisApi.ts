// fastAPI 로 전적 데이터 호출 담당

import type { RankAnalysisResponse } from "../src/types/analysis";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function getRankAnalysis(
  nickname: string,
  count: 50 | 100 | 150,
): Promise<RankAnalysisResponse> {
  const params = new URLSearchParams({
    nickname,
    count: String(count),
  });

  const response = await fetch(
    `${API_BASE_URL}/analysis/rank?${params.toString()}`,
  );

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);

    throw new Error(errorBody?.detail ?? "전적 분석 요청에 실패했습니다.");
  }

  return response.json();
}
