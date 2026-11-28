# Security

Target: **OWASP ASVS 5.0.0, level 1**, plus the level 2 items chosen in D61 (listed below).
User files are served from a separate origin (D62, built in T06). Baseline set up in T04.

## Threat model (one page)

**Users**
- *Anonymous visitors* (parents, teachers, the public): read artists' pages and the catalog.
- *Artists*: manage their own page, offers and answers to inquiries and notices.
- *Institutions* (schools, cultural centres): send inquiries, post notices.
- *Staff / admins*: moderate content and accounts (`/django-admin/`, later `adminpanel`, 2FA in E9).

**Assets**
- Personal data (GDPR): names, e-mail addresses, phone numbers, institution contacts, messages.
- Accounts and sessions (takeover means impersonating an artist or a school).
- Uploaded files: photos, documents (T06, E2).
- Integrity of public pages and the catalog (defacement, spam, scams aimed at schools).
- Secrets: `DJANGO_SECRET_KEY`, database and SMTP credentials, `OPENROUTER_API_KEY` (env only,
  never in the repo).
- AI budget: the OpenRouter balance (D63).

**Trust boundaries**
1. Browser → web app (internet). Everything from the browser is untrusted: validated in forms and
   services, CSRF-checked, escaped on output, framed by a strict CSP.
2. Web app → PostgreSQL, SMTP, object storage (private network; credentials from env).
3. Web app → user-files origin (D62): uploaded content never runs on the app's origin.
4. Worker (Procrastinate) → same database; jobs carry ids, not personal data.
5. Logs → host log collector: JSON on stdout without e-mails, full IPs, cookies or secrets.
6. Web app / worker → OpenRouter → model providers (internet, T07). Only artists' marketing
   materials, scrubbed of e-mails, phones, IBANs and listed names (D59); only ZDR endpoints
   that do not collect data, from an allowlist; the user is an HMAC pseudonym.

**Main threats and controls**

