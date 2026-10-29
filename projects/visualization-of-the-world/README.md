# visualization-of-the-world

Data research for a later visualization of the world (how people live: where, in what, with whom).

**Phase 1 (current) = research only.** No web pages, dashboards or charts yet. The output of this phase is a set of sourced, reproducible datasets and short reports that a visualization can be built on in a later phase.

## Layout
- `research/<topic>/` - one folder per research topic, each with its own README, `sources.csv`, `data/`, `scripts/`, `reports/`.
- `research/poland-demography-housing/` - Poland: population by place class, housing, etc. (first topic).
- `design/` - design system for the later site: tokens (colour, type, space, motion), components and a style guide (`design/style-guide.html`, rules in `design/README.md`).

## Principles
- Every number has a source (see `CLAUDE.md`).
- Primary sources (national statistical offices, Eurostat, UN, OECD, World Bank) first; articles only for interpretation.
- Missing data stays missing; nothing is silently estimated.
