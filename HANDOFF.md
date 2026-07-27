# HANDOFF – 1Step („Една стъпка")

## Project
Django app for anyone who wants calmer, healthier daily habits. **Pivoted** from a static 7-day health plan into a calm
**daily one-step ritual**: „Една стъпка. Всеки ден." — the app shows **one** small
step at a time; the user does it or swaps for another, and the next is offered.

- **GitHub:** https://github.com/PeterStoyanov83/moiat-plan-50
- **Live URL:** https://web-production-e3b54.up.railway.app
- **Railway project:** `1-step App` (service `web`) · Postgres attached
- **Local path:** `/Users/peterstoyanov/PycharmProjects/PythonProject/1Step` (local app folder renamed from `moiat_plan_50/` → `1Step/` on 2026-07-18; nested git repo, GitHub name `moiat-plan-50` and Railway unaffected). Outer PyCharm workspace dir `PythonProject/` rename pending (user does it — it's the live CWD).
- **Python package:** `onestep` (gunicorn: `onestep.wsgi:application`).

---

## Current status (2026-07-27) — LIVE on `main`

The web-MVP behavioral platform (the **BOS**, 7 engines) is deployed. Per-engine completeness
lives in `bos/STATUS.md` — **6 of 7 at 🟢/✅**; only mobile/sensor work (Track B) + the legal
launch gate remain. Full loop: category bubbles → area-filtered daily steps → verify → tree
growth + level-up → gentle recovery → AI reflection that learns.

### User flow
1. `/` home → „Направи първата стъпка" (or „Влез с Google" / „Вход")
2. `/questionnaire/` — 18-q interview (+ `first_name`, GDPR consent). Prefilled name if signed in.
3. → **session** `response_id` + (if logged in) tie to user → redirect to `/ritual/`
4. `/ritual/` — the daily ritual: opens on **category bubbles** (Движение · Хранене · Вода · Сън ·
   Близост · Спокойствие · Финанси). Pick an area → its steps (A/Б/В, level-scaled, safety-gated) →
   done → next step in the same area; „Приключих за днес" ends → celebration + end-of-day reflection.
5. Ritual endpoints: `/ritual/choices/` (area's actions), `/ritual/done/` (complete + lazy level
   check), `/ritual/reflect/` (save reflection), `/api/verify/` (objective verification — future
   mobile). `/ritual/swap/` is legacy.
6. `/progress/` — „Твоето дърво": the living tree (grows with verified actions, animates on
   level-up), streak/total, recent steps, link to Размисли.
7. `/reflections/` — „Твоите размисли": journal of past reflections **+ today's composer** (reflect & revisit).
8. `/profile/` — account: name, email, login method, streak/total, links.
9. `/accounts/*` — allauth. `/admin/` — Django admin. Bottom nav: **Днес · Напредък · Размисли · Профил**.
   (`/result/<id>/` full 7-day plan + `/download/` PDF still exist but are **unlinked** from the UI.)