| Threat | Control |
| --- | --- |
| XSS / content injection | Django autoescape; CSP without `unsafe-inline`/`unsafe-eval`; HTMX with `allowEval: false`, `allowScriptTags: false` |
| CSRF (also via HTMX) | `CsrfViewMiddleware` on all unsafe methods; HTMX sends `X-CSRFToken`; cookies `SameSite=Lax` |
| Clickjacking | `frame-ancestors 'none'` + `X-Frame-Options: DENY` |
| Session theft | `HttpOnly`, `Secure` + `__Host-` cookies in prod, HSTS, SSL redirect |
| Credential stuffing / brute force | no passwords (D1); 6-digit codes lock after 5 failures per e-mail for 15 min; login e-mails limited to 5/h per address and 20/h per IP; counters in PostgreSQL (`apps/accounts/throttling.py`, D96) |
| Malicious uploads | separate origin, type/size checks (T06, E2) |
| Data leak through logs | redaction in `apps/core/logs.py`, pseudonymised user ids, no query strings |
| Account enumeration, spam | the login page answers identically for known, unknown and inactive addresses (also when rate-limited) and only active users get e-mail (T12); E2+ moderation |
| Personal data leaking to AI providers | `apps/profiles/ai`: scrubber before every call, `data_collection: deny` + `zdr: true`, provider allowlist, no prompt text stored or logged |
| Images leaking to AI providers (D59) | an image part is refused unless the caller passes `allow_images=True`; PNG/JPEG sniffed from bytes, 3 MB and 4 images per call, each counted at 4,000 tokens in the cost plan (per-call and daily caps hold); images never logged or stored in `AICall`; page screenshots are sent only for `origin: synthetic` test-set packages (`apps/quality/screenshots.py`), never photos or pages of real artists; screenshots stay in the output folder, not in git or public storage (T44) |
| Disputed or altered legal consent | `apps/trust`: immutable versioned documents, acceptance rows with version + time (PROTECT), consent only to the versions the page showed, re-acceptance gate after material changes |
| Disputed or altered artist statements (US-8.2) | `apps/trust`: append-only `ArtistStatement` rows (model and queryset refuse edits and deletes; withdrawal is a row) with the wording version and an aware time; statements only on the version the page showed (`StaleWording`); artist-only view; shown as "Oświadczenie artysty", never as a check by the service (D31) |
| Runaway AI cost (bug, loop, abuse) | per-call and daily caps checked before sending (`AICapExceeded`), `AI_KILL_SWITCH`, low-limit key |
| Untraceable or silently changed generator (US-11.1, D13, D14) | `apps/quality`: every component version is hashed and checked against the checked-in `components.json` (test fails on a change without a version bump); append-only `Generation` and `GeneratorComponentVersion` rows (model and queryset refuse edits and deletes once finished); the input is kept only as a SHA-256 fingerprint (D107), never a copy of the materials; no prompt or reply text in `AICall`, `Generation` or `generation_show`; admin read-only and staff-only |
| Test artists or real people's data in production through the generator test set (US-11.2, D12, D57, D118) | `apps/quality/testset.py`: `QUALITY_LAB_ENABLED` is off by default and on only in the dev, test and pirx settings; with it off `testset_check`, `testset_load` and `load_package` refuse before any row is created (tests for both commands and for prod, pirx, dev and test settings); packages are `synthetic` only: `origin: consented` is refused because the service has no consent record for the test set; `check_package` fails a package whose text changes under the project scrubber (e-mail, phone, account, PESEL) or holds a URL host other than `example.invalid` and YouTube/Vimeo; no network at load (link titles come from the package); photos are drawn at load time, no binary files in git |
| Leaked key, prompt text or unreviewed real data through the automatic evaluation, or a review that hides its own failure (US-11.3A, D13, D59, D63, D120) | `apps/quality/evaluation.py`, `reviewer.py`: `evaluate_testset` refuses with `QUALITY_LAB_ENABLED` off (no AI call) and for `consented` packages; all AI calls go through `apps/profiles/ai` (kill switch, per-call and daily caps; a cap stops the run as `niekompletny`, no further call); the reviewer gets only the source input and the profile without `claims_audit` (tested), its reply is schema-checked and a bad reply gives `brak oceny` with the reason, never an invented score; stored reasons and the JSON report hold no prompt, instruction or reply text; `--key-file` is read like in `ai_smoke` and never printed or written (tested); runs and package rows are append-only and the admin is read-only and staff-only |
| A generator error fixed without a lasting check, or real people's data in regression cases (US-11.7, D12, D13, D57) | `apps/quality/catalog.py`: every catalog entry names a validator rule or an instruction anchor and at least one case; `error_catalog_check` and a pytest test fail on an unknown rule, a missing anchor, a fixture the validator does not flag, a missing case or an expectation the package lacks; cases may use only `origin: synthetic` packages; the catalog, its schema and the fixtures are a hashed component (a change needs a version bump, human-approved PR); no network, no AI call |
| Invented facts, foreign photos or links, and promises in a generated profile (US-2.5B, D113) | `apps/profiles/validator.py`: deterministic hard rules (numbers and prices only from the artist's sources, testimonials verbatim, photo, video and offer ids only of the artist's ready materials, YouTube/Vimeo links only the artist's own, no process language or promises, fact and length limits); no AI in the validator; a hard finding leaves the run at `do przeglądu`, never `gotowa`; findings hold a path, a message and a value cut to 120 characters |
| Unchecked generated content shown or published, or a repair loop that runs away (US-2.5C, D114) | `apps/profiles/repair.py`: at most 2 repair rounds, every call through `apps/profiles/ai` (per-call and daily caps, kill switch), the repair prompt holds rule, path and message plus the already-scrubbed input, never the offending value; a cap, an invalid reply or a provider error stops the loop and the run goes to `do przeglądu`, never `gotowa`; the artist panel shows only „Profil czeka na przegląd”; closing a review is staff-only (admin permission `quality.view_reviewqueue`), needs a note, and writes an append-only `GenerationReview` audit row (staff user, time, decision) |
| Another artist's missing items shown, or generator text injected into the list (US-2.7) | `apps/profiles/completeness.py`: no id in the URL, `role_required("artist")`, the list is computed only from the signed-in artist's own data; a held (`do przeglądu`) run's gaps are never read; an unknown gap shows the generator's text cut to 200 characters, auto-escaped, with no link |
| Unwanted or unsafe input to the profile generator (US-2.5A, D59) | `apps/profiles/inputs.py`: only `ready` materials and only with a current „Prawa do materiałów” statement; ids, flags and scrubbed text, never file bytes, names, keys or URLs; the AI is called only through `apps/profiles/ai` (cost cap, kill switch); a reply is accepted only if it matches the JSON Schema, and failure reasons hold JSON paths, never reply text; the status views carry no id, are artist-only and show the artist's own latest run |

## What is in place (T04)

- **Headers** (every response): `Content-Security-Policy` (see `CSP_DIRECTIVES` in
  `config/settings/base.py`; per-request nonce as `{{ csp_nonce }}` for the rare inline script),
  `Permissions-Policy` (camera, microphone, geolocation, payment, usb, sensors, topics off),
  `Referrer-Policy: strict-origin-when-cross-origin`, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Cross-Origin-Opener-Policy: same-origin`, `X-Request-ID`.
- **Prod only**: `Strict-Transport-Security: max-age=31536000; includeSubDomains`, redirect to
  HTTPS (except `/healthz`, `/readyz`), cookies `__Host-sessionid` / `__Host-csrftoken` with
  `Secure`. `manage.py check --deploy --fail-level WARNING` is clean (tested in CI).
- **HSTS preload** is off and its deploy warning (`security.W021`) silenced: once a domain is on
  the browsers' preload list it is hard to remove, so the owner turns it on
  (`DJANGO_SECURE_HSTS_PRELOAD=true`) when the domain is final.
- **Proxy**: `X-Forwarded-Proto` is trusted only with `DJANGO_TRUST_X_FORWARDED_PROTO=true`, and
  client IPs come from `REMOTE_ADDR` only, until hosting is decided (D91).
- **Logging**: one JSON object per line on stdout, same config in dev and prod. Fields: `ts`
  (UTC), `level`, `logger`, `msg`, `request_id`, `user` (HMAC pseudonym or `-`), and for the
  `access` logger `method`, `path` (no query string), `status`, `duration_ms`, `ip` (IPv4 /24,
  IPv6 /48). E-mails, `key=value` secrets (password, token, cookie, session, csrf, api key...),
  auth headers and IP host parts are redacted from messages and tracebacks.
- **Log inventory**: web and worker write only to stdout/stderr; nothing is written to files.
  `django.server` (runserver) is muted because its lines contain query strings.
- **Uploads (T06)**: size limits per kind, content type sniffed from magic bytes, random
  keys, EXIF/GPS stripped from images, private files only through short-lived signed URLs,
  public files on a separate origin (`MEDIA_PUBLIC_BASE_URL`, required in prod). **Malware
  scanning (T24, US-2.3A)**: every artist material and offer poster is scanned by a `media`
  job (`apps/core/scanning.py`, ClamAV `clamd` over INSTREAM) before it counts; infected files
  are deleted. Prod refuses to load with `MALWARE_SCANNER` other than `clamd`. **Open owner
  decision:** clamd needs ~1 GB of RAM, which pirx in light mode does not have (D87), so pirx
  and dev run `MALWARE_SCANNER=none` (files logged as `upload_unscanned`); a host with clamd is
  needed before uploads from real users go live.
- **Artist materials (T24, US-2.3A)**: the materials step and questionnaire are artist-only
  with complete basics (permission matrix). Photos and PDFs use the T06 upload path (sniffed
  type, size limits, EXIF stripped, random key, private storage, signed URLs only) and the
  per-artist counts (40 photos, 10 PDFs) are checked before storing and again under a row lock.
  A material counts only when `ready` (scanned clean). Deleting looks the material up with the
  owner in the query (foreign id = 404) and removes the file after the commit. Video links:
  the URL is parsed locally to a YouTube/Vimeo id and only the fixed oEmbed endpoints
  (`https://www.youtube.com/oembed`, `https://vimeo.com/api/oembed.json`) are called, with the
  canonical URL rebuilt from the id, a 5 s timeout, no redirects and a 64 KB answer limit:
  any other host, port or user-info is refused without a request (no SSRF). PDF text is
  extracted by `pypdf` (pure Python, no external program) within page, character and time
  limits; encrypted and broken PDFs end as a status. File names are stored cleaned and
  rendered autoescaped. Logs carry a pseudonymised user and the material id only.
- **Video and audio, resumable uploads (T25, US-2.3B)**: an upload session is created only
  after the kind, the declared size (500 MB video, 50 MB audio) and the remaining count (5 / 10)
  are checked, the count again under the artist row lock, and again when the file is completed.
  Sessions are random UUIDs looked up with the owner in the query (another artist's = 404,
  institution = 403, CSRF on every POST), expire after `UPLOAD_SESSION_TTL_HOURS` and are
  deleted with their data by an hourly job; an artist has at most as many open sessions of a
  kind as its limit (disk use is bounded). A chunk must start at the received offset, be at most
  `UPLOAD_CHUNK_BYTES` and not reach past the declared size, so the server never stores more
  than declared; the first chunk's magic bytes must already be an allowed type and the full
  file is sniffed again by `store_upload`. Chunks are written to `UPLOAD_TEMP_DIR` (mode 0700,
  file names from the UUID only, never a served storage). **ffmpeg** (`apps/core/ffmpeg.py`)
  runs only after a clean scan, as a subprocess with an argument list (no shell, `--` before
  the input for ffprobe, stdin closed), a wall-clock timeout (`FFMPEG_TIMEOUT_SECONDS`,
  `FFPROBE_TIMEOUT_SECONDS`) and an address-space limit (`FFMPEG_MEMORY_MB`, `RLIMIT_AS`), with
  input and output in a fresh temporary directory; a timeout, crash or bad file ends as a
  `rejected` material with a readable message and the files deleted, never as a stuck job.
  **Quality checks (T27, US-2.4, D59)** run locally on the stored file and on the original's
  metadata, read in `store_upload` before the stripping (`apps/core/imagemeta.py`: bounded,
  never raises, no XML parser, only byte-pattern search in the metadata segments). No raw
  metadata is stored, only the derived flags and a "had camera data" bit; no AI or external
  service sees a photo. Video frames come from the same ffmpeg wrapper (limits above), are private
  and shown through signed URLs; a frame is looked up with the owner in the query (foreign id =
  404, POST only, in the permission matrix). Converted MP4s and thumbnails are private and shown only through signed URLs. CSP gains
  `media-src 'self' blob:` so the page can read a chosen video's duration locally. **Owner
  note:** clamd scans streams only up to `StreamMaxLength` (default 25 MB); scanning 500 MB
  videos needs that raised on the future host, with the RAM decision (D87).
- **Import from the artist's website, SSRF (T26, US-2.2, STORIES "Import ze strony")**: done.
  All user-given URLs are fetched only by `apps/core/safefetch.py`: `http`/`https` only, no
  user-info, default ports only; the host is resolved once and every address must be public
  (loopback, private, link-local incl. `169.254.169.254`, shared `100.64/10`, multicast,
  reserved, unspecified, documentation and benchmarking ranges, IPv6 unique-local, link-local,
  Teredo, and IPv4 wrapped in IPv4-mapped, 6to4 or NAT64 addresses are refused before any
  connection); the socket connects to the checked address (no second DNS lookup, so no DNS
  rebinding window) with the original name for `Host`, SNI and the certificate check; each of
  at most 3 redirects is checked the same way and, after the first page, must stay on the site's
  host. One hard deadline per request (a watchdog shuts the socket, so drip-feeding cannot hold
  the job), a byte cap per request, 20 MB per import, `Accept-Encoding: identity` (no
  decompression bombs), only HTML parsed with the stdlib parser, JavaScript never run. Table
  test with the forbidden-address list in `apps/core/tests/test_safefetch.py`. The dev-only
  `SAFE_FETCH_ALLOW_LOOPBACK` (loopback on any port, for a local synthetic site) makes the
  hosted settings (prod, pirx) refuse to load. The import needs the rights checkbox, which
  records the `material_rights` statement (D4, D104). Imported text is scrubbed before it is
  stored (D59: e-mails, phones, IBAN/NRB, PESEL and ID card numbers with valid checksums, postal
  addresses); contact data found is kept on the import for the artist only, never published
  and never sent to AI. Photos go through the normal upload path (sniffed type, EXIF stripped,
  private storage, malware scan, 40-photo limit). Logs and events carry the import id, counts
  and error codes, never the URL. One running import per artist, at most 10 per day.
- **Legal documents (T10)**: bodies are plain text from staff, rendered autoescaped
  (`linebreaks`), never as HTML. Published versions cannot be changed or deleted (model,
  queryset and admin all refuse). The re-acceptance gate redirects only to a fixed URL; the
  `next` target is checked with `url_has_allowed_host_and_scheme`; the accept form is a CSRF-
  protected POST.
- **E-mail login (T12, D1, D96)**: no passwords. `/logowanie/` answers identically whether or
  not the address has an active account; only active users get an e-mail. One challenge is a
  `secrets.token_urlsafe(32)` link token plus a 6-digit code, valid 15 minutes, single use
  (using either consumes it; a newer e-mail closes the older one). Stored as SHA-256 (token)
  and HMAC-SHA256 with SECRET_KEY and a per-row salt (code); codes compared in constant time.
  The e-mail job receives only the user id and site origin and creates the challenge itself,
  so codes and tokens never reach the jobs table. Limits: 5 failed codes per e-mail lock code
  login for 15 minutes; 5 login e-mails per hour per address, 20 per IP (IPv6: per /64).
  Sessions: database, key rotated on login, 30 days idle expiry; logout is a CSRF-protected
  POST that deletes the session row and sends `Clear-Site-Data: "cookies", "storage"`.
- **Artist registration (T13, US-1.1, D97)**: `/rejestracja/artysta/` gives a valid form the
  same status and text for a new and an already registered address; for an existing one
  nothing is created or recorded and the owner gets a normal login e-mail. Registration
  checks the login e-mail limits *before* creating anything, so it cannot be used to create
  accounts beyond 5/h per address and 20/h per IP. New accounts have no password and stay
  unconfirmed (`email_confirmed_at` empty) until the first successful link or code login. The
  optional `next` in the e-mailed link is a local path only (`login_link()` drops anything
  else, and the login views check it again with `url_has_allowed_host_and_scheme`). Logs and
  events carry a pseudonymised user only, never the e-mail or the name.
- **Institution registration (T14, US-1.2, D98)**: `/rejestracja/placowka/` follows the artist
  flow above (same answer for new and existing addresses, limits checked first, no password,
  unconfirmed until the first login). A chosen RSPO suggestion is sent as its number only; the
  server copies name, type, locality and voivodeship from `RspoEntry`, so a tampered POST
  cannot rename a registry institution. A second account for an RSPO number that already has
  an institution is linked with `needs_review=True` for the admin and gets no access to the
  other members' data (inquiries in M2 are scoped to the member, not the institution). The
  suggestion endpoint `/rejestracja/placowka/rspo/` is anonymous, GET only, read-only, returns
  at most 10 public registry rows and nothing for fewer than 3 characters (query capped at 200
  characters). Events hold the institution type and two booleans only, no names or e-mails.
- **Institution verification (T16, US-1.4, D3, D100)**: "zweryfikowana" only through
  `institutions.services.verify()`, by the domain rule or by staff. Domain rule: a confirmed,
  active member's e-mail domain must equal the RSPO e-mail domain exactly (case-insensitive, no
  subdomain or parent-domain guessing); free mailbox domains (`PUBLIC_MAILBOX_DOMAINS`: gmail.com,
  wp.pl, o2.pl, onet.pl, interia.pl, op.pl, outlook.com, ...) never verify, because anyone can
  get an address there. Manual approval is the Django admin action "Zatwierdź placówkę"
  (`/django-admin/` is staff only; the action also needs the change permission) and records
  the admin. The verification fields are read-only in the admin, so the event cannot be
  skipped. The RSPO import is a server command (`manage.py import_rspo <path>`), not a web
  upload; it keeps only the domain of the registry's e-mail address (not the address, not the
  director's name) and never logs row content, only counts. `institution_verified` carries the
  method only (D39).
