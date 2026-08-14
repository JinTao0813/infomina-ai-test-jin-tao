"use client";

import Link from "next/link";
import React, { useCallback, useEffect, useMemo, useState } from "react";

import { getProfiles, getRecommendations } from "@/lib/api";
import type {
  Context,
  DiscoveryMode,
  Profile,
  RecommendationResponse,
} from "@/lib/types";
import ClaimBoundary from "./claim-boundary";
import SiteHeader from "./site-header";

const contextOptions: Array<{ value: Context; label: string }> = [
  { value: "weekday", label: "Weekday" },
  { value: "weekend", label: "Weekend" },
];

const discoveryOptions: Array<{
  value: DiscoveryMode;
  label: string;
  hint: string;
}> = [
  { value: "familiar", label: "Keep it familiar", hint: "Historical popularity leads" },
  { value: "balanced", label: "Balanced", hint: "A measured mix" },
  { value: "something_new", label: "Show me something new", hint: "Candidate novelty has more weight" },
];

export default function DiscoveryExperience() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [profileId, setProfileId] = useState("mixed");
  const [context, setContext] = useState<Context>("weekday");
  const [discoveryMode, setDiscoveryMode] = useState<DiscoveryMode>("balanced");
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
      return getRecommendations(profileId, context, discoveryMode, signal)
        .then(setResult)
        .catch((requestError: unknown) => {
          if ((requestError as Error).name !== "AbortError") {
            setResult(null);
            setError("We couldn’t reach the local ranking API. Start FastAPI, then try again.");
          }
        })
        .finally(() => setIsRanking(false));
    },
    [context, discoveryMode, profileId],
  );

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
    <div className="prototype-page">
      <SiteHeader active="prototype" />
      <ClaimBoundary />

      <main id="main-content">
        <section className="prototype-intro" aria-labelledby="page-title">
          <div>
            <h1 id="page-title">Context-Aware Discovery</h1>
            <p className="hypothesis">
              Inspect how explicit intent, profile-level diversity, reliable context, and separate candidate signals can form one cautious discovery-ranking policy.
            </p>
          </div>
          <div className="historical-stamp">
            <strong>Historical candidate sample</strong>
            <span>2012–2013 source check-ins</span>
          </div>
        </section>

        <section className="evidence-bridge" aria-labelledby="bridge-title">
          <div className="bridge-heading">
            <h2 id="bridge-title">How evidence becomes a ranking hypothesis</h2>
            <Link href="/#selected-concept-and-product-hypothesis">Trace this reasoning in the analysis</Link>
          </div>
          <ol>
            <li>
              <span>Measured</span>
              <strong>Profile history diversity</strong>
              <p>Normalized venue and category entropy describe observed synthetic-profile history—not venues, quality, or personality.</p>
            </li>
            <li>
              <span>Applied</span>
              <strong>A bounded ranking signal</strong>
              <p>Explicit intent leads. Reliable weekend context is modest; sparse histories regress toward a neutral profile signal.</p>
            </li>
            <li>
              <span>Not proven</span>
              <strong>Recommendation usefulness</strong>
              <p>The ranker is deterministic and illustrative. Only a future randomized test could validate the product hypothesis.</p>
            </li>
          </ol>
          <p className="definition-line">
            <strong>“New” here means</strong> new to the synthetic profile or less commonly visited in this historical sample—not newly opened.
          </p>
        </section>

        <div className="workbench">
          <aside className="conditions" aria-label="Ranking conditions">
            <div className="panel-heading">
              <h2>Set the conditions</h2>
              <span>Changes rerank immediately</span>
            </div>

            <label className="select-label" htmlFor="profile">Synthetic profile</label>
            <select
              id="profile"
              value={profileId}
              onChange={(event) => setProfileId(event.target.value)}
              disabled={isLoadingProfiles || profiles.length === 0}
              aria-label="Demo profile"
            >
              {isLoadingProfiles && <option>Loading profiles…</option>}
              {profiles.map((profile) => (
                <option key={profile.id} value={profile.id}>{profile.label}</option>
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
                  <h2 id="signals-title">Profile signals</h2>
                  <span>Observed history, not identity</span>
                </div>
                <SignalRow label="Normalized venue entropy" value={selectedProfile.venue_entropy} />
                <SignalRow label="Normalized category entropy" value={selectedProfile.category_entropy} />
                <SignalRow label="History confidence" value={selectedProfile.confidence} />
                <div className="signal-meta">
                  <span>{selectedProfile.observation_count} synthetic observations</span>
                  <span>{selectedProfile.weekend_delta >= 0 ? "+" : ""}{selectedProfile.weekend_delta.toFixed(2)} weekend difference</span>
                </div>
                <p className="demo-note">Synthetic values anchored to aggregate ranges in the executed analysis.</p>
              </section>
            )}
          </aside>

          <section className="ranking" aria-labelledby="ranking-title">
            <div className="ranking-header">
              <div>
                <h2 id="ranking-title">Ranked for this setting</h2>
                <p>Same safe candidate pool. Different transparent weighting.</p>
              </div>
              {result && (
                <div className="applied-readout" aria-label={`Applied discovery ${Math.round(result.applied_discovery * 100)} percent`}>
                  <span>Applied discovery</span>
                  <strong>{Math.round(result.applied_discovery * 100)}%</strong>
                </div>
              )}
            </div>

            <div className="announcement" role="status" aria-live="polite" aria-atomic="true">
              {isRanking ? "Re-ranking historical candidates…" : result ? `${result.recommendations.length} recommendations updated.` : ""}
            </div>

            {result && !isRanking && (
              <div className={result.uses_neutral_fallback ? "ranking-note fallback" : "ranking-note"}>
                <span>{result.uses_neutral_fallback ? "Neutral fallback" : "Why it shifted"}</span>
                <p>{result.ranking_summary}</p>
              </div>
            )}

            {isRanking && <LoadingResults />}

            {error && !isRanking && (
              <div className="error-state" role="alert">
                <strong>Ranking unavailable</strong>
                <p>{error}</p>
                <button type="button" onClick={() => setRetryNonce((value) => value + 1)}>Try again</button>
              </div>
            )}

            {!isRanking && !error && result && !hasRecommendations && (
              <div className="empty-state">
                <strong>No candidates matched this run.</strong>
                <p>Try another setting to rerun the safe candidate pool.</p>
              </div>
            )}

            {!isRanking && !error && hasRecommendations && (
              <ol className="recommendation-list">
                {result!.recommendations.map((recommendation, index) => (
                  <li key={recommendation.id}>
                    <article className="recommendation">
                      <div className="rank-number" aria-label={`Rank ${index + 1}`}>{String(index + 1).padStart(2, "0")}</div>
                      <div className="recommendation-copy">
                        <div className="recommendation-title">
                          <div>
                            <span className="category">{recommendation.city} · {recommendation.category}</span>
                            <h3>{recommendation.label}</h3>
                          </div>
                          <span className="score" aria-label={`Illustrative final score ${recommendation.final_score.toFixed(2)}`}>{recommendation.final_score.toFixed(2)}</span>
                        </div>
                        <p className="reason">{recommendation.reason}</p>
                        <dl className="provenance-row">
                          <div><dt>Historical check-ins</dt><dd>{recommendation.historical_checkins.toLocaleString()}</dd></div>
                          <div><dt>Distinct visitors</dt><dd>{recommendation.distinct_historical_visitors.toLocaleString()}</dd></div>
                          <div><dt>Popularity percentile</dt><dd>{recommendation.aggregate_popularity_percentile}</dd></div>
                        </dl>
                        <p className="provenance-note">{recommendation.provenance} · Rounded support · Pseudonymous label</p>
                        <details>
                          <summary>Inspect score breakdown</summary>
                          <div className="score-grid">
                            <ScoreValue label="Illustrative baseline relevance" value={recommendation.baseline_relevance} />
                            <ScoreValue label="Aggregate candidate novelty" value={recommendation.aggregate_novelty} />
                            <ScoreValue label="Category familiarity" value={recommendation.category_familiarity} />
                            <ScoreValue label="Combined novelty input" value={recommendation.novelty_score} />
                          </div>
                          <p className="formula-note">
                            Baseline relevance transforms aggregate historical popularity. Candidate novelty is its inverse. Category familiarity comes from the selected synthetic profile. Profile entropy only adjusts applied discovery; it is never a candidate score. Generated candidate ID breaks ties.
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

        <aside className="historical-warning" aria-label="Historical relevance limitation">
          <strong>Historical sample—not a place guide</strong>
          <p>This historical sample cannot establish whether a candidate still exists, is open, is desirable today, or is suitable for a real trip.</p>
        </aside>

        <section className="method-strip" aria-labelledby="method-title">
          <div>
            <h2 id="method-title">Candidate-generation boundary</h2>
            <p>Offline generation excludes private-home and sensitive residential or workplace categories, requires 30 check-ins and 15 distinct visitors, rounds support, and removes source venue IDs, user IDs, coordinates, timestamps, and trajectories.</p>
          </div>
          <div>
            <strong>How this hypothesis would be evaluated</strong>
            <p>Randomize baseline ranking against context-aware ranking over the same pool. Measure saves or selections per impression; guard against hides, exits, repetition, distance, latency, and sparse-history harm.</p>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <p>Illustrative discovery ranking over privacy-safe historical candidates; not a trained or validated recommender.</p>
        <Link href="/">Return to the analysis</Link>
      </footer>
    </div>
  );
}

function SignalRow({ label, value }: { label: string; value: number }) {
  return (
    <div className="signal-row">
      <div><span>{label}</span><strong>{Math.round(value * 100)}%</strong></div>
      <div className="measure" aria-hidden="true"><span style={{ width: `${Math.round(value * 100)}%` }} /></div>
    </div>
  );
}

function ScoreValue({ label, value }: { label: string; value: number }) {
  return <div><span>{label}</span><strong>{value.toFixed(2)}</strong></div>;
}

function LoadingResults() {
  return (
    <div className="loading-list" aria-hidden="true">
      {[0, 1, 2].map((item) => (
        <div className="loading-row" key={item}><span /><div><span /><span /><span /></div></div>
      ))}
    </div>
  );
}
