import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Discovery Mode — Context-Aware Discovery",
  description: "A transparent interaction prototype over synthetic data.",
};

const directionContract = `
<!--
THESIS: Make cause and effect read like an annotated evidence review; refuse the generic dashboard grid.
OWN-WORLD: Cool paper, ink navy, ultramarine controls, citron measurement marks, ruled result strips.
STORY: Set conditions, see the applied signal, inspect reranking, then understand limits and evaluation.
FIRST VIEWPORT: Compact title above a two-column workbench; conditions and signals left, ranked evidence right.
FORM: Explain-first evidence dossier, grounded direction 6; seed 8b3c53b3.
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
