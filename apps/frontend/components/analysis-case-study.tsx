import Link from "next/link";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import type {
  AnalysisArtifact,
  AnalysisOutput,
  AnalysisSection,
} from "@/lib/analysis-types";
import ClaimBoundary from "./claim-boundary";
import SiteHeader from "./site-header";

const NOTEBOOK_URL = "https://github.com/JinTao0813/infomina-ai-test-jin-tao/blob/main/notebooks/location_entropy_analysis.ipynb";
const NOTEBOOK_DOWNLOAD_URL = "https://raw.githubusercontent.com/JinTao0813/infomina-ai-test-jin-tao/main/notebooks/location_entropy_analysis.ipynb";

const kindLabels: Record<string, string> = {
  overview: "Executive summary",
  method: "Method & preparation",
  observation: "Observed evidence",
  hypothesis: "Interpretation & hypothesis",
  implementation: "Implementation choice",
  limitation: "Limit & claim boundary",
};

export default function AnalysisCaseStudy({ artifact }: { artifact: AnalysisArtifact }) {
  return (
    <div className="case-study-page">
      <SiteHeader active="analysis" />
      <ClaimBoundary />

      <main id="main-content">
        <section className="case-hero" aria-labelledby="case-title">
          <div className="case-hero-copy">
            <h1 id="case-title">{artifact.title}</h1>
            <ReactMarkdown>{artifact.summary}</ReactMarkdown>
            <div className="hero-actions">
              <Link className="primary-action" href="/prototype/discovery">Open Discovery Mode</Link>
              <a href="#objective-and-executive-summary">Read the analysis</a>
            </div>
          </div>
          <div className="evidence-path" aria-label="Case study path">
            {[
              ["Study", "Historical check-ins"],
              ["Measure", "Profile diversity"],
              ["Interpret", "Bounded findings"],
              ["Hypothesize", "Discovery ranking"],
              ["Test", "Interactive prototype"],
            ].map(([verb, object]) => (
              <div key={verb}>
                <strong>{verb}</strong>
                <span>{object}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="executive-strip" aria-label="Executive summary">
          <div>
            <strong>Question</strong>
            <p>Do observed visits concentrate in a few places, and how does that pattern vary by city and context?</p>
          </div>
          <div>
            <strong>Selected hypothesis</strong>
            <p>Let explicit discovery intent lead; use profile history and reliable context only as bounded adjustments.</p>
          </div>
          <div>
            <strong>Evidence still needed</strong>
            <p>A randomized comparison must establish usefulness without worsening trust, privacy, or sparse-history outcomes.</p>
          </div>
        </section>

        <div className="case-layout">
          <aside className="section-rail">
            <nav aria-label="Case study sections">
              <strong>Analysis path</strong>
              <ol>
                {artifact.sections.map((section) => (
                  <li key={section.id}>
                    <a href={`#${section.id}`}>{section.title.replace(/^\d+\.\s*/, "")}</a>
                  </li>
                ))}
              </ol>
            </nav>
            <div className="artifact-ticket">
              <strong>Generated source</strong>
              <span>{artifact.source_notebook}</span>
              <span>{formatTimestamp(artifact.generated_at)}</span>
              <code>{artifact.source_sha256.slice(0, 12)}</code>
              <a href={NOTEBOOK_URL}>View executed notebook</a>
              <a href={NOTEBOOK_DOWNLOAD_URL} download>Download notebook</a>
            </div>
          </aside>

          <article className="analysis-story">
            {artifact.sections.map((section) => (
              <AnalysisSectionView key={section.id} section={section} />
            ))}

            <section className="prototype-handoff" aria-labelledby="handoff-title">
              <div>
                <h2 id="handoff-title">The hypothesis is inspectable</h2>
                <p>
                  Change an explicit preference and watch the same privacy-safe historical candidate pool rerank. Profile entropy and aggregate candidate novelty stay visibly separate.
                </p>
              </div>
              <Link className="primary-action" href="/prototype/discovery">Open Discovery Mode</Link>
            </section>
          </article>
        </div>
      </main>

      <footer className="site-footer">
        <p>Executed notebook is authoritative. Website artifact fingerprint: {artifact.source_sha256.slice(0, 12)}.</p>
        <a href="#main-content">Back to top</a>
      </footer>
    </div>
  );
}

function AnalysisSectionView({ section }: { section: AnalysisSection }) {
  return (
    <section id={section.id} className="analysis-section" aria-labelledby={`${section.id}-title`}>
      <header className="analysis-section-heading">
        <h2 id={`${section.id}-title`}>{section.title}</h2>
        <span data-kind={section.kind}>{kindLabels[section.kind] ?? section.kind}</span>
      </header>
      {section.blocks.map((block, index) => {
        if (block.type === "markdown") {
          return (
            <div className="notebook-markdown" key={`${section.id}-markdown-${index}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                  a: ({ href, children }) => (
                    <a href={href} target={href?.startsWith("http") ? "_blank" : undefined} rel={href?.startsWith("http") ? "noreferrer" : undefined}>
                      {children}
                    </a>
                  ),
                  img: ({ src, alt }) => (
                    // Exporter only emits committed safe static paths.
                    <img src={src ?? ""} alt={alt ?? ""} loading="eager" />
                  ),
                  table: ({ children }) => (
                    <div className="markdown-table-wrap" tabIndex={0}>
                      <table>
                        <caption>Analysis table from the executed notebook</caption>
                        {children}
                      </table>
                    </div>
                  ),
                }}
              >
                {block.markdown}
              </ReactMarkdown>
            </div>
          );
        }
        return (
          <div className="executed-cell" key={`${section.id}-code-${index}`}>
            <details className="code-disclosure">
              <summary>View executed code</summary>
              <div className="code-heading">
                <span>Python</span>
                <span>Execution {block.execution_count ?? "—"}</span>
              </div>
              <pre><code>{block.source}</code></pre>
            </details>
            {block.outputs.length > 0 && (
              <div className="cell-outputs">
                {block.outputs.map((output, outputIndex) => (
                  <AnalysisOutputView
                    key={`${section.id}-output-${outputIndex}`}
                    output={output}
                    sectionTitle={section.title}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}
    </section>
  );
}

function AnalysisOutputView({ output, sectionTitle }: { output: AnalysisOutput; sectionTitle: string }) {
  if (output.type === "image") {
    return (
      <figure className="analysis-figure">
        <img src={`/generated/analysis/${output.asset}`} alt={output.alt} loading="eager" />
        <figcaption>{output.caption}</figcaption>
      </figure>
    );
  }
  if (output.type === "text") {
    return <pre className="text-output" aria-label={`Executed output for ${sectionTitle}`}>{output.text}</pre>;
  }
  return (
    <div className="output-table-wrap">
      <table>
        <caption>Executed aggregate output for {sectionTitle}</caption>
        <thead><tr>{output.headers.map((header, index) => <th key={`${header}-${index}`} scope="col">{header || "Row"}</th>)}</tr></thead>
        <tbody>
          {output.rows.map((row, rowIndex) => (
            <tr key={rowIndex}>{row.map((value, index) => <td key={index}>{value}</td>)}</tr>
          ))}
        </tbody>
      </table>
      <div className="mobile-output-table">
        {output.rows.map((row, rowIndex) => (
          <dl key={rowIndex}>
            {row.map((value, index) => (
              <div key={index}><dt>{output.headers[index] || "Row"}</dt><dd>{value}</dd></div>
            ))}
          </dl>
        ))}
      </div>
    </div>
  );
}

function formatTimestamp(timestamp: string) {
  if (timestamp === "Not recorded") return "Execution time not recorded";
  return `Generated ${new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }).format(new Date(timestamp))} UTC`;
}
