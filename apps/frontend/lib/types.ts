export type Context = "weekday" | "weekend";
export type DiscoveryMode = "familiar" | "balanced" | "something_new";

export interface Profile {
  id: string;
  label: string;
  venue_entropy: number;
  category_entropy: number;
  weekend_delta: number;
  observation_count: number;
  confidence: number;
  familiar_categories: string[];
}

export interface Recommendation {
  id: string;
  label: string;
  city: string;
  category: string;
  historical_checkins: number;
  distinct_historical_visitors: number;
  aggregate_popularity_percentile: number;
  baseline_relevance: number;
  aggregate_novelty: number;
  provenance: string;
  final_score: number;
  category_familiarity: number;
  category_discovery: number;
  novelty_score: number;
  reason: string;
}

export interface RecommendationResponse {
  profile: Profile;
  context: Context;
  discovery_mode: DiscoveryMode;
  applied_discovery: number;
  uses_neutral_fallback: boolean;
  ranking_summary: string;
  recommendations: Recommendation[];
  disclaimer: string;
}