- **Roles and access control (T15, US-1.5, D37, D99)**: one role per account, derived from data
  (`apps/accounts/roles.py`: `admin` = `is_staff`/`is_superuser`, `artist` = has `Artist`,
  `institution` = has `InstitutionMember`; contradictory data fails closed). Views declare their
  roles with `role_required(...)` / `RoleRequiredMixin` (`apps/accounts/permissions.py`):
  anonymous -> login page with a local `next`, wrong role -> 403 (Polish page) and one
  `permission denied` line (pseudonymised user, role, URL name, required role; no e-mail, IP or
  query string). Registration services never add a second role to an existing address, forms
  have no role fields (extra POST fields are ignored), and admin accounts exist only through
  `manage.py create_admin` on the server. The permission matrix
  `apps/accounts/tests/test_permission_matrix.py` checks every URL name for anonymous, artist,
  institution and admin, and fails on a route without a row (excluded by name: `/django-admin/`,
  `/healthz`, `/readyz`; static files are not a URL name). It is part of the pre-pilot security
  gate (D65).
- **Account settings and e-mail change (T17, US-1.6, D101)**: the login e-mail changes only
  after confirmation from the new address, by the same logged-in account. `/konto/email/`
  answers identically for a free and a taken address; a taken address gets nothing and nothing
  changes. The old address always gets a notice without link or code (so its absence tells
  nothing). The new address gets a link token and a 6-digit code made like a login challenge
  (`secrets`, 15 minutes, single use, SHA-256 / salted HMAC, constant-time compare; the job gets
  only the request id). Limits: 5 requests/h per user, 20/h per IP shared with login; 5 wrong
  codes lock code entry for 15 minutes. A link opened by another account is refused (and stays
  valid for its owner). Confirmation sets `email_confirmed_at`, closes open login challenges,
  gives the current session a new key and ends every other session: the session auth hash
  covers the e-mail (`User._get_session_auth_hash`). Until then login works with the old address
  only. Events `email_change_requested`, `email_change_email_sent`, `email_change_notice_sent`,
  `email_change_refused`, `email_change_confirmed`, `email_change_rate_limited` carry a
  pseudonymised user only.
