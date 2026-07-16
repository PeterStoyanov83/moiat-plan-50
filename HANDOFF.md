# HANDOFF – 1Step („Една крачка")

## Project
Django app for people 50+. **Pivoted** from a static 7-day health plan into a calm
**daily one-step ritual**: „Една крачка. Всеки ден." — the app shows **one** small
step at a time; the user does it or swaps for another, and the next is offered.

- **GitHub:** https://github.com/PeterStoyanov83/moiat-plan-50
- **Live URL:** https://web-production-e3b54.up.railway.app
- **Railway project:** `1-step App` (service `web`) · Postgres attached
- **Local path:** `/Users/peterstoyanov/PycharmProjects/PythonProject/moiat_plan_50`
- **Python package:** `onestep` (gunicorn: `onestep.wsgi:application`). Outer repo dir is still `moiat_plan_50/`.

---

## Current status (2026-07-15) — LIVE, all shipped on `main`

The full ritual redesign + accounts are deployed and verified in production.

### User flow
1. `/` home → „Направи първата крачка" (or „Влез с Google" / „Вход")
2. `/questionnaire/` — 18-q interview (+ `first_name`, GDPR consent). Prefilled name if signed in.
3. → **session** `response_id` + (if logged in) tie to user → redirect to `/ritual/`
4. `/ritual/` — the daily one-step ritual (single step, „Направих го" / „Покажи ми друга",
   micro-celebration, then next; „Приключих за днес" ends). Greeting line is AI-written when enabled.
5. `/ritual/done/`, `/ritual/swap/` — JSON endpoints (step engine).
6. `/progress/` — Напредък: streak, 7-day chart, recent steps.
7. `/result/<id>/` — the old full 7-day plan, kept as „Пълен план"; `/download/<id>/` PDF.
8. `/profile/` — account: name, email, login method, streak/total, links.
9. `/accounts/*` — allauth: login, signup, password reset/change, email mgmt.
10. `/admin/` — Django admin (username + password).

### Architecture (app `plans`)
```
plans/
├── models.py           # QuestionnaireResponse(+user FK,+first_name,+consent), UserPlan, Feedback, StepCompletion
├── knowledge_base.py   # loads data/knowledge_base.json; level mapping (movement/nutrition)
├── data/knowledge_base.json  # the step library (task pools by level + social/finance)
├── step_engine.py      # eligible_steps / offer_step / mark_done / today_progress / weekly_history
├── ai_companion.py     # optional: Claude (Haiku 4.5) picks step + writes line; falls back to engine
├── profile_logic.py    # determine_profile() + generate_plan() (for the full plan / PDF)
├── views.py            # home, questionnaire, ritual, step_done, step_swap, progress, profile, result, pdf, feedback, privacy
├── context_processors.py  # google_flags
├── forms.py, admin.py, urls.py
└── templates/plans/    # base.html (calm cream), home, questionnaire, ritual, progress, profile, result, pdf_plan, privacy, feedback*
templates/allauth/layouts/base.html   # brands all allauth pages (project DIRS override)
onestep/settings.py     # allauth + google + email/password + email backend + hardening
```

### Key design: the KB *is* the step library
`generate_plan()` still builds the full plan/PDF, but the **ritual** re-serves the same
`knowledge_base.json` task pools **one at a time** via `step_engine`. Levels come from
`movement_level_for` / `nutrition_level_for`; profile sets category priority.

---

## Auth
- **Google Sign-In** (django-allauth): GET-link login (`SOCIALACCOUNT_LOGIN_ON_GET`),
  auto-connects to an existing account by verified email (`EMAIL_AUTHENTICATION[_AUTO_CONNECT]`).
  Redirect URI in Google console: `…/accounts/google/login/callback/`. Client type MUST be **Web application**.
- **Email + password** (allauth): login by email, signup, **password reset** (needs SMTP), change, email mgmt.
- **Admin** (`/admin/`) uses username+password, separate from allauth/Google.
  Superuser: **`Peter`** / peterstoyanov83@gmail.com (temp pwd set 2026-07-15 — CHANGE IT).
- Logged-in users own their `QuestionnaireResponse` → cross-device; anon session response is claimed on first login.

---

## Railway env vars (toggles)
| Key | Purpose | Set? |
|-----|---------|------|
| `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `PORT=8000` | core | ✅ |
| `DATABASE_URL` | Postgres (persistent) | ✅ (auto) |
| `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_SECRET` | shows „Влез с Google" | ✅ set |
| `ANTHROPIC_API_KEY` | activates AI companion (else rule-based). Opt: `AI_COMPANION_MODEL`, `AI_COMPANION_TIMEOUT` | ✅ set |
| `EMAIL_HOST` (+ `EMAIL_HOST_USER`/`PASSWORD`/`PORT`, `DEFAULT_FROM_EMAIL`) | **password-reset emails** (SMTP; console fallback) | ⛔ NOT set — reset emails won't deliver until added |

Deploy: push to `main` → Railway auto-builds (Dockerfile) → `start.sh` runs `migrate` + gunicorn.
Healthcheck fix (historical): `ALLOWED_HOSTS` always appends `.railway.app`; no `SECURE_SSL_REDIRECT` (keeps internal healthcheck 2xx).

---

## Migrations
`0001`–`0003` base + consent · `0004` first_name + StepCompletion · `0005` user FK · `0006` Site name→„1Step".

## Tests
`plans/tests.py` — 18 tests (step engine, ritual flow, progress, AI-companion fallback+mock, Google account ownership/claim). All green. Run: `python manage.py test plans`.

---

## TODO / backlog
- [ ] **Fill privacy contact** placeholder in `templates/plans/privacy.html` (`[ДОПЪЛНЕТЕ…]`) before wide launch.
- [ ] **SMTP** (`EMAIL_HOST` …) so password-reset emails actually send.
- [ ] **Change the temp admin password** for `Peter`.
- [ ] Optional: add Profile/Login to the ritual/progress bottom nav (currently header + home only).
- [ ] Optional: multi-week level progression; reminders/notifications.

---

## Latest (2026-07-16)
- **Ritual = one step as 3 options (А/Б/В).** `step_engine.offer_choices()` returns
  up to 3 distinct eligible steps (variety across categories); ritual shows them as
  A/B/C cards — pick one → mark done → next 3. When AI is on, option **А** is the
  companion's pick. `views._build_choices()`; `step_done` now returns `{choices, progress}`
  (not `next`). Swap endpoint kept but unused by the UI.
- **Progress = Living Tree** (Fable's engine). `plans/static/plans/tree-engine.js`
  (vendored, framework-agnostic canvas). `progress.html` → „Твоето дърво": seeded per
  user (email/resp id), grows with **total StepCompletion count** (`completedActions`),
  season from month, personality `calm`. Replaced the 7-day bar chart; streak/total/recent kept.
  Source demo: `/Users/peterstoyanov/Progress Tree/` (README = algorithm/API).
- **Full auth live**: Google + **email/password login, signup, password reset/change,
  email mgmt** (allauth, branded via `templates/allauth/layouts/base.html`). `/profile/`
  page. Email backend from env (SMTP when `EMAIL_HOST` set, else console — reset emails
  need SMTP). Admin superuser `Peter` (temp pwd set — change it).
- **Design brief:** `design/REDESIGN_BRIEF.md` (project-grounded "personal life companion"
  transformation). Next builds from it: conversational onboarding; tree personality from
  profile; reflection prompt (+storage decision).
- No new migrations since `0006` (choices + tree are logic/static only). Tests: 18, green.
