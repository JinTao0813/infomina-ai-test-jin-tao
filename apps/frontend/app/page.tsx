import type { Metadata } from "next";

import AnalysisCaseStudy from "@/components/analysis-case-study";
import artifact from "@/generated/analysis.json";
import type { AnalysisArtifact } from "@/lib/analysis-types";

export const metadata: Metadata = {
  title: "From Data to Product — Location Entropy Case Study",
  description: "Executed analysis, product reasoning, and an inspectable discovery-ranking hypothesis.",
};

export default function Home() {
  return <AnalysisCaseStudy artifact={artifact as AnalysisArtifact} />;
}
