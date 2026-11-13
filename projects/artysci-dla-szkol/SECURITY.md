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
- Secrets: `DJANGO_SECRET_KEY`, database and SMTP credentials (env only, never in the repo).

**Trust boundaries**
1. Browser → web app (internet). Everything from the browser is untrusted: validated in forms and
   services, CSRF-checked, escaped on output, framed by a strict CSP.
2. Web app → PostgreSQL, SMTP, object storage (private network; credentials from env).
3. Web app → user-files origin (D62): uploaded content never runs on the app's origin.
4. Worker (Procrastinate) → same database; jobs carry ids, not personal data.
5. Logs → host log collector: JSON on stdout without e-mails, full IPs, cookies or secrets.

**Main threats and controls**

| Threat | Control |
| --- | --- |
| XSS / content injection | Django autoescape; CSP without `unsafe-inline`/`unsafe-eval`; HTMX with `allowEval: false`, `allowScriptTags: false` |
| CSRF (also via HTMX) | `CsrfViewMiddleware` on all unsafe methods; HTMX sends `X-CSRFToken`; cookies `SameSite=Lax` |
| Clickjacking | `frame-ancestors 'none'` + `X-Frame-Options: DENY` |
| Session theft | `HttpOnly`, `Secure` + `__Host-` cookies in prod, HSTS, SSL redirect |
| Credential stuffing / brute force | `apps/accounts/throttling.py` (scaffold, wired into login by E1) |
| Malicious uploads | separate origin, type/size checks (T06, E2) |
| Data leak through logs | redaction in `apps/core/logs.py`, pseudonymised user ids, no query strings |
| Account enumeration, spam | E1 (generic errors), E2+ (moderation, rate limits) |

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

Remediation time frames for vulnerable dependencies (ASVS 15.1.1): critical 7 days, high 30
days, others with the next regular update; dependencies are reviewed at least monthly.

## ASVS 5.0 level 1 checklist

Status: **done**, **partial** (what is missing), **planned** (task), **n/a** (feature absent).

| ID | Requirement (short) | Status |
| --- | --- | --- |
| 1.2.1 | Context-aware output encoding | done (Django autoescape) |
| 1.2.2 | URL building encodes untrusted data | done (`{% url %}`, `urlencode`) |
| 1.2.3 | Encoding in JS/JSON | done (no inline JS; `json_script` when needed) |
| 1.2.4 | Parameterised queries | done (ORM only, no raw SQL) |
| 1.2.5 | OS command injection | n/a (no OS calls) |
| 1.3.1 | Sanitise WYSIWYG HTML | planned (profiles, if rich text is added) |
| 1.3.2 | No `eval()` / dynamic code | done (CSP without `unsafe-eval`, HTMX `allowEval: false`) |
| 1.5.1 | Safe XML parser config | n/a (no XML input) |
| 2.1.1 | Input validation rules documented | planned (per feature, E1+) |
| 2.2.1 | Input validated against business rules | planned (per feature, Django forms) |
| 2.2.2 | Validation at a trusted service layer | done by design (`services.py` rule, CLAUDE.md) |
| 2.3.1 | Business flow steps in order | planned (inquiries, notices) |
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
| 5.2.1 | File size limits | planned (T06, E2) |
| 5.2.2 | File extension and content checked | planned (T06, E2) |
| 5.3.1 | Uploads never executed | planned (T06: separate origin, D62) |
| 5.3.2 | Server-generated file paths | planned (T06) |
| 6.1.1 | Rate limiting / anti-automation documented | done (this file, `throttling.py`) |
| 6.2.1 | Passwords ≥ 8 chars | done (`MinimumLengthValidator`) |
| 6.2.2 | Users can change password | planned (E1) |
| 6.2.3 | Change needs current + new password | planned (E1) |
| 6.2.4 | Check against common passwords | done (`CommonPasswordValidator`) |
| 6.2.5 | No composition rules | partial (`NumericPasswordValidator` rejects all-digit passwords; review in E1) |
| 6.2.6 | `type=password` fields | planned (E1) |
| 6.2.7 | Paste / password managers allowed | planned (E1) |
| 6.2.8 | Password checked exactly as entered | done (Django hashers) |
| 6.3.1 | Brute force / stuffing controls | partial (scaffold T04, wired in E1) |
| 6.3.2 | No default accounts | done (none created; seed users have unusable passwords) |
| 6.4.1 | Initial passwords/codes random, expiring | planned (E1) |
| 6.4.2 | No password hints / secret questions | done (none) |
| 7.2.1 | Session checked on the backend | done (Django sessions) |
| 7.2.2 | Dynamic session tokens | done (Django sessions) |
| 7.2.3 | Tokens from a CSPRNG | done (Django sessions) |
| 7.2.4 | New session on login | planned (E1, Django `login()` rotates the key) |
| 7.4.1 | Logout/expiry ends the session | planned (E1) |
| 7.4.2 | Disabling a user ends their sessions | planned (E1, E9) |
| 8.1.1 | Authorisation rules documented | planned (E1 roles) |
| 8.2.1 | Function-level access control | planned (per feature; admin is staff-only) |
| 8.2.2 | Data-level access control (IDOR) | planned (per feature) |
| 8.3.1 | Authorisation in the service layer | planned (per feature, `services.py`) |
| 9.1.1–9.2.1 | Self-contained tokens (JWT etc.) | n/a (none; Django signed tokens use HMAC) |
| 10.4.1–10.4.5 | OAuth authorisation server | n/a |
| 11.3.1 | No ECB / weak padding | n/a (no own encryption) |
| 11.3.2 | Approved ciphers only | n/a (no own encryption) |
| 11.4.1 | Approved hash functions | done (Django: PBKDF2-SHA256, HMAC-SHA256) |
| 12.1.1 | TLS 1.2+ only | planned (deployment, D91) |
| 12.2.1 | TLS for all external connections | partial (app redirects + HSTS; proxy at deployment, D91) |
| 12.2.2 | Publicly trusted certificates | planned (deployment, D91) |
| 13.4.1 | No `.git` in the deployment | done (`.dockerignore`) |
| 14.2.1 | No sensitive data in URLs | partial (query strings never logged; per feature in E1+) |
| 14.3.1 | Client storage cleared on logout | planned (E1, `Clear-Site-Data`) |
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
| 16.3.1 | Authentication events logged | planned (E1; throttle lockout logged now) |
| 16.4.1 | Log injection prevented | done (JSON encoding) |
| 16.5.1 | Generic error messages | done (`DEBUG = False` in prod) |

## Reporting a vulnerability

Open a private security advisory on the GitHub repository, or contact the owner directly. Do not
open a public issue for vulnerabilities.
