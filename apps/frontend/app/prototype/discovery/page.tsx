import type { Metadata } from "next";

import DiscoveryExperience from "@/components/discovery-experience";

export const metadata: Metadata = {
  title: "Discovery Mode — From Data to Product",
  description: "Inspect a deterministic discovery-ranking hypothesis over privacy-safe historical candidates.",
};

export default function DiscoveryPage() {
  return <DiscoveryExperience />;
}
