import type {
  Context,
  DiscoveryMode,
  Profile,
  RecommendationResponse,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_DISCOVERY_API_URL ?? "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export async function getProfiles(signal?: AbortSignal): Promise<Profile[]> {
  return parseResponse<Profile[]>(
    await fetch(`${API_BASE}/profiles`, { signal }),
  );
}

export async function getRecommendations(
  profileId: string,
  context: Context,
  discoveryMode: DiscoveryMode,
  signal?: AbortSignal,
): Promise<RecommendationResponse> {
  return parseResponse<RecommendationResponse>(
    await fetch(`${API_BASE}/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        profile_id: profileId,
        context,
        discovery_mode: discoveryMode,
        limit: 6,
      }),
      signal,
    }),
  );
}
