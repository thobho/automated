# Roadmap: Artyści dla szkół

> **Owner-approved plan** (decided 2026-11-11, recovered into this repo 2026-11-17). Replaces the agent-written draft.
>
> **For the planner and every builder:** each story id below is defined in [docs/STORIES.md](docs/STORIES.md)
> (search the id, e.g. `US-2.5`) with its acceptance criteria and the decisions taken with it, in Polish.
> Turn those criteria into the issue's Given/When/Then; do not invent scope. A part id (`US-2.5a`) takes the
> subset of the parent story described in its title. [docs/DECISIONS.md](docs/DECISIONS.md) wins when the two
> differ: hosting is undecided and code stays provider-neutral (D91); pirx runs in light mode until its RAM
> upgrade (D87: Chromium, Lighthouse, axe and screenshots run in CI only); AI only through `apps/profiles/ai/`
> and OpenRouter with the cost cap (D46, D59, D63). US-0.13 is the hosting comparison task that D91 asks for.
>
> Format for `agent/planner.py`: `## M<n> title`, then `- US-<id>: title (depends: US-<id>, ...)`.

## M0 Foundation (done: T01-T09)
- US-0.1: Project skeleton and agent conventions
- US-0.11: Agent conventions in CLAUDE.md, PR and task templates
- US-0.2: Local environment with Compose lite and full
- US-0.3: CI pipeline in GitHub Actions
- US-0.6: Background jobs and scheduler (Procrastinate)
- US-0.7: File storage behind the S3 interface, separate media origin
- US-0.10: AI adapter (OpenRouter) with cost cap
- US-0.12: Dev instance on pirx
- US-10.1: Event catalog
- US-10.2: Event collection on the server and cookie-free visits
- US-10.6: Contract tests for key events

