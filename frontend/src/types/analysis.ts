export type SampleStatus = "no_data" | "very_low" | "low" | "normal";

export interface TimeSlotAnalysis {
  timeSlot: string;
  gameCount: number;
  totalRpGain: number;
  averageRpGain: number | null;
  averageRank: number | null;
  winCount?: number;
  winRate: number | null;
  sampleStatus: SampleStatus;
}

// 공휴일, 주말, 평일 여부 판단
export interface TimeSlotDayTypeAnalysis {
  timeSlot: string;
  dayType: "weekday" | "weekend_or_holiday";
  gameCount: number;
  totalRpGain: number;
  averageRpGain: number;
  averageRank: number;
  winCount: number;
  winRate: number;
  sampleStatus: SampleStatus;
}

// 분석된 랭크 결과 response
export interface RankAnalysisResponse {
  nickname: string;
  userId: string;
  seasonId: number;
  requestedGameCount: number;
  analyzedGameCount: number;

  timeSlotAnalysis: TimeSlotAnalysis[];
  timeSlotDayTypeAnalysis: TimeSlotDayTypeAnalysis[];

  games: unknown[];
}
