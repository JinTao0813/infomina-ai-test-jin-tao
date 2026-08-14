---
name: From Data to Product
description: A cool, evidence-led system for reading analysis and inspecting ranking behavior.
colors:
  ink-navy: "#111c34"
  ink-soft: "#516079"
  cool-paper: "#f3f6fb"
  surface: "#ffffff"
  rule: "#c8d2e3"
  rule-dark: "#8f9db3"
  action-blue: "#284bdb"
  action-blue-dark: "#1735aa"
  action-blue-pale: "#dfe6ff"
  measured-citron: "#d9f45f"
  error: "#a82424"
typography:
  display:
    fontFamily: "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "clamp(3rem, 5.5vw, 5.8rem)"
    fontWeight: 700
    lineHeight: 0.93
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "clamp(1.85rem, 3vw, 2.75rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.035em"
  body:
    fontFamily: "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.74rem"
    fontWeight: 780
    lineHeight: 1.5
rounded:
  compact: "4px"
  control: "6px"
  panel: "10px"
spacing:
  compact: "8px"
  control: "12px"
  panel: "28px"
  section: "70px"
components:
  action-control:
    backgroundColor: "{colors.action-blue}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "10px 15px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-navy}"
    rounded: "{rounded.control}"
    height: "46px"
  measured-readout:
    backgroundColor: "{colors.measured-citron}"
    textColor: "{colors.ink-navy}"
    rounded: "{rounded.control}"
    padding: "9px 12px"
---

# Design System: From Data to Product

## Overview

**Creative North Star: "The Evidence Workbench"**

A cool, precise work surface makes the full evidence chain inspectable. The system feels like an annotated analytical case file rather than a consumer recommendation feed: source and claim boundaries stay visible, generated findings occupy white evidence plates, and controls sit beside the outcomes they affect.

The visual language is restrained and dense without becoming clinical. Blue marks action and inference; citron marks measured or declared state. Ruled paths, tables, figures, and ranked strips carry comparison without turning every thought into a card.

**Key Characteristics:**
- Cool paper and white working surfaces
- Ink-heavy typography with compact evidence labels
- One action blue and one measured-state citron
- Ruled reading paths and result strips instead of repeated cards
- Interpretations, provenance, and limitations adjacent to outcomes

## Colors

The palette separates action, measured state, neutral evidence, and warning without relying on color alone.

### Primary
- **Action Blue:** selected controls, links, rank markers, and implementation labels.
- **Deep Action Blue:** readable emphasis and hover states.

### Secondary
- **Measured Citron:** applied-discovery readouts, historical-sample stamps, and declared measured state only.

### Neutral
- **Ink Navy:** headings, claim-boundary rails, and primary content.
- **Soft Ink:** supporting explanations, metadata, and provenance.
- **Cool Paper:** page ground.
- **Surface White:** analysis outputs and active work areas.
- **Rules:** section boundaries, tables, and comparison structure.

**The Measured Citron Rule.** Citron labels a measured or declared state; it is not decoration and never replaces a textual label.

## Typography

**Display and Body Font:** platform UI sans-serif stack.

**Character:** Workmanlike and direct. Tight display tracking gives the thesis authority; compact labels and tabular numbers make evidence scan quickly.

### Hierarchy
- **Display:** bold, tightly tracked, and reserved for each route’s thesis.
- **Headline:** large section titles with a compact line height and balanced wrapping.
- **Title:** bold 1.0–1.36rem labels for workbench regions and ranked candidates.
- **Body:** 1rem base; analytical prose stays near 74 characters per line.
- **Label:** 0.60–0.76rem with strong weight for evidence state, metadata, controls, and provenance.

**The Plain-Language Rule.** Technical measurements may be compact, but every result first receives a readable interpretation or reason.

## Layout

The shared shell reaches 1380px with 32px desktop gutters. The analysis route uses a thesis-and-path first viewport, a three-part executive strip, then a 240px sticky section rail beside a reading column capped near 980px. Discovery Mode uses an evidence bridge followed by an approximately 29/71 conditions-and-ranking workbench.

At 1000px, both routes stack: the analysis rail becomes a two-part index and the workbench places controls before results. At 700px, all core structures become one column, generated output tables switch to labeled record lists, gutters tighten to 12px, and fixed-position aids remain readable without horizontal page overflow.

Spacing expands at analytical section boundaries and contracts inside related evidence. There is always more room before a new section heading than after it.

## Elevation & Depth

The system is flat by default. Tonal layers and one-pixel rules carry most hierarchy. One soft offset ambient shadow lifts a complete evidence plate or workbench; individual findings and recommendations never receive separate elevation.

**The One Work Surface Rule.** Ranked recommendations are ruled rows within one work surface, never separately elevated cards.

## Shapes

Corners are compact and functional: 4px for labels, 6px for controls and readouts, and 10px for explanatory or warning panels. Tables and major work surfaces remain square. Rules are one pixel. The asymmetrical D→P mark is the only deliberately unusual silhouette.

## Components

### Navigation
- A 64px sticky desktop masthead becomes 56px on mobile.
- Active routes use a textual `aria-current` state plus a blue bottom rule.
- The dark claim rail remains directly below navigation and names its boundary in citron text.

### Action controls
- **Shape:** compact 6px corners and at least 44px touch height.
- **Selected:** white text on Action Blue plus native input semantics.
- **Focus:** three-pixel high-contrast outline with offset.
- **Disabled:** cool neutral fill and explicit muted state.

### Inputs
- White fill, dark one-pixel rule, 46px minimum height, visible label, and the shared focus outline.

### Evidence sections
- Structure: section title, named evidence-state label, narrative, prominent output, and optional executed-code disclosure.
- Charts always have concise alt text and an interpretation caption.
- Wide generated outputs switch to key/value records on narrow screens.

### Result list
- Structure: rank, city/category provenance, pseudonymous label, final score, plain-language reason, aggregate support, then optional breakdown.
- Native disclosure opens a four-column score grid, two columns on mobile.
- Candidate novelty, category familiarity, and profile entropy are always named separately.

### Status panels
- Loading uses content-shaped ruled skeleton rows.
- Error names the unavailable service and recovery action.
- Neutral fallback uses a citron-tinted panel with explicit limited-history language.
- Historical relevance uses a named amber warning with plain text, never color alone.

## Do's and Don'ts

### Do:
- **Do** keep provenance, claim strength, and output visible near each other.
- **Do** distinguish observation, interpretation, hypothesis, implementation, and limitation in text.
- **Do** label synthetic profiles, historical aggregates, and uncertain inference explicitly.
- **Do** use ruled rows and tables for comparable evidence.
- **Do** preserve native semantics, visible focus, live announcements, and reduced-motion behavior.

### Don't:
- **Don't** use entropy as identity, personality, venue quality, freshness, or intent language.
- **Don't** scatter citron as decorative accent.
- **Don't** nest cards or elevate individual findings and results.
- **Don't** hide critical explanations behind hover or color alone.
- **Don't** invent venue proper names when the source does not provide them.
