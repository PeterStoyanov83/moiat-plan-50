# HANDOFF – Моят План 50+

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

### ⚠️ Last known blocker
**Railway healthcheck still failing** — gunicorn runs fine on port 8000 inside the container, but Railway's load balancer target port is not set, so external traffic can't reach it.

**One manual step still required in Railway dashboard:**
```
Settings → Networking → click domain row
→ "Edit Port" field → type 8000 → click Update
```

### Debugging history (so you don't repeat it)
| Attempt | Problem | Fix |
|---------|---------|-----|
| Nixpacks | `nixpacks.toml` silently ignored; pango/cairo missing | Switched to Dockerfile |
| WhiteNoise crash | `CompressedManifestStaticFilesStorage` needs manifest; collectstatic ran with wrong storage | Use `CompressedStaticFilesStorage` |
| `$PORT` not expanding | Railway CMD handling didn't shell-expand `$PORT` | Created `start.sh` with explicit `export PORT="${PORT:-8000}"` |
| Port not routed | Gunicorn running on 8000 but Railway proxy has no target port | Need to set Edit Port → 8000 in Networking UI |

---

## Architecture

```
moiat_plan_50/
├── Dockerfile              # python:3.11-slim, installs pango/cairo for WeasyPrint
├── start.sh                # entrypoint: migrate + gunicorn on $PORT (fallback 8000)
├── railway.json            # builder: DOCKERFILE, healthcheck: /
├── requirements.txt        # Django, WeasyPrint, gunicorn, psycopg2, whitenoise, dj-database-url, python-dotenv
├── .env                    # local only (gitignored): DEBUG=True, SECRET_KEY, ALLOWED_HOSTS
├── moiat_plan_50/
│   ├── settings.py         # reads from env vars via python-dotenv
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
- [ ] **CRITICAL:** Set Edit Port → 8000 in Railway Networking to make app live
- [ ] Create superuser via Railway shell once live
- [ ] Add PostgreSQL plugin for persistent data (SQLite is ephemeral on Railway)
- [ ] Test full user flow on production
- [ ] Test PDF download (WeasyPrint + pango/cairo already in Dockerfile)
- [ ] Set `ALLOWED_HOSTS` to exact Railway domain in Variables if getting 400 errors