- **Artist profile wizard, step 1 (T21, US-2.1, D102)**: `/artysta/kreator/`,
  `/artysta/profil/dane/` and the later-step placeholders are artist-only (`role_required`; rows
  in the permission matrix). The form edits only the logged-in user's own `Artist` (looked up by
  `request.user`, no id in the URL, so no IDOR); type, voivodeships and audiences are choice
  fields, so tampered values get a 400 form error, and `save_basics()` validates again and saves
  all or nothing. The POST is CSRF-protected; the log line `artist_basics_saved` carries a
  pseudonymised user only, no field values.
- **Offers and posters (T22, US-2.9, D103)**: the offer pages are artist-only and need complete
  basics. Every lookup is `Offer.objects.get(artist=<request.user's artist>, pk=...)`, so another
  artist's offer id and a missing id both give the same 404 and nothing changes (IDOR test);
  institution and admin accounts get 403. Changes are CSRF-protected POSTs (delete only after a
  confirmation page). Title and description are plain text rendered autoescaped (`linebreaksbr`),
  never as HTML. **Posters use the T06 upload path**: `store_upload(kind="photo",
  visibility="private")`, so the type is sniffed from magic bytes (a PDF renamed `.jpg` is
  refused), the 15 MB limit applies (D8), EXIF/GPS is stripped by re-encoding, the key is random
  and the file sits in the private storage; the artist sees it only through a short-lived
  `media.signed_url` (attachment, `nosniff`, sandbox CSP). It becomes public only with
  publication (US-2.8). A rejected upload saves nothing; a replaced or removed poster and a
  deleted offer's poster are deleted from storage after the commit (a storage failure is logged
  as `offer_poster_orphan` without the key). Posters are malware-scanned like materials (T24:
  `poster_status`, an infected poster is deleted). Log lines carry a pseudonymised user and the
  offer id only.
