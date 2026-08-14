import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import DiscoveryExperience from "./discovery-experience";

const profiles = [
  {
    id: "mixed",
    label: "Mixed demo",
    venue_entropy: 0.85,
    category_entropy: 0.76,
    weekend_delta: 0.06,
    observation_count: 154,
    confidence: 0.84,
    familiar_categories: ["Coffee Shop", "Train Station"],
  },
  {
    id: "sparse",
    label: "New / sparse history demo",
    venue_entropy: 0.62,
    category_entropy: 0.51,
    weekend_delta: 0.11,
    observation_count: 8,
    confidence: 0.12,
    familiar_categories: ["Coffee Shop"],
  },
];

const recommendations = [
  {
    id: "candidate-nyc-001",
    label: "NYC · Train Station · Candidate 01",
    city: "NYC",
    category: "Train Station",
    historical_checkins: 1145,
    distinct_historical_visitors: 265,
    aggregate_popularity_percentile: 100,
    baseline_relevance: 0.95,
    aggregate_novelty: 0,
    provenance: "Aggregated historical Foursquare sample",
    final_score: 0.81,
    category_familiarity: 1,
    category_discovery: 0,
    novelty_score: 0,
    reason: "Higher aggregate popularity supports your familiar choice.",
  },
  {
    id: "candidate-nyc-007",
    label: "NYC · Burrito Place · Candidate 07",
    city: "NYC",
    category: "Burrito Place",
    historical_checkins: 35,
    distinct_historical_visitors: 25,
    aggregate_popularity_percentile: 13,
    baseline_relevance: 0.43,
    aggregate_novelty: 0.87,
    provenance: "Aggregated historical Foursquare sample",
    final_score: 0.76,
    category_familiarity: 0,
    category_discovery: 1,
    novelty_score: 0.9,
    reason: "Less commonly visited in this historical sample.",
  },
];

const recommendationResponse = {
  profile: profiles[0],
  context: "weekday",
  discovery_mode: "balanced",
  applied_discovery: 0.57,
  uses_neutral_fallback: false,
  ranking_summary: "Your balanced choice combines aggregate popularity with candidate novelty.",
  recommendations,
  disclaimer: "Illustrative discovery ranking over privacy-safe historical candidates; not a trained or validated recommender.",
};

function jsonResponse(data: unknown, ok = true): Promise<Response> {
  return Promise.resolve({
    ok,
    status: ok ? 200 : 503,
    json: () => Promise.resolve(data),
  } as Response);
}

describe("DiscoveryExperience", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockImplementationOnce(() => jsonResponse(profiles))
        .mockImplementation((_, options?: RequestInit) => {
          const body = options?.body ? JSON.parse(options.body as string) : {};
          const next = body.discovery_mode === "something_new"
            ? { ...recommendationResponse, discovery_mode: "something_new", recommendations: [...recommendations].reverse() }
            : recommendationResponse;
          return jsonResponse(next);
        }),
    );
  });

  afterEach(() => vi.unstubAllGlobals());

  it("renders the evidence bridge, initial state, provenance, and returned order", async () => {
    render(<DiscoveryExperience />);

    expect(screen.getByRole("heading", { name: "Context-Aware Discovery" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "How evidence becomes a ranking hypothesis" })).toBeInTheDocument();
    expect(await screen.findByText("NYC · Train Station · Candidate 01")).toBeInTheDocument();
    expect(screen.getByText("NYC · Burrito Place · Candidate 07")).toBeInTheDocument();
    expect(screen.getByText("Higher aggregate popularity supports your familiar choice.")).toBeInTheDocument();
    expect(screen.getByText(/historical sample cannot establish/i)).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "Balanced" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "Weekday" })).toBeChecked();
    expect(screen.getByLabelText("Demo profile")).toHaveValue("mixed");
  });

  it("sends the expected request when keyboard-operable controls change", async () => {
    const user = userEvent.setup();
    render(<DiscoveryExperience />);
    await screen.findByText("NYC · Train Station · Candidate 01");

    await user.selectOptions(screen.getByLabelText("Demo profile"), "sparse");
    await user.click(screen.getByRole("radio", { name: "Weekend" }));
    await user.click(screen.getByRole("radio", { name: "Show me something new" }));

    await waitFor(() => {
      const calls = vi.mocked(fetch).mock.calls;
      const bodies = calls
        .filter(([, options]) => options?.method === "POST")
        .map(([, options]) => JSON.parse(options?.body as string));
      expect(bodies).toContainEqual({
        profile_id: "sparse",
        context: "weekend",
        discovery_mode: "something_new",
        limit: 6,
      });
    });
  });

  it("visibly reranks and announces the change when explicit preference changes", async () => {
    const user = userEvent.setup();
    render(<DiscoveryExperience />);
    await screen.findByText("NYC · Train Station · Candidate 01");

    await user.click(screen.getByRole("radio", { name: "Show me something new" }));

    await waitFor(() => {
      const rankedLabels = screen.getAllByRole("heading", { level: 3 }).map((heading) => heading.textContent);
      expect(rankedLabels[0]).toBe("NYC · Burrito Place · Candidate 07");
    });
    expect(screen.getByRole("status")).toHaveTextContent("recommendations updated");
    expect(screen.getAllByText("Aggregate candidate novelty").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Category familiarity").length).toBeGreaterThan(0);
  });

  it("shows loading and a recoverable API error", async () => {
    let rejectRequest: (reason: Error) => void = () => undefined;
    vi.mocked(fetch)
      .mockReset()
      .mockImplementationOnce(() => jsonResponse(profiles))
      .mockImplementationOnce(
        () =>
          new Promise<Response>((_, reject) => {
            rejectRequest = reject;
          }),
      )
      .mockImplementation(() => jsonResponse(recommendationResponse));

    const user = userEvent.setup();
    render(<DiscoveryExperience />);
    expect(await screen.findByText("Re-ranking historical candidates…")).toBeInTheDocument();

    rejectRequest(new Error("offline"));
    expect(await screen.findByRole("alert")).toHaveTextContent("couldn’t reach the local ranking API");

    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByText("NYC · Train Station · Candidate 01")).toBeInTheDocument();
  });
});