### Architecture (app `plans`)
```
plans/
├── models.py          # QuestionnaireResponse, UserPlan, Feedback, StepCompletion, Level,
│                      #   ActionDef, UserProgram, ActionLog, HabitStability, TreeState,
│                      #   DailyAssignment, Reflection
├── daily.py           # ritual's action server: today_actions(category=…) — core-first, level-scaled,
│                      #   contraindication-gated, recovery-tapered; categories_meta() (bubbles)
├── behavior.py        # Behavior engine (01): per-level mission themes + weakest-habit adaptation
├── progression.py     # Level engine (04): mastery scoring + promote/extend
├── verification.py    # Verification engine (03): verify() sensor/timer/location/photo/confirm + anti-cheat
├── tree_state.py      # Tree (06) + Recovery (05): growth stage, health/dormant, recovery window + factor
├── reflection.py      # daily reflection question pool + storage + recent_answers (AI learning loop)
├── ai_companion.py    # optional Claude (Haiku): warm line + AI reflection question; graceful fallback
├── apps.py            # PostHog client init (disabled when no key)
├── step_engine.py     # LEGACY step engine — still feeds ai_companion candidates + the unused swap
├── knowledge_base.py / data/knowledge_base.json  # LEGACY: power only the old full-plan/PDF
├── profile_logic.py   # determine_profile() + generate_plan() (full plan / PDF only)
├── views.py           # home, questionnaire, ritual, ritual_choices, step_done, reflect, verify_action,
│                      #   progress, reflections, profile, result, pdf, feedback, privacy
├── context_processors.py  # google_flags
├── forms.py, admin.py, urls.py
└── templates/plans/   # base, home, questionnaire, ritual, progress, reflections, profile, result,
                       #   pdf_plan, privacy, feedback*  + _topnav.html / _bottomnav.html partials
templates/allauth/layouts/base.html   # brands all allauth pages (project DIRS override)
onestep/settings.py    # allauth + google + email/password + Resend SMTP + PostHog + hardening
bos/                   # governance: CONSTITUTION · README · STATUS · engines/01–07 (source of truth)
```

### Key design: the ActionDef library + the BOS engines
The daily ritual is served by `daily.today_actions()` from the **ActionDef** library (100 actions,
full metadata; seeded in `0008`/`0011`/`0012`) — filtered by the user's chosen category, scaled to
the **system-driven level**, safety-gated (contraindications), and tapered during recovery. Mastery
(`progression`), adaptation (`behavior`), verification (`verification`) and the tree (`tree_state`)
are separate single-responsibility engines per `bos/engines/`. The legacy `knowledge_base.json` +
`step_engine.py` + `generate_plan()` now power only the old full-plan/PDF (unlinked from the UI).

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
| `EMAIL_HOST` (+ `EMAIL_HOST_USER`/`PASSWORD`/`PORT`, `DEFAULT_FROM_EMAIL`) | **password-reset emails** (SMTP; console fallback) | ✅ set 2026-07-18 — **Resend SMTP** (`smtp.resend.com:587`, user `resend`, pwd = Najivo `RESEND_API_KEY` reused from Railway `pleasant-art`/Bileti; from `1Step <info@najivo.bg>`, najivo.bg domain already verified in Resend). Verified via `manage.py sendtestemail`. |

Deploy: push to `main` → Railway auto-builds (Dockerfile) → `start.sh` runs `migrate` + gunicorn.
Healthcheck fix (historical): `ALLOWED_HOSTS` always appends `.railway.app`; no `SECURE_SSL_REDIRECT` (keeps internal healthcheck 2xx).

---

## Migrations
`0001`–`0003` base + consent · `0004` first_name + StepCompletion · `0005` user FK · `0006` Site
name→„1Step" · `0007` habit-engine schema (Level, ActionDef, UserProgram, ActionLog, HabitStability,
TreeState, DailyAssignment) · `0008` seed (20 levels + 8 starter actions) · `0009`–`0010` ActionDef
metadata + backfill · `0011`–`0012` library → **100 actions** · `0013` Reflection.

