export interface AnalysisArtifact {
  schema_version: number;
  title: string;
  summary: string;
  source_notebook: string;
  source_sha256: string;
  generated_at: string;
  sections: AnalysisSection[];
}

export interface AnalysisSection {
  id: string;
  title: string;
  kind: "overview" | "method" | "observation" | "hypothesis" | "implementation" | "limitation";
  blocks: AnalysisBlock[];
}

export type AnalysisBlock = MarkdownBlock | CodeBlock;

export interface MarkdownBlock {
  type: "markdown";
  markdown: string;
}

export interface CodeBlock {
  type: "code";
  execution_count: number | null;
  source: string;
  outputs: AnalysisOutput[];
}

export type AnalysisOutput = TextOutput | TableOutput | ImageOutput;

export interface TextOutput {
  type: "text";
  text: string;
}

export interface TableOutput {
  type: "table";
  headers: string[];
  rows: string[][];
}

export interface ImageOutput {
  type: "image";
  asset: string;
  sha256: string;
  alt: string;
  caption: string;
}
