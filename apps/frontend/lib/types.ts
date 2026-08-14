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
  name: string;
  category: string;
  description: string;
  final_score: number;
  baseline_relevance: number;
  venue_novelty: number;
  category_novelty: number;
  novelty_score: number;
  distance_penalty: number;
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