## Tests
`plans/tests.py` — **49 tests**, all green (step engine, ritual flow, progress, AI companion,
Google claim, Knowledge library contract + contraindication inference, Recovery taper,
Reflection + journal + input bounds, Behavior themes/adaptation, Level promote/extend,
Verification endpoint, category selection). Run: `POSTHOG_API_KEY="" ./venv/bin/python manage.py test plans`
(empty key keeps the analytics client disabled during tests; use `./venv/bin/python -m pip` — the
venv's `pip` shebang broke on the folder rename).

---

## TODO / backlog
- [x] **Fill privacy contact** — `plans/templates/plans/privacy.html` now shows `info@najivo.bg` (2026-07-18).
- [ ] **⛔ LAUNCH BLOCKER — register the ЕООД, then add the data-controller identity to the privacy policy.** Decided 2026-07-18: hold launch to real users until the ЕООД exists (no entity registered yet — see `~/Downloads/NaJivo — Правна структура.pdf`; register at brra.bg, ~160 лв, 1–2 days). Then add controller name + ЕИК + седалище to `privacy.html`. Do NOT collect real users' health data before this.
- [x] **SMTP** — Resend SMTP wired on Railway `1-step App`/web (from `1Step <info@najivo.bg>`); verified 2026-07-18. Optional: confirm a live reset via `/accounts/password/reset/`.
- [ ] **Change the temp admin password** for `Peter`. _(Deferred by user 2026-07-18 — still a pre-launch security item; do before wide launch.)_
- [ ] Optional: multi-week level progression; reminders/notifications.
- [ ] **Teach the founder how to use PostHog** — walkthrough of funnels, retention, the
  self-driving inbox (`eu.posthog.com/project/227058`), and reading the 5 events. _(User requested 2026-07-18.)_
- [ ] **Before launch (part of the ЕООД gate):** disclose **PostHog (EU) as a data processor**
  in the privacy policy + sign its DPA; decide whether to keep `enable_exception_autocapture`.
- [ ] **Recreate the venv** — it broke on the `moiat_plan_50/`→`1Step/` rename (pip shebang points
  at the old path). Works via `./venv/bin/python -m pip …`; cleanest is a fresh `python -m venv`.
- [ ] Rename the outer PyCharm workspace folder `PythonProject/` → `1Step/` (user; it's the live CWD + drives Claude's memory path). Optional: rename GitHub repo `moiat-plan-50` → 1Step.

---

## Latest (2026-07-26)
- **Ritual home = category bubbles.** The ritual now opens on **circular category bubbles**
  (Движение · Хранене · Вода · Сън · Близост · Спокойствие · Финанси) instead of an auto-served
  mixed A/Б/В. The user taps an area → `POST /ritual/choices/` (`ritual_choices` view) →
  `daily.today_actions(category=…)` serves only that area's steps; `step_done` keeps the next
  steps in the same area. `daily.categories_meta()` powers the bubbles (icons/colours reused from
  the ritual's ICON/META). Selection rules (core-first, weakest-habit bias, safety gating) now run
  *within* the chosen area. Behavioral note: the "≥3/day includes core habits" guarantee is now
  user-gated. 49/49 green.

## Latest (2026-07-19)
- **Reflect-from-journal + AI-endpoint hardening.** `/reflections/` now has a **today's composer**
  at the top (reflect straight from the „Размисли" tab, reusing the `reflect` endpoint), above the
  past entries. **Security:** reflection input is length-bounded server-side (`MAX_ANSWER=2000`,
  `MAX_QUESTION=200` — fixes a real >200-char `question` → DB-500 bug; API can bypass client caps)
  and each answer fed to the LLM is truncated (`PROMPT_ANSWER_CAP=280`) to limit prompt-injection
  surface. Full **AI-endpoint security requirements** written into `bos/engines/07-ai-planner-engine.md`
  (auth/isolation, input bounds, rate/cost limits, injection resistance, output escaping, scope) —
  binding for the future chat. **Known gap:** the companion call runs on every ritual load; add a
  per-day cache / rate limit before shipping a chat. 46/46 green.
- **Reflection UI redesigned + a journal to revisit.** The end-of-ritual reflection is now a calm,
  intentional moment (gentle divider, softer larger input, readable placeholder, delayed fade-in so
  the celebration lands first, non-shaming thanks). New **`/reflections/` journal** (`views.reflections`,
  `reflections.html`) — a warm, flowing list (not boxed cards) of past answered reflections with an
  empty state; linked from the progress page under the tree. Built with the impeccable craft rules
  (contrast, reduced-motion, no slop). 45/45 green.
- **Verification — server `/api/verify/` endpoint built** (`views.verify_action`, `POST api/verify/`).
  A client posts one action's evidence (`measured`/`claimed`, `minutes`, `confidence`, or `confirmed`);
  `verification.verify()` resolves it (sensor/timer/location/photo/confirm) with gentle anti-cheat
  (`claimed > 3× measured` → not counted, non-shaming message). On a counting outcome it bridges to
  streak/tree (`mark_done`) + runs the level check (`level_event`). The browser has no sensors, so
  `step_done` stays the web path; this endpoint is for the future mobile client + is covered by tests.
  Verification → 🟢 (server side). Remaining (Track B): wearable/HealthKit/Fit/GPS adapters + the app. 44/44 green.
- **AI Planner — reflection now AI-written + a learning loop.** The companion's single Claude call
  (`ai_companion._ai_choose`) now returns `{index, message, reflection}` — the warm line **and** the
  end-of-day reflection question, both informed by the user's **recent reflection answers**
  (`reflection.recent_answers`, fed into the prompt). `pick_opening_step` returns a 3-tuple; ritual
  falls back to the rule-based pool when AI is off/fails. The reflect endpoint now stores the exact
  question shown. Habit-stability selection already lives in Behavior (1). No schema change. 39/39
  green. AI Planner → 🟢. This is the companion "learning" substrate the future AI chat builds on.
- **Tree Engine — level-up now animates.** `progress.html` consumes the Level engine's
  `celebrate_level` signal: it mounts the tree one level below and calls `tree.setLevel(new, {animate})`
  after the page settles, so the user **watches the trunk/branches grow** into the new level (major
  growth event, spec §6). Non-celebration loads are unchanged. Vendored engine still used as-is.
  Remaining: long-term events (birds/fruit) + a recovery-renewal visual on return.
- **Product principle (founder, 2026-07-19): never show level numbers / the word „ниво" to users.**
  Levels 1–20 stay internal mechanics; progression is expressed only through the tree metaphor +
  its Bulgarian growth-stage labels. Level-up copy is now „Дървото ти пуска нов клон." (no number).
- **Level Engine — mastery loop surfaced.** `views.ritual` now runs a **lazy nightly re-eval**
  (`evaluate_level` on load, not only on completion) so promote/extend land even when idle.
  Promote/extend messages surface as a **ritual banner** (server-rendered + shown from `step_done`
  JSON `level_event`); a promotion sets `session['tree_celebrate']` → the **progress page shows a
  "Ново ниво!" celebration** (Level *emits*, Tree *renders*). Extend copy stays non-shaming. No
  schema change. Level → 🟢. 37/37 green. Remaining: a true cron; the explicit tree blossom (Tree engine).
- **Behavior Engine — mission themes + weakest-habit adaptation** (`plans/behavior.py`, wired into
  `daily.today_actions`). `emphasized_categories(level)` = per-level curriculum (foundations first;
  nutrition/sleep @L4, social @L8, financial @L12). `category_stability()` scores each category from
  recent `ActionLog` completions (persisted to `HabitStability`, now in admin). Missions are ordered
  theme-first → weakest-category-first → stable daily shuffle; **core habits still lead, untouched**.
  No schema change. Behavior → 🟢. 34/34 green.
- **AI Planner — daily reflection question shipped** (the precursor to any AI chat). New
  `Reflection` model (`migrations/0013`, one per response/day, in admin) + `plans/reflection.py`
  (rule-based question pool, stable per day). Shown on the ritual's end screen (`ritual.html`
  final) with a textarea → `POST /ritual/reflect/` (`reflect` view). Answer stored for the future
  AI-learning loop. Founder chose the **dedicated Reflection model**. Open: AI-written question;
  surface reflections back to the companion. 31/31 green.
- **Recovery Engine wired in.** `tree_state.recovery_factor()` — a linear taper 0.4→1.0 over the
  7-day recovery window. `daily.py` applies it to targets **only for effort metrics (steps/minutes)**
  — sleep hours and hydration glasses are never reduced (that's not recovery). `daily.welcome_back_message()`
  shows a gentle, non-shaming line as the ritual lead on return (spec §5: "missing time is normal").
  Tests cover the taper, effort-vs-rest scaling, and welcome-back gating. Recovery now 🟢 in STATUS.

## Latest (2026-07-18)
- **Knowledge Engine — library grown 8 → 100 actions** (`migrations/0011`+`0012`) across all 7
  categories (movement 19, mind 18, nutrition 17, social 14, sleep 12, financial 11, hydration 9).
  All `growth_mission` (kept 4 cores so daily variety isn't starved), full metadata + `why`.
- **Refined contraindication inference** (`daily.py::user_contraindications`): now 5 inferrable
  tags — `severe_joint_pain`, `acute_injury`, plus **`cardiac`, `balance_issues`, `respiratory`**
  (keyword scan of `health_limitations`). High-intensity actions (stairs, brisk walk, one-leg
  balance…) carry the matching tags; `KnowledgeLibraryTests` enforce the metadata contract +
  the inference + a safe-substitution test. 24/24 green.
- **Weather deferred** to a later version (per founder — CI/CD scoping). Actions carry
  `weather_adaptations` metadata (rain/heat/cold) but the planner doesn't honor it yet.
- **PostHog analytics (EU) instrumented** via `@posthog/wizard` self-driving (project 227058,
  `eu.posthog.com`). Server-side events in `plans/views.py`: `questionnaire_completed`,
  `daily_action_completed`, `plan_downloaded`, `feedback_submitted` (+ a `.set`); client init in
  `plans/apps.py`; `PosthogContextMiddleware` in settings. All events are **PII-safe**
  (pseudonymous `response-{pk}`/user-pk ids; no names/emails/health answers). Keys live in
  `.env` (gitignored) + Railway `1-step App`/web (`POSTHOG_API_KEY`, `POSTHOG_HOST`).
  **Hardened** `apps.py` so a missing key disables the client instead of crashing (wizard's
  raw `os.environ[...]` would KeyError; also fixed its `api_key=`→`project_api_key=` for
  posthog 7.x). `enable_exception_autocapture` is ON only when configured — **review before
  launch** (tracebacks could carry health context). Note: `self-driving` is PostHog's
  autonomous agent (inbox/scouts), broader than plain funnel analytics.
- **Terminology rebrand крачка/крачки → стъпка/стъпки** across all code + docs (templates,
  `step_engine.py`, `ai_companion.py`, `tests.py`, `knowledge_base.json`, and the `.md` docs).
  Motto is now **„Една стъпка. Всеки ден."** (founder chose the full rebrand). Brand name
  resolved: **1Step**. No behaviour change; 18 tests still green.
- **Upper + bottom nav on ALL pages.** New shared partials `plans/templates/plans/_topnav.html`
  (brand + Профил/Вход) and `_bottomnav.html` (Днес · Напредък · Пълен план · Профил, active tab
  auto-detected from `request.resolver_match.url_name`). Wired into `base.html` (all Bootstrap
  pages, + bottom-nav CSS & body padding), `ritual.html` and `progress.html` (added top nav,
  swapped their inline bottom navs for the include), and the allauth base (bottom nav added).
  New `context_processors.nav_context` supplies `nav_plan_id` everywhere so „Пълен план" shows
  app-wide (registered in `settings.TEMPLATES`). PDF template left nav-free.
- **Local app folder renamed** `moiat_plan_50/` → `1Step/` (see Project). Nested repo/GitHub/Railway unaffected.
- **Session-start protocol added to `CLAUDE.md`**: read HANDOFF.md + BHANDOFF.md + bos/CONSTITUTION.md + bos/STATUS.md first, every session.

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
