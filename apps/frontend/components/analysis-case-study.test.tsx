import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import artifact from "@/generated/analysis.json";
import type { AnalysisArtifact } from "@/lib/analysis-types";
import AnalysisCaseStudy from "./analysis-case-study";

const generatedArtifact = artifact as AnalysisArtifact;

describe("AnalysisCaseStudy", () => {
  it("renders the generated notebook story, navigation, metadata, and claim boundary", () => {
    render(<AnalysisCaseStudy artifact={generatedArtifact} />);

    expect(screen.getByRole("heading", { name: artifact.title })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Case study sections" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "1. Objective and executive summary" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "2. Dataset and quality checks" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "8. Insights and product opportunities" })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Open Discovery Mode" })[0]).toHaveAttribute("href", "/prototype/discovery");
    expect(screen.getByRole("link", { name: "View executed notebook" })).toHaveAttribute("href", expect.stringContaining("github.com"));
    expect(screen.getByRole("link", { name: "Download notebook" })).toHaveAttribute("href", expect.stringContaining("raw.githubusercontent.com"));
    expect(screen.getAllByText(/not a trained or validated recommender/i).length).toBeGreaterThan(0);
    expect(screen.getByRole("heading", { name: "9. Selected concept and product hypothesis" })).toBeInTheDocument();
    expect(screen.getByText(new RegExp(artifact.source_notebook))).toBeInTheDocument();
    expect(screen.getAllByText(new RegExp(artifact.source_sha256.slice(0, 12))).length).toBeGreaterThan(0);
  });

  it("keeps executed code collapsible and gives outputs accessible alternatives", async () => {
    const user = userEvent.setup();
    render(<AnalysisCaseStudy artifact={generatedArtifact} />);

    const disclosure = screen.getAllByText("View executed code")[0];
    expect(disclosure.closest("details")).not.toHaveAttribute("open");
    await user.click(disclosure);
    expect(disclosure.closest("details")).toHaveAttribute("open");

    expect(screen.getByAltText(/similar normalized venue entropy distributions/i)).toBeInTheDocument();
    expect(screen.getByText(/The two city distributions overlap substantially/i)).toBeInTheDocument();
    expect(screen.getAllByRole("table")[0]).toHaveAccessibleName(/executed aggregate output/i);
  });
});
