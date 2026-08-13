---
name: Context-Aware Discovery
description: An evidence-led interface for inspecting deterministic recommendation behavior.
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
    fontSize: "clamp(2.6rem, 5.3vw, 5.4rem)"
    fontWeight: 700
    lineHeight: 0.94
    letterSpacing: "-0.04em"
  body:
    fontFamily: "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.76rem"
    fontWeight: 750
    lineHeight: 1.5
rounded:
  compact: "4px"
  control: "6px"
  panel: "10px"
spacing:
  compact: "8px"
  control: "12px"
  panel: "28px"
  section: "56px"
components:
  action-control:
    backgroundColor: "{colors.action-blue}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
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

# Design System: Context-Aware Discovery

## Overview

**Creative North Star: "The Evidence Workbench"**

A cool, precise work surface makes ranking cause-and-effect inspectable. It feels closer to an annotated analysis artifact than a consumer recommendation feed: conditions on one side, ranked evidence on the other, with uncertainty and methodology in the same visual hierarchy as the results.

The interface is restrained and dense without becoming clinical. Blue marks action and inference; citron marks measured outputs and synthetic-data status. Familiar controls disappear into the task while ruled lists make rank changes easy to compare.

**Key Characteristics:**
- Cool paper and white working surfaces
- Ink-heavy typography with compact labels
- One action blue and one measured-output citron
- Ruled result strips instead of repeated cards
- Explanations adjacent to outcomes

## Colors

The palette separates action, measured output, and neutral evidence without using color as the sole state cue.

### Primary
- **Action Blue:** selected controls, focus-adjacent emphasis, links, and rank markers.
- **Deep Action Blue:** text emphasis and hover states.

### Secondary
- **Measured Citron:** applied-discovery readouts and synthetic-data labels only.

### Neutral
- **Ink Navy:** headings and primary content.
- **Soft Ink:** supporting explanations and metadata.
- **Cool Paper:** page ground.
- **Surface White:** active work areas and controls.
- **Rules:** boundaries, dividers, and measurement structure.

**The Measured Citron Rule.** Citron labels a measured or declared state; it is not decoration and never replaces a textual label.

## Typography

**Display and Body Font:** platform UI sans-serif stack.

**Character:** Workmanlike and direct. Weight, size, and spacing—not a decorative type pairing—create hierarchy.

### Hierarchy
- **Display:** bold, tightly tracked, and used only for the page thesis.
- **Headline:** 1.36–1.5rem bold for major workbench sections.
- **Title:** 1.0–1.14rem bold for controls and venue names.
- **Body:** 1rem base with explanatory copy generally limited to about 70 characters.
- **Label:** 0.62–0.76rem with strong weight for categories, metadata, and controls.

**The Plain-Language Rule.** Technical measurements may be compact, but every result first receives a readable reason.

## Layout

The desktop workbench uses an approximately 29/71 split: persistent conditions and signals at left, ranked evidence at right. The shell reaches 1380px with 32px outer gutters. At 900px the workbench becomes one column, preserving controls before results. At 560px padding tightens, readouts become horizontal, and score details move to a two-column grid. Type remains fixed except for the page title.

## Elevation & Depth

The system is flat by default. One soft, offset ambient shadow lifts the complete workbench from the cool paper; internal hierarchy uses tonal layers and one-pixel rules rather than nested elevation.

**The One Work Surface Rule.** Individual recommendations are ruled rows, never separately elevated cards.

## Shapes

Corners are compact and functional: 4px for small labels, 6px for controls and readouts, 10px for explanatory panels. Rules are one pixel. The asymmetrical brand mark is the only deliberately unusual silhouette.

## Components

### Action controls
- **Shape:** compact 6px corners and generous keyboard/touch targets.
- **Selected:** white text on Action Blue plus native radio semantics.
- **Focus:** three-pixel visible blue outline offset from the control.
- **Disabled:** cool neutral fill and muted ink.

### Inputs
- **Style:** white field, dark rule, 46px minimum height, visible label.
- **Focus:** the shared high-contrast outline.

### Result list
- **Structure:** rank marker, venue/category, final score, plain-language reason, description, then optional breakdown.
- **Separation:** one-pixel horizontal rules; no per-result shadows.
- **Details:** native disclosure behavior with a four-column score grid, two columns on mobile.

### Status panels
- **Loading:** content-shaped skeleton rows.
- **Error:** named problem, recovery instruction, and retry action.
- **Neutral fallback:** citron-tinted panel with explicit limited-history language.

## Do's and Don'ts

### Do:
- **Do** keep user intent, confidence, and output visible in the same viewport where practical.
- **Do** label synthetic data and uncertain inference in text.
- **Do** preserve native semantics and visible focus.
- **Do** use ruled rows for ranked, comparable content.

### Don't:
- **Don't** use entropy as identity, personality, or intent language.
- **Don't** scatter citron as decorative accent.
- **Don't** nest cards or elevate each result independently.
- **Don't** hide critical explanations behind hover or color alone.