- **Preview editing (T34, US-2.6)**: edit, unlock, regenerate and restore are POST-only, CSRF-protected,
  `role_required("artist")` and act on the logged-in user's own artist (no artist id in any URL; a version
  number of another artist is a 404). Edited text is stored as plain text and rendered escaped. Section
  regeneration goes only through `profiles/ai/` with the cost cap; no prompt or reply text is stored.
- **Page themes (T33, US-3.2)**: the theme switch `POST /panel/podglad/motyw/` is artist-only
  (`role_required`), CSRF-protected and acts on the logged-in user's own artist (no id in the
  URL). The value is checked against the closed `Theme` list (unknown = refused, nothing stored);
  a stored unknown value renders the default. Themes are CSS custom properties in a static file,
  selected by a `data-theme` attribute: no inline style, no external fonts or assets.
- **Artist page template and owner preview (T32, US-3.1, D9, D10, D11)**: `/panel/podglad/`
  is artist-only (`role_required("artist")`, row in the permission matrix: anonymous -> login,
  institution and admin -> 403) and shows only the logged-in user's own artist (no id in the
  URL, so no IDOR). The response is `never_cache` with `X-Robots-Tag: noindex, nofollow` and a
  `noindex` meta tag; nothing is published here. The template renders only `PageContent`
  fields, all autoescaped (a test feeds HTML into every text field); no `|safe`, no inline
  `<script>`, `<style>` or `style=""`, so the strict CSP stays unchanged. **No public contact
  data (D9):** the page has no `mailto:` or `tel:`, only the "Sprawdź termin" anchor to the
  inquiry section. **No external requests (D11):** CSS and fonts are served from `static/`,
  images from the media origin; a YouTube/Vimeo video is a local thumbnail or placeholder plus
  a link (no iframe, nothing requested from the provider before the click). Video links reach
  the page only as `http(s)` URLs (`VideoItem` drops anything else, e.g. `javascript:`; the
  builder uses the canonical URL rebuilt from the provider id, T24). A test scans the rendered
  HTML for inline code and foreign hosts; the Playwright test
  `tests/e2e/test_artist_page.py` checks the same in a browser, including that the browser makes
  no request to another host. No testimonials are imported (D10).
- **The one allowed token in a URL**: the login link `/logowanie/link/?t=<token>` (and, built the
  same way, the e-mail change link `/konto/email/link/?t=<token>`). The token
  is only in the query string, which the access log never contains (path only, `django.server`
  muted); `Referrer-Policy: strict-origin-when-cross-origin` keeps it out of cross-origin
  `Referer` headers. Opening the link (GET) only shows a "Zaloguj" button, so mail scanners
  that fetch links cannot consume it; the POST logs in. The page is `Cache-Control: no-cache,
  no-store` and the token is single use and expires in 15 minutes.

