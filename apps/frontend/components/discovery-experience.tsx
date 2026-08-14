"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";

import { getProfiles, getRecommendations } from "@/lib/api";
import type {
  Context,
  DiscoveryMode,
  Profile,
  RecommendationResponse,
} from "@/lib/types";

const contextOptions: Array<{ value: Context; label: string }> = [
  { value: "weekday", label: "Weekday" },
  { value: "weekend", label: "Weekend" },
];

const discoveryOptions: Array<{
  value: DiscoveryMode;
  label: string;
  hint: string;
}> = [
  { value: "familiar", label: "Keep it familiar", hint: "Relevance leads" },
  { value: "balanced", label: "Balanced", hint: "A measured mix" },
  {
    value: "something_new",
    label: "Show me something new",
    hint: "Novelty has more weight",
  },
];

export default function DiscoveryExperience() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState("mixed");
  const [context, setContext] = useState<Context>("weekday");
  const [discoveryMode, setDiscoveryMode] =
    useState<DiscoveryMode>("balanced");
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [isLoadingProfiles, setIsLoadingProfiles] = useState(true);
  const [isRanking, setIsRanking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryNonce, setRetryNonce] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    getProfiles(controller.signal)
      .then((nextProfiles) => {
        setProfiles(nextProfiles);
        if (!nextProfiles.some((profile) => profile.id === "mixed")) {
          setProfileId(nextProfiles[0]?.id ?? "");
        }
      })
      .catch((requestError: unknown) => {
        if ((requestError as Error).name !== "AbortError") {
          setError("We couldn’t load the synthetic profiles from the local API.");
        }
      })
      .finally(() => setIsLoadingProfiles(false));
    return () => controller.abort();
  }, []);

  const requestRanking = useCallback(
    (signal?: AbortSignal) => {
      if (!profileId) return Promise.resolve();
      setIsRanking(true);
      setError(null);
      return getRecommendations(
        profileId,
        context,
        discoveryMode,
        signal,
      )
        .then(setResult)
        .catch((requestError: unknown) => {
          if ((requestError as Error).name !== "AbortError") {
            setResult(null);
            setError(
              "We couldn’t reach the local ranking API. Start FastAPI, then try again.",
            );
          }
        })
        .finally(() => setIsRanking(false));
    }, [context, discoveryMode, profileId]);

  useEffect(() => {
    if (isLoadingProfiles || !profileId) return;
    const controller = new AbortController();
    void requestRanking(controller.signal);
    return () => controller.abort();
  }, [isLoadingProfiles, profileId, context, discoveryMode, retryNonce, requestRanking]);

  const selectedProfile = useMemo(
    () => profiles.find((profile) => profile.id === profileId),
    [profileId, profiles],
  );

  const hasRecommendations = Boolean(result?.recommendations.length);

  return (
    <main>
      <header className="masthead">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">CAD</span>
          <span>Discovery Mode prototype</span>
        </div>
        <div className="synthetic-label">Synthetic demo data</div>
      </header>

      <section className="intro" aria-labelledby="page-title">
        <div>
          <h1 id="page-title">Context-Aware Discovery</h1>
          <p className="hypothesis">
            What if recommendation novelty responded to observed diversity,
            reliable context, and—most importantly—what you ask for today?
          </p>
        </div>
        <p className="claim-boundary">
          These patterns motivate a product hypothesis. They do not prove that
          entropy-aware ranking improves outcomes.
        </p>
      </section>

      <div className="workbench">
        <aside className="conditions" aria-label="Ranking conditions">
          <div className="panel-heading">
            <h2>Set the conditions</h2>
            <span>Changes rerank immediately</span>
          </div>

          <label className="select-label" htmlFor="profile">
            Demo profile
          </label>
          <select
            id="profile"
            value={profileId}
            onChange={(event) => setProfileId(event.target.value)}
            disabled={isLoadingProfiles || profiles.length === 0}
          >
            {isLoadingProfiles && <option>Loading profiles…</option>}
            {profiles.map((profile) => (
              <option key={profile.id} value={profile.id}>
                {profile.label}
              </option>
            ))}
          </select>

          <fieldset className="control-group compact-options">
            <legend>Context</legend>
            <div className="segmented">
              {contextOptions.map((option) => (
                <label key={option.value}>
                  <input
                    type="radio"
                    name="context"
                    aria-label={option.label}
                    value={option.value}
                    checked={context === option.value}
                    onChange={() => setContext(option.value)}
                  />
                  <span>{option.label}</span>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset className="control-group discovery-options">
            <legend>What feels right today?</legend>
            {discoveryOptions.map((option) => (
              <label key={option.value}>
                <input
                  type="radio"
                  name="discovery-mode"
                  aria-label={option.label}
                  value={option.value}
                  checked={discoveryMode === option.value}
                  onChange={() => setDiscoveryMode(option.value)}
                />
                <span className="choice-copy">
                  <strong>{option.label}</strong>
                  <small>{option.hint}</small>
                </span>
              </label>
            ))}
          </fieldset>

          {selectedProfile && (
            <section className="signals" aria-labelledby="signals-title">
              <div className="panel-heading">
                <h2 id="signals-title">Signals used</h2>
                <span>Observed behavior, not identity</span>
              </div>
              <SignalRow
                label="Venue diversity"
                value={selectedProfile.venue_entropy}
              />
              <SignalRow
                label="Activity diversity"
                value={selectedProfile.category_entropy}
              />
              <SignalRow label="Confidence" value={selectedProfile.confidence} />
              <div className="signal-meta">
                <span>{selectedProfile.observation_count} observations</span>
                <span>
                  {selectedProfile.weekend_delta >= 0 ? "+" : ""}
                  {selectedProfile.weekend_delta.toFixed(2)} weekend difference
                </span>
              </div>
              <p className="demo-note">
                Synthetic values anchored to aggregate ranges in the analysis.
              </p>
            </section>
          )}
        </aside>

        <section className="ranking" aria-labelledby="ranking-title">
          <div className="ranking-header">
            <div>
              <h2 id="ranking-title">Ranked for this setting</h2>
              <p>Same fictional candidate pool. Different transparent weighting.</p>
            </div>
            {result && (
              <div className="applied-readout" aria-label={`Applied discovery ${Math.round(result.applied_discovery * 100)} percent`}>
                <span>Applied discovery</span>
                <strong>{Math.round(result.applied_discovery * 100)}%</strong>
              </div>
            )}
          </div>

          <div className="announcement" aria-live="polite" aria-atomic="true">
            {isRanking
              ? "Re-ranking fictional places…"
              : result
                ? `${result.recommendations.length} recommendations updated.`
                : ""}
          </div>

          {result && !isRanking && (
            <div
              className={result.uses_neutral_fallback ? "ranking-note fallback" : "ranking-note"}
            >
              <span>{result.uses_neutral_fallback ? "Neutral fallback" : "Why it shifted"}</span>
              <p>{result.ranking_summary}</p>
            </div>
          )}

          {isRanking && <LoadingResults />}

          {error && !isRanking && (
            <div className="error-state" role="alert">
              <strong>Ranking unavailable</strong>
              <p>{error}</p>
              <button type="button" onClick={() => setRetryNonce((value) => value + 1)}>
                Try again
              </button>
            </div>
          )}

          {!isRanking && !error && result && !hasRecommendations && (
            <div className="empty-state">
              <strong>No fictional places matched this run.</strong>
              <p>Try another setting to rerun the candidate pool.</p>
            </div>
          )}

          {!isRanking && !error && hasRecommendations && (
            <ol className="recommendation-list">
              {result!.recommendations.map((recommendation, index) => (
                <li key={recommendation.id}>
                  <article className="recommendation">
                    <div className="rank-number" aria-label={`Rank ${index + 1}`}>
                      {String(index + 1).padStart(2, "0")}
                    </div>
                    <div className="recommendation-copy">
                      <div className="recommendation-title">
                        <div>
                          <span className="category">{recommendation.category}</span>
                          <h3>{recommendation.name}</h3>
                        </div>
                        <span className="score">{recommendation.final_score.toFixed(2)}</span>
                      </div>
                      <p className="reason">{recommendation.reason}</p>
                      <p className="description">{recommendation.description}</p>
                      <details>
                        <summary>Why this ranking?</summary>
                        <div className="score-grid">
                          <ScoreValue label="Baseline relevance" value={recommendation.baseline_relevance} />
                          <ScoreValue label="Venue novelty" value={recommendation.venue_novelty} />
                          <ScoreValue label="Effective activity novelty" value={recommendation.category_novelty} />
                          <ScoreValue label="Distance penalty" value={recommendation.distance_penalty} inverse />
                        </div>
                        <p className="formula-note">
                          Relevance and novelty are blended by applied discovery;
                          familiar activity categories use profile-adjusted activity novelty;
                          distance subtracts up to 0.15. Candidate ID breaks ties.
                        </p>
                      </details>
                    </div>
                  </article>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>

      <section className="method-strip" aria-labelledby="method-title">
        <div>
          <h2 id="method-title">A hypothesis with boundaries</h2>
          <p>
            Entropy stays behind the interface as one ranking signal. No source
            users, coordinates, trajectories, personality labels, or live venue
            data enter this prototype.
          </p>
        </div>
        <div>
          <h3>How we would evaluate it</h3>
          <p>
            Randomize baseline relevance against context-aware ranking over the
            same pool. Measure saves or selections per impression; guard against
            hides, exits, repetition, distance, latency, and sparse-history harm.
          </p>
        </div>
      </section>

      <footer>
        <p>Illustrative ranking over fictional venues; not a validated recommender.</p>
        <a href="#method-title" aria-label="Read the prototype methodology">
          Methodology lives with the analysis
        </a>
      </footer>
    </main>
  );
}

function SignalRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="signal-row">
      <div>
        <span>{label}</span>
        <strong>{Math.round(value * 100)}%</strong>
      </div>
      <div className="measure" aria-hidden="true">
        <span style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
    </div>
  );
}

function ScoreValue({
  label,
  value,
  inverse = false,
}: {
  label: string;
  value: number;
  inverse?: boolean;
}) {
  return (
    <div>
      <span>{label}</span>
      <strong>{inverse ? "−" : ""}{value.toFixed(2)}</strong>
    </div>
  );
}

function LoadingResults() {
  return (
    <div className="loading-list" aria-hidden="true">
      {[0, 1, 2].map((item) => (
        <div className="loading-row" key={item}>
          <span />
          <div><span /><span /><span /></div>
        </div>
      ))}
    </div>
  );
}
