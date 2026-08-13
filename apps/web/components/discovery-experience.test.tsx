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
    familiar_categories: ["Coffee Shop"],
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

const recommendationResponse = {
  profile: profiles[0],
  context: "weekday",
  discovery_mode: "balanced",
  applied_discovery: 0.57,
  uses_neutral_fallback: false,
  ranking_summary: "Your balanced choice combines relevance with measured novelty.",
  recommendations: [
    {
      id: "venue-02",
      name: "Northline Coffee Works",
      category: "Coffee Shop",
      description: "A fictional coffee counter.",
      final_score: 0.81,
      baseline_relevance: 0.9,
      venue_novelty: 0.42,
      category_novelty: 0.12,
      novelty_score: 0.3,
      distance_penalty: 0.08,
      reason: "A new venue in a familiar activity category.",
    },
    {
      id: "venue-07",
      name: "Afterimage Gallery",
      category: "Gallery",
      description: "A fictional artist-run space.",
      final_score: 0.76,
      baseline_relevance: 0.65,
      venue_novelty: 0.82,
      category_novelty: 0.78,
      novelty_score: 0.8,
      distance_penalty: 0.11,
      reason: "A different kind of activity.",
    },
  ],
  disclaimer: "Illustrative ranking over fictional venues; not a validated recommender.",
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
        .mockImplementation(() => jsonResponse(recommendationResponse)),
    );
  });

  afterEach(() => vi.unstubAllGlobals());

  it("renders the initial Mixed, Weekday, Balanced state and returned order", async () => {
    render(<DiscoveryExperience />);

    expect(screen.getByRole("heading", { name: "Context-Aware Discovery" })).toBeInTheDocument();
    expect(await screen.findByText("Northline Coffee Works")).toBeInTheDocument();
    expect(screen.getByText("Afterimage Gallery")).toBeInTheDocument();
    expect(screen.getByText("A new venue in a familiar activity category.")).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "Balanced" })).toBeChecked();
    expect(screen.getByRole("radio", { name: "Weekday" })).toBeChecked();
    expect(screen.getByLabelText("Demo profile")).toHaveValue("mixed");
  });

  it("sends the expected request when keyboard-operable controls change", async () => {
    const user = userEvent.setup();
    render(<DiscoveryExperience />);
    await screen.findByText("Northline Coffee Works");

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
    expect(await screen.findByText("Re-ranking fictional places…")).toBeInTheDocument();

    rejectRequest(new Error("offline"));
    expect(await screen.findByRole("alert")).toHaveTextContent("couldn’t reach the local ranking API");

    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByText("Northline Coffee Works")).toBeInTheDocument();
  });
});