Remediation time frames for vulnerable dependencies (ASVS 15.1.1): critical 7 days, high 30
days, others with the next regular update; dependencies are reviewed at least monthly.

## Private preview links (US-3.7, D121)

`/podglad/<token>/` opens the artist's current page without login, so the token is the only
secret. It is 32 random bytes from `secrets` (43 URL-safe characters), shown once in the answer
to the POST that creates it (no session, no redirect URL, `Cache-Control: no-store`) and stored
only as SHA-256 (`PreviewLink.token_hash`, unique index; a 256-bit random value needs no slow
hash). Valid 7 days, at most 3 active per artist, revocable at once; it stops working when the
page is withdrawn or the account deactivated or deleted, and a token only ever maps to its own
artist. Unknown, expired, revoked and malformed tokens get the site's own 404 page (same body
and headers). Wrong tokens count per client IP in `accounts.throttling` (`preview_ip`,
`PREVIEW_LIMIT_PER_IP`/`PREVIEW_LIMIT_WINDOW`, default 20 per 15 minutes); at the limit the IP
gets 429 and one `preview_rate_limited` log line without token or path. The token never reaches
logs or analytics: `core.logs.redact()` turns `/podglad/<anything>` into `/podglad/[token]`
(access log and `django.request` lines), and visit counting skips `/podglad/`. The page sends
`noindex` (meta and `X-Robots-Tag: noindex, nofollow`), `Cache-Control: no-store` and
`Referrer-Policy: no-referrer`, has no owner controls, shows photos and videos only with a
current rights statement and replaces any e-mail or phone with "[ukryte]" (D9). Behind a
reverse proxy all visitors share one REMOTE_ADDR bucket (as for the login limits, D91).
Creating and revoking are POST-only, CSRF-protected and owner-only (the artist is the logged-in
user; a foreign link id is simply not found).

## Artist statements (US-8.2, D104)

Statements (child protection, rights to materials, image consents, billing form, OC with its
validity date) are **personal data of the artist** and evidence: who declared which wording
version when. They are visible only to the artist (`/artysta/profil/oswiadczenia/`, role check,
403 for others) and read-only to staff in the Django admin. The counted ones appear publicly
only as the "Oświadczenie artysty" badges (kind, billing form, OC date), never the rows.
Logs carry the pseudonymised user and the kind only; the OC reminder job carries the statement
id only, the address is read when the e-mail is sent. Rows are `PROTECT`ed like legal
acceptances, so an artist account cannot be deleted while statements exist.
**Open question for US-8.7 (retention):** how long statements and withdrawals are kept after a
withdrawal or account deletion (proof of what was declared vs. data minimisation).

## Cookies (US-8.8, D32)

The site sets only essential cookies, so no consent banner is needed. The allowlist is
`apps/core/cookies.py` (`essential_cookie_names()`, derived from settings). The test
`apps/core/tests/test_cookies.py` requests every reversible route anonymously and logged in and
fails with the path and cookie name for any other `Set-Cookie`; routes with arguments are listed
in `ROUTES_WITH_ARGUMENTS` there (extend it with new features). A test-only URLconf proves the
check catches a stray cookie. Analytics use no cookies (D38, D39); flash messages use session
storage (`MESSAGE_STORAGE`); there is no language cookie.

| Cookie (prod / dev) | Purpose | Lifetime | Flags |
|---|---|---|---|
| `__Host-sessionid` / `sessionid` | Login session | 30 days idle (`SESSION_COOKIE_AGE`) | HttpOnly, SameSite=Lax, Secure in prod |
| `__Host-csrftoken` / `csrftoken` | CSRF protection | 1 year (Django default) | HttpOnly, SameSite=Lax, Secure in prod |

## ASVS 5.0 level 1 checklist

Status: **done**, **partial** (what is missing), **planned** (task), **n/a** (feature absent).