## M1 Artist has a page (pirx)
- US-8.1: Versioned legal documents and recorded acceptance (texts come from the owner's lawyer, D30) (depends: US-0.1)
- US-8.8: Only essential cookies, enforced by a test (D32) (depends: US-0.1)
- US-1.3: E-mail login with link and 6-digit code, sessions and rate limits (D1) (depends: US-0.1)
- US-1.1: Artist registration and e-mail confirmation (depends: US-1.3, US-8.1)
- US-1.2: Institution registration with RSPO suggestions (depends: US-1.3, US-8.1)
- US-1.5: Roles and permissions with a permission-matrix test (depends: US-1.1, US-1.2)
- US-1.4: Institution verification: RSPO CSV import and manual approval (D3) (depends: US-1.2)
- US-1.6: Account settings and e-mail change (depends: US-1.1)
- US-2.1: Artist profile basics: type, name, region, audiences (D2) (depends: US-1.1)
- US-2.9: Offers and repertoire (depends: US-2.1)
- US-8.2: Artist statements: child-protection standards, rights to materials, image consent, billing form, insurance (D4, D6, D7) (depends: US-2.1)
- US-2.3a: Artist materials, part 1: photos, PDF text, YouTube and Vimeo links, school questionnaire, malware scan (D8) (depends: US-2.1, US-0.7)
- US-2.3b: Artist materials, part 2: video and audio upload with ffmpeg conversion and resumable uploads (D8) (depends: US-2.3a)
- US-2.2: Import from the artist's own website with SSRF protection and data scrubbing (D4) (depends: US-2.1)
- US-2.4: Asset quality checks and flags (resolution, stock, screenshot, poster, video frames) (depends: US-2.3a)
- US-11.1: Generator versioning and generation registry (depends: US-0.10)
- US-2.5a: AI generation, part 1: profile JSON schema and background generation job (D5, D59) (depends: US-2.2, US-2.3a, US-2.4, US-2.9, US-11.1)
- US-2.5b: AI generation, part 2: validator of hard rules (depends: US-2.5a)
- US-2.5c: AI generation, part 3: automatic repair loop and admin review fallback (depends: US-2.5b)
- US-3.1: Public profile template (premium layout, sections, hidden empty sections) (depends: US-2.9)
- US-3.2: Four themes with WCAG AA contrast test (depends: US-3.1)
- US-2.6: Preview, field editing with locks, section regeneration, versions (depends: US-2.5c, US-3.1)
- US-2.7: Missing items as a task list with completeness score (depends: US-2.5c)
- US-2.8: Publication and withdrawal, stable profile URL (D6) (depends: US-2.6, US-8.2)
- US-3.3: Mobile layout and performance targets (depends: US-3.1)
- US-3.6: Accessibility (depends: US-3.1)
- US-3.4: Search engine visibility: server rendering, Open Graph, schema.org, sitemap (depends: US-2.8)
- US-3.7: Private preview link and sharing (depends: US-2.8)
- US-11.2: Generator test set with expectations (synthetic and consented data only, D12) (depends: US-11.1)
- US-11.3a: Automatic evaluation, part 1: validator results and AI reviewer with the 6-dimension rubric (depends: US-11.2, US-2.5c)
- US-11.3b: Automatic evaluation, part 2: page metrics and screenshot review in CI (depends: US-11.3a, US-3.3, US-3.6)
- US-11.4: Version comparison and quality gate (D13, D14) (depends: US-11.3b)
- US-11.7: Error catalog turned into rules and regression cases (depends: US-11.3a)
- US-3.8: Page quality standard enforced before publication is offered (depends: US-11.3b)

## M2 School finds and asks (pirx)
- US-4.6: Closed dictionaries managed by the admin (D17) (depends: US-1.5)
- US-4.1: Catalog list and cards (D15) (depends: US-2.8, US-4.6)
- US-4.2: Filters in the URL and an empty-results path to notices (depends: US-4.1)
- US-4.3: Polish text search (depends: US-4.1)
- US-4.4: Result ordering without paid boosts (D16) (depends: US-4.1)
- US-4.5: Region and category pages with indexing threshold (D18) (depends: US-4.2)
- US-4.7: Catalog performance target (depends: US-4.2, US-4.3)
- US-7.5: Notification queue, retries, idempotency and send log (depends: US-0.6)
- US-7.2: E-mail templates (depends: US-7.5)
- US-7.1: Notification catalog with triggers (D28, D29) (depends: US-7.2)
- US-5.1: Inquiry form with draft kept across e-mail confirmation (depends: US-1.2, US-4.1)
- US-5.2: Send one inquiry to up to 3 artists and reveal contacts (D9, D19) (depends: US-5.1)
- US-3.5: "Check date" button opening the inquiry form (depends: US-5.1)
- US-5.3: Artist inbox and statuses (depends: US-5.2, US-7.1)
- US-5.4: Offer or decline with gross price and billing form (D21) (depends: US-5.3)
- US-5.5: Institution decision and side-by-side offers (D20) (depends: US-5.4)
- US-5.6: Message thread with grouped e-mails (D27) (depends: US-5.3)
- US-5.7: Reminders, expiry and event confirmation (D22) (depends: US-5.5)
- US-5.8: Cancellation (depends: US-5.5)
- US-5.9: Anti-spam limits and spam reports (depends: US-5.2)
- US-7.3: Notification preferences and one-click unsubscribe (depends: US-7.1)
- US-7.6: In-app notifications (depends: US-7.1)

## M3 School posts a notice (pirx)
- US-6.1: Create a notice (verified institutions only, D23) (depends: US-1.4, US-4.6)
- US-6.2: Automatic content checks and flags (depends: US-6.1)
- US-6.3: Artist matching with recorded match reasons (depends: US-6.1, US-4.4)
- US-6.4: Notify up to 30 best-matched artists (D24) (depends: US-6.3, US-7.1)
- US-6.5: Notice board, public summary without the institution's name (D25) (depends: US-6.3)
- US-6.6: Artist applies with an offer (depends: US-6.5, US-5.4)
- US-6.7: Compare and choose, creating an accepted inquiry (depends: US-6.6, US-5.5)
- US-6.8: Closing and one extension (depends: US-6.6)
- US-6.9: Visibility rules for notices (depends: US-6.5)

## M4 Ready for the pilot (pirx)
- US-9.1: Admin access with TOTP and audit log (D34, D35) (depends: US-1.5)
- US-9.2: Admin dashboard with queues (depends: US-9.1, US-2.5c)
- US-9.3: Profile review with validator and reviewer reports (depends: US-9.2, US-11.3a)
- US-8.5: Content reports with reasons to authors (DSA) (depends: US-9.1)
- US-9.4: Moderation of reports and notices (depends: US-9.2, US-8.5, US-6.2)
- US-9.5: Institution verification and RSPO import in the panel (depends: US-9.1, US-1.4)
- US-8.3: Artist verification checklist and badge (D31) (depends: US-9.1, US-8.2)
- US-9.6: Artist verification in the panel (depends: US-9.1, US-8.3)
- US-9.7: Users and blocks (depends: US-9.1)
- US-9.8: Read-only view of inquiries and notices (D36) (depends: US-9.1, US-5.3)
- US-8.4: Document pack PDF for the school (depends: US-5.5, US-8.3)
- US-8.6: Data export and account deletion (D33) (depends: US-1.6)
- US-8.7: Retention and minimization jobs (depends: US-0.6)
- US-10.3: Pilot dashboard with thresholds and funnels (depends: US-9.1, US-5.7, US-6.7)
- US-10.4: Surveys: artists' willingness to pay and institutions' satisfaction (D40) (depends: US-5.7)
- US-10.5: CSV export without personal data (depends: US-10.3)
- US-11.5: Production signals report (depends: US-11.1, US-2.6)
- US-11.6: Human rating and blind comparison in the panel (depends: US-9.1, US-11.4)

## M5 Hosting and launch (E0b)
- US-0.13: Hosting comparison and decision request for the owner (D91) (depends: US-0.12)
- US-0.4: Infrastructure as code for the chosen hosting (depends: US-0.13)
- US-0.5: Deployment and rollback (depends: US-0.4)
- US-0.8: Logs, health checks and alarms (depends: US-0.5)
- US-0.9: Backups, restore drill and security patching (D64) (depends: US-0.5)
- US-7.4: E-mail deliverability: SPF, DKIM, DMARC, bounces (depends: US-0.5, US-7.1)

## M6 After the pilot
- US-11.8: Improver agent proposing generator changes as PRs (D14) (depends: US-11.4, US-11.5)
