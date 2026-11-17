# Roadmap: Artyści dla szkół

> **DRAFT written by an agent from the README and the M0 issues, not from the owner's decision log.**
> Edit it before merging: story ids (`US-…`), scope and order are proposals. The planner
> (`agent/planner.py`) turns unplanned stories into issues, at most 4 per run, earliest milestone first,
> and only when fewer than 2 tasks are queued. Nothing outside this file is ever planned.
> Format: `## M<n> title`, then `- US-<id>: title (depends: US-<id>, ...)`.

## M0 Foundation
- US-0.1: Project skeleton and agent conventions
- US-0.11: Security baseline and structured logging
- US-0.12: Dev instance on pirx

## M1 Accounts and artist profiles
- US-1.1: Artist registration, e-mail login and e-mail confirmation (depends: US-0.1)
- US-1.2: Institution registration (school or other institution) with a verification state (depends: US-1.1)
- US-1.3: Artist profile editor: bio, categories, regions, photos and video (depends: US-1.1)
- US-1.4: Generated public artist page with a stable URL and Polish SEO basics (depends: US-1.3)
- US-1.5: AI-assisted profile draft from the artist's own marketing materials, with the cost cap (depends: US-1.3)
- US-1.6: Admin moderation: approve or hide artist and institution profiles (depends: US-1.2, US-1.4)

## M2 Catalog and contact
- US-2.1: Searchable artist catalog: filters by category and region, pagination (depends: US-1.4)
- US-2.2: Inquiry from an institution to an artist, with e-mail notification (depends: US-1.2, US-2.1)
- US-2.3: Artist inbox: answer or decline an inquiry (depends: US-2.2)
- US-2.4: Notices posted by institutions that artists can answer (depends: US-1.2, US-2.3)

## M3 Trust and quality
- US-3.1: Reports and abuse handling for profiles, inquiries and notices (depends: US-2.4)
- US-3.2: Reviews and ratings after a completed visit (depends: US-2.3)
- US-3.3: Quality checks on profiles: completeness score and prompts to improve (depends: US-1.4)
- US-3.4: Analytics dashboard for the owner from the events foundation (depends: US-2.3)
