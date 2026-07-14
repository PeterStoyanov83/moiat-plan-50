# HANDOFF – 1Step

## Project
Django MVP app that generates a personalized 7-day health plan for people 50+.
- **GitHub:** https://github.com/PeterStoyanov83/moiat-plan-50
- **Live URL:** https://web-production-e3b54.up.railway.app
- **Local path:** `/Users/peterstoyanov/PycharmProjects/PythonProject/moiat_plan_50`

---

## Current Status (2026-06-12)

### ✅ What works
- Full Django app builds and runs correctly
- Dockerfile-based Railway deployment
- `start.sh` runs migrate then gunicorn on `PORT=8000`
- Static files collected at build time via `CompressedStaticFilesStorage`
- All migrations apply cleanly
- Gunicorn starts and listens on `0.0.0.0:8000` confirmed in logs
- `PORT=8000` set manually in Railway Variables tab
- Custom Start Command in Railway UI set to `sh start.sh`

### ✅ Healthcheck blocker — ROOT-CAUSED AND FIXED (2026-07-10)
The real cause was **not** the load-balancer port. With `DEBUG=False` and
`ALLOWED_HOSTS` set to only the public domain, Django returned **HTTP 400
(Invalid HTTP_HOST header)** to Railway's healthcheck, which probes `/` with
`Host: healthcheck.railway.app` — not the public domain. Gunicorn was up, but
every healthcheck got a non-2xx, so the deploy never went healthy — and because
it never went healthy, Railway never finalized the domain's target port (which
is why the manual "Edit Port" step *appeared* to be needed). One root cause.

**Fix (in `settings.py`, committed):** always append `.railway.app` to
`ALLOWED_HOSTS` and `https://*.railway.app` to `CSRF_TRUSTED_ORIGINS`,
regardless of the env var, plus auto-pick up `RAILWAY_PUBLIC_DOMAIN`. Verified
locally: `healthcheck.railway.app` now accepted, `evil.com` still rejected.
Also added prod cookie/HSTS hardening — but intentionally **left
`SECURE_SSL_REDIRECT` off** so the internal (HTTP) healthcheck isn't 301'd.

### Debugging history (so you don't repeat it)
| Attempt | Problem | Fix |
|---------|---------|-----|
| Nixpacks | `nixpacks.toml` silently ignored; pango/cairo missing | Switched to Dockerfile |
| WhiteNoise crash | `CompressedManifestStaticFilesStorage` needs manifest; collectstatic ran with wrong storage | Use `CompressedStaticFilesStorage` |
| `$PORT` not expanding | Railway CMD handling didn't shell-expand `$PORT` | Created `start.sh` with explicit `export PORT="${PORT:-8000}"` |
| ~~Port not routed~~ | *Misdiagnosis.* Real cause: Django 400'd the healthcheck host | Added `.railway.app` to `ALLOWED_HOSTS` in `settings.py` |

---

## Architecture

```
moiat_plan_50/
├── Dockerfile              # python:3.11-slim, installs pango/cairo for WeasyPrint
├── start.sh                # entrypoint: migrate + gunicorn on $PORT (fallback 8000)
├── railway.json            # builder: DOCKERFILE, healthcheck: /
├── requirements.txt        # Django, WeasyPrint, gunicorn, psycopg2, whitenoise, dj-database-url, python-dotenv
├── .env                    # local only (gitignored): DEBUG=True, SECRET_KEY, ALLOWED_HOSTS
├── onestep/                # Django project package (was moiat_plan_50/)
│   ├── settings.py         # reads from env vars via python-dotenv
│   ├── wsgi.py             # gunicorn target: onestep.wsgi:application
│   └── urls.py
└── plans/                  # main Django app
    ├── models.py            # QuestionnaireResponse, UserPlan, Feedback
    ├── forms.py             # Bulgarian labels/choices
    ├── views.py             # home, questionnaire, result, download_pdf, feedback
    ├── urls.py
    ├── admin.py
    ├── profile_logic.py     # determine_profile() + generate_plan()
    └── templates/plans/
        ├── base.html        # Bootstrap 5, green theme
        ├── home.html
        ├── questionnaire.html
        ├── result.html
        ├── feedback.html
        ├── feedback_success.html
        └── pdf_plan.html    # WeasyPrint PDF template
```

---

## Railway Environment Variables (set in Variables tab)
| Key | Value |
|-----|-------|
| `SECRET_KEY` | (long random string) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `web-production-e3b54.up.railway.app` |
| `PORT` | `8000` |

`DATABASE_URL` — not set, app uses SQLite (ephemeral on Railway free tier).
For persistent data: add PostgreSQL plugin → Railway auto-sets `DATABASE_URL`.

---

## Key Technical Decisions

| Decision | Reason |
|----------|--------|
| Dockerfile over Nixpacks | Nixpacks ignored `nixpacks.toml`; Dockerfile gives full control over WeasyPrint system libs |
| `CompressedStaticFilesStorage` (not Manifest) | Manifest variant crashes if collectstatic didn't run with same storage at build time |
| `start.sh` entrypoint | `$PORT` wasn't shell-expanding in Railway's CMD handling; explicit sh script is bulletproof |
| SQLite fallback | No PostgreSQL plugin connected yet; settings auto-detect `DATABASE_URL` |
| `SECRET_KEY=build-only-dummy-key` in Dockerfile | Needed for collectstatic at build time before real env vars are available |

---

## User Flow
1. `/` → home page → "Започни моя план"
2. `/questionnaire/` → 18-question form
3. POST → `determine_profile()` → `generate_plan()` → saves `QuestionnaireResponse` + `UserPlan`
4. `/result/<plan_id>/` → shows profile + 7-day plan
5. `/download/<plan_id>/` → PDF via WeasyPrint
6. `/feedback/<response_id>/` → feedback form → `/feedback/success/`
7. `/admin/` → Django admin (needs superuser)

---

## Profiles Logic (`plans/profile_logic.py`)
| Profile | Condition |
|---------|-----------|
| Лек старт | `movement_level == 'ниско'` AND `energy_level <= 2` |
| Отслабване без стрес | `main_goal == 'отслабване'` |
| Повече енергия | `main_goal == 'енергия'` |
| Социално активиране | `social_activity == 'ниска'` |
| Баланс и поддръжка | all other cases |

---

## Create Superuser (after deploy is live)
In Railway → Service → **Deploy** tab → open a terminal shell:
```bash
python manage.py createsuperuser
```
Then access admin at: `https://web-production-e3b54.up.railway.app/admin/`

---

## Next Steps (backlog)
- [x] ~~CRITICAL: Set Edit Port → 8000~~ — superseded by the `ALLOWED_HOSTS` fix; redeploy from `main` and the healthcheck should pass on its own
- [ ] Redeploy and confirm healthcheck goes green (no dashboard step needed)
- [ ] Create superuser via Railway shell once live
- [ ] Add PostgreSQL plugin for persistent data (SQLite is ephemeral on Railway)
- [ ] Test full user flow on production
- [ ] Test PDF download (WeasyPrint + pango/cairo already in Dockerfile)
- [ ] Set `ALLOWED_HOSTS` to exact Railway domain in Variables if getting 400 errors
