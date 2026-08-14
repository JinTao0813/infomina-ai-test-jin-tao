import type { Metadata } from "next";
import type { ReactNode } from "react";
import "katex/dist/katex.min.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "From Data to Product — Context-Aware Discovery",
  description: "An evidence-led location entropy case study and transparent discovery-ranking prototype.",
};

const directionContract = `
<!--
THESIS: Make the complete evidence-to-product chain read as one inspectable case file; refuse a prototype-first dashboard or detached analysis article.
OWN-WORLD: Cool paper, white evidence plates, ink navy, ultramarine action, citron measured-state labels, and ruled comparative rows.
STORY: Understand the question, inspect generated notebook evidence, compare opportunities, then operate and challenge the ranking hypothesis.
FIRST VIEWPORT: Shared case-study masthead, persistent claim rail, decisive analysis thesis, and a five-stage evidence path leading directly to Discovery Mode.
FORM: Annotated case-file rail, grounded structure 3; seed 526f6362.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, and DESIGN.md
-->
`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <template dangerouslySetInnerHTML={{ __html: directionContract }} />
        {children}
      </body>
    </html>
  );
}