| ID | Requirement (short) | Status |
| --- | --- | --- |
| 1.2.1 | Context-aware output encoding | done (Django autoescape) |
| 1.2.2 | URL building encodes untrusted data | done (`{% url %}`, `urlencode`) |
| 1.2.3 | Encoding in JS/JSON | done (no inline JS; `json_script` when needed) |
| 1.2.4 | Parameterised queries | done (ORM only, no raw SQL) |
| 1.2.5 | OS command injection | done (T25: the only OS calls are ffmpeg/ffprobe in `apps/core/ffmpeg.py`, argument lists with `shell=False`, binary paths from settings, file names generated by the server) |
| 1.3.1 | Sanitise WYSIWYG HTML | planned (profiles, if rich text is added) |
| 1.3.2 | No `eval()` / dynamic code | done (CSP without `unsafe-eval`, HTMX `allowEval: false`) |
| 1.5.1 | Safe XML parser config | n/a (no XML input) |
| 2.1.1 | Input validation rules documented | planned (per feature, E1+) |
| 2.2.1 | Input validated against business rules | partial (Django forms per feature; T16: RSPO import validates every row, skips invalid ones with a count) |
| 2.2.2 | Validation at a trusted service layer | done by design (`services.py` rule, CLAUDE.md) |
| 2.3.1 | Business flow steps in order | partial (re-acceptance gate before using the app, T10); inquiries, notices planned |
| 3.2.1 | Content not rendered in wrong context | done (nosniff, correct Content-Type, user files on own origin in T06) |
| 3.2.2 | Text rendered safely | done (autoescape; no own JS using `innerHTML`) |
| 3.3.1 | Cookies `Secure` with `__Host-`/`__Secure-` prefix | done (prod) |
| 3.4.1 | HSTS, max-age ≥ 1 year | done (prod) |
| 3.4.2 | CORS origin fixed / allowlisted | done (no CORS headers sent) |
| 3.5.1 | CSRF protection | done (all unsafe methods, HTMX header) |
| 3.5.2 | Preflight not bypassable | n/a (CSRF tokens, not preflight) |
| 3.5.3 | Sensitive actions use POST/PUT/... | done so far (`require_GET`/`require_POST`); per feature |
| 4.1.1 | Content-Type with charset | done (Django default `utf-8`) |
| 4.4.1 | WebSockets over TLS | n/a (no WebSockets) |
| 5.2.1 | File size limits | done for offer posters, photos, PDFs, video and audio (T06 limits, T22, T24; per-artist counts T24; T25: declared size checked before a resumable upload starts, bytes past it refused, ffmpeg time and memory limits) |
| 5.2.2 | File extension and content checked | done for offer posters, photos, PDFs, video and audio (sniffed type, T22, T24; T25: first chunk and full file sniffed, then ffprobe checks container and streams) |
| 5.3.1 | Uploads never executed | done (T06: separate origin, D62; private files are attachments with a sandbox CSP; T24: malware scan with clamd before a file counts, prod refuses no scanner; PDF text read by pure-Python `pypdf`, never an external program) |
| 5.3.2 | Server-generated file paths | done (random keys from `store_upload`, T06; posters T22; materials T24) |
| 6.1.1 | Rate limiting / anti-automation documented | done (this file, `throttling.py`) |
| 6.2.1–6.2.8 | Password rules (length, change, common lists, composition, fields, paste, exact check) | n/a (no passwords: e-mail link + code only, D1; users have unusable passwords. Django-admin staff logins keep Django's password validators until admin TOTP, US-9.1) |
| 6.3.1 | Brute force / stuffing controls | done (T12: 5 failed codes per e-mail lock code login for 15 min, even a correct code; send limits 5/h per address, 20/h per IP; shared in PostgreSQL) |
| 6.3.2 | No default accounts | done (none created; seed users have unusable passwords) |
| 6.4.1 | Initial passwords/codes random, expiring | done (T12: `secrets` link token + 6-digit code, 15 min, single use, only hashes stored, constant-time compare) |
| 6.4.2 | No password hints / secret questions | done (none) |
| 7.2.1 | Session checked on the backend | done (Django sessions) |
| 7.2.2 | Dynamic session tokens | done (Django sessions) |
| 7.2.3 | Tokens from a CSPRNG | done (Django sessions) |
| 7.2.4 | New session on login | done (T12: `django.contrib.auth.login()` rotates the key) |
| 7.4.1 | Logout/expiry ends the session | done (T12: POST logout flushes the DB session; expiry after 30 idle days, activity refreshes it) |
| 7.4.2 | Disabling a user ends their sessions | planned (E1, E9); T17: changing the login e-mail ends all other sessions |
| 8.1.1 | Authorisation rules documented | done (T15: roles and rules in `apps/accounts/roles.py`, per-route table in `apps/accounts/tests/test_permission_matrix.py`, "Roles and access control" above) |
| 8.2.1 | Function-level access control | done (T15: `role_required` / `RoleRequiredMixin`, 403 + log; every route in the permission matrix; `/django-admin/` staff only) |
| 8.2.2 | Data-level access control (IDOR) | per feature: T21's wizard edits only `request.user`'s own artist; T22 offers and T24 materials are looked up with the owner in the query (foreign id = 404, tested) |
| 8.3.1 | Authorisation in the service layer | partial (T15: rule functions `can_create_artist_profile`, `can_create_inquiry`, `can_create_notice`; E5/E6 call them in their services) |
| 9.1.1–9.2.1 | Self-contained tokens (JWT etc.) | n/a (none; Django signed tokens use HMAC) |
| 10.4.1–10.4.5 | OAuth authorisation server | n/a |
| 11.3.1 | No ECB / weak padding | n/a (no own encryption) |
| 11.3.2 | Approved ciphers only | n/a (no own encryption) |
| 11.4.1 | Approved hash functions | done (Django: PBKDF2-SHA256, HMAC-SHA256) |
| 12.1.1 | TLS 1.2+ only | planned (deployment, D91) |
| 12.2.1 | TLS for all external connections | partial (app redirects + HSTS; proxy at deployment, D91) |
| 12.2.2 | Publicly trusted certificates | planned (deployment, D91) |
| 13.4.1 | No `.git` in the deployment | done (`.dockerignore`) |
| 14.2.1 | No sensitive data in URLs | partial (query strings never logged; the login link token is one allowed exception, see "E-mail login"; the preview link token in the path is the other, redacted in logs and kept out of analytics, see "Private preview links") |
| 14.3.1 | Client storage cleared on logout | done (T12: `Clear-Site-Data: "cookies", "storage"`) |
| 15.1.1 | Remediation time frames documented | done (above) |
| 15.2.1 | Components within those time frames | planned (dependency audit in CI) |
| 15.3.1 | Return only needed fields | done so far (health endpoints); per feature |

## Chosen level 2 items (D61)

| ID | Requirement (short) | Status |
| --- | --- | --- |
| 3.3.2 | SameSite per cookie purpose | done (`Lax`) |
| 3.3.3 | `__Host-` prefix | done (prod) |
| 3.3.4 | `HttpOnly` where scripts need no access | done (session and CSRF cookies) |
| 3.4.3 | CSP restricting sources | done |
| 3.4.4 | `X-Content-Type-Options: nosniff` | done |
| 3.4.5 | Referrer policy | done |
| 3.4.6 | `frame-ancestors` | done |
| 3.5.4 | Separate hostnames for separate apps | planned (T06, user files origin) |
| 13.4.2 | Debug off in production | done (`DEBUG = False` in prod) |
| 13.4.4 | No HTTP TRACE | done (views allow GET/HEAD/OPTIONS or POST only) |
| 16.2.1 | Log entries have when/where/who/what | done (ts, logger, request id, user pseudonym) |
| 16.2.2 | UTC timestamps | done |
| 16.2.4 | Common log format | done (JSON lines) |
| 16.2.5 | Sensitive data kept out of logs | done (redaction, pseudonyms) |
| 6.3.7 | Users notified after updates to authentication details | done (T17: an e-mail change request always sends a notice without link or code to the current address; the change needs confirmation from the new one) |
| 6.6 (e-mail as factor) | Out-of-band authenticators; e-mail is not a strong OOB channel | accepted deviation (D1: the e-mail link + code *is* the login factor, no passwords). Mitigations: 15 min single-use codes stored as hashes, 5-failure lock, send limits, a changed login e-mail needs confirmation from the new address by the same logged-in account and ends other sessions (T17); admin TOTP planned (US-9.1) |
| 16.3.1 | Authentication events logged | done (T12: `login_requested`, `login_email_sent`, `login_succeeded`, `login_code_failed`, `login_link_failed`, `login_locked`, `login_rate_limited`, `logout`; T17: `email_change_requested`, `email_change_confirmed`, `email_change_refused`, `email_change_rate_limited`; pseudonymised user, no e-mail, IP, code or token) |
| 16.3.2 | Failed authorisation attempts logged | done (T15: one `permission denied` line per 403 from a permission check) |
| 16.4.1 | Log injection prevented | done (JSON encoding) |
| 16.5.1 | Generic error messages | done (`DEBUG = False` in prod) |
| 8.2.1 (public profile exposure) | Only published pages are reachable; no contact data leaks | done (T39 adds: the search tags and JSON-LD come from the snapshot only and carry no e-mail, phone or address; JSON-LD escapes `<`, `>`, `&` so no `</script>` breakout, meta attributes are autoescaped, the `application/ld+json` block needs no CSP change; `/sitemap.xml` lists `published()` pages only and is revalidated on every request; `/robots.txt` disallows `/panel/`, `/admin/`, `/django-admin/`, `/artysta/`; the preview keeps `noindex` + `X-Robots-Tag`; `SITE_URL` is required in hosted settings so no localhost URL is published) (T36: `/artysci/<slug>/` serves the snapshot of `Artist.objects.published()`; draft, withdrawn and unknown slugs give one identical 404; the snapshot holds everything shown, nothing is read live, so nothing new goes public without a click; photos, videos and links only while the artist's "Prawa do materiałów" statement counts; publication is refused while a name, city, text, offer or photo alt text has an e-mail or phone; slug, state and dates are read-only in the Django admin; no upload file names, no inquiry data; deactivated accounts have no public page; publish/update/withdraw are POST-only, CSRF-protected, owner-only; `Cache-Control: no-cache` so a withdrawal is immediate; analytics events carry ids only) |
| 8.2.1 (catalog dictionaries) | Only staff with the change permission edit or merge the dictionaries | done (T50: `/django-admin/` staff only, merge action needs the change permission and is a POST with CSRF; anonymous, artist and institution users get the login page or 403; an entry with assignments cannot be deleted, merge is one transaction within one kind; artists can only pick active entries of the right kind, checked again in the service; names are autoescaped) |

## Public catalog (US-4.1, D123)

The catalog `/artysci/` is public by design (D15). Data comes only from the publication snapshot
(`CatalogEntry`), is filtered by `Artist.objects.published()` on every request (draft, withdrawn and
deactivated accounts never appear), and carries no e-mail or phone (D9); tests assert no `mailto:`,
`tel:`, `@`, inline script or style. Photos are short-lived signed links shown only while the artist
confirms the rights (D4, D7). The `?strona` parameter is validated as ASCII digits (max 9) before use.

Filters (US-4.2, D127): every URL parameter is checked against a closed list (voivodeships, artist
types, age groups, active dictionary entries) or parsed as ASCII digits (max 6, at least 1); anything else
is dropped, never echoed and never an error, so there is no reflected input. Filter matching runs on the
read model in code (no raw SQL, no user text in queries). The analytics events carry only these checked
values and numbers (no IP, user id or e-mail; the actor is empty). `/ogloszenia/nowe/` is a public GET-only
placeholder that reads no data.

Text search (US-4.3, D129): `q` is free text, so it is the one reflected input of the catalog. It is cut to
100 characters, reduced to `[a-z0-9]` words (at most 8) before it reaches the database (ORM `contains`
lookups, no raw SQL, so no injection and no LIKE wildcard), and shown back only through Django autoescaping
(a test posts `<script>`). Because it may hold personal data it is never logged (the access log records the
path without the query string), never stored in an analytics event (`catalog_searched` gets only
`text_query` and `word_count`) and not passed on to the notice page link.

## Reporting a vulnerability

Open a private security advisory on the GitHub repository, or contact the owner directly. Do not
open a public issue for vulnerabilities.
