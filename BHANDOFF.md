# BHANDOFF – 1Step („Една крачка") · Business

Business / non-technical handoff. Product strategy, market, monetization, validation,
GTM. (For code, deploy, env vars → `HANDOFF.md`.) Items marked **[ФОУНДЪР]** need your
input — don't treat placeholders as decided.

---

## One-liner
**„Една крачка. Всеки ден."** — a calm daily health companion for Bulgarians **50+**
that shows **one** small step at a time instead of overwhelming plans, dashboards, or
medical jargon.

## The insight / problem
People 50+ want to feel better but are put off by health apps that feel like a
dashboard, an admin panel, or a doctor's office. Overwhelm → no action. 1Step's bet:
**one small step a day beats a perfect plan nobody follows.**

## Target user (persona)
- Bulgarian, 50+, wants more energy / movement / social contact, not "fitness".
- Low tolerance for complexity, small screens, medical tone. Values warmth and calm.
- **[ФОУНДЪР]** primary segment to focus first (e.g. active retirees vs. still-working 50s)?

## Value proposition & differentiation
- **Calm, single step** (not a to-do list / dashboard) — the core wedge.
- **Human, warm, Bulgarian-native** tone; large type; big targets; no red/alarm colors.
- **Non-medical, safe** — „общи препоръки", clear disclaimer, consult-a-doctor.
- Optional **AI companion** frames the day's one step personally.
- **[ФОУНДЪР]** the sharpest 1-sentence differentiator vs. "just use a habit app"?

## Business model / monetization (HYPOTHESES — validating now)
- Built-in willingness-to-pay probe: feedback form asks **would_pay** + **suggested_price**
  (buckets: безплатно / 1–5 / 5–10 / 10–20 / 20+ лв).
- Candidate models (unvalidated): freemium (free daily step; paid = full plan/PDF,
  progress history, AI companion, reminders); one-off PDF; low monthly sub; B2B2C
  (pensioner clubs, pharmacies, insurers, employers of 50+ workforce).
- **[ФОУНДЪР]** target price point & model to test first? free-tier boundary?

## Validation — what to measure (MVP goal is learning, not revenue)
Funnel + retention + willingness-to-pay. Data is in Django admin (`/admin/`):
- **Acquisition→activation:** home visits → interview starts → interview completes
  (`QuestionnaireResponse`) → first step done (`StepCompletion`).
- **Core ritual retention:** returning days, **streak** (the north-star for the concept).
- **Monetization signal:** % `would_pay = yes`, price distribution.
- **Qual:** `most_useful_part`, `improvement_suggestion`, feedback scores.
- **[ФОУНДЪР]** success thresholds (e.g. "≥40% complete interview", "≥X% would_pay",
  "≥Y% return day-2") that decide go / pivot / stop.
- **Gap:** no funnel analytics yet (only DB records) — see TODO.

## Go-to-market / channels (IDEAS — pick & test)
- Communities of 50+: pensioner clubs, читалища, church/community groups, Facebook groups.
- Adult children buying/sharing it for parents (gift/for-my-mum angle).
- Partnerships: pharmacies, GPs, physiotherapists, health-food shops.
- Content: short Bulgarian tips ("днешната ти крачка"), reels, local press.
- **[ФОУНДЪР]** first channel to run a real test on + budget?

## Competitive landscape
- **[ФОУНДЪР]** name the real alternatives users use today (habit apps, YouTube,
  nothing, a notebook, family nagging) and why 1Step wins for this audience.

## Positioning / messaging (current live copy)
- Hero: „Една крачка към по-добър живот. Всеки ден." · CTA „Направи първата крачка".
- Reassurance: „Не е нужно да направиш всичко. Достатъчна е една крачка."
- **[ФОУНДЪР]** brand name final? („1Step" vs „Една крачка" — currently both in use).

## Legal / trust (business view; tech in HANDOFF)
- Health data (age, weight, health notes) = **GDPR special category** → consent checkbox
  + `/privacy` page already live.
- **[ФОУНДЪР] / action:** privacy-policy **contact email** still a placeholder — fill before
  any real marketing push. Decide data controller identity (personal vs. company/ЕООД).
- Not medical advice — disclaimer present; keep all copy in "general wellbeing" language.

## Roadmap (business milestones, not features)
1. **Now:** validate the ritual concept — interview→step→return funnel + would_pay, on real 50+ users.
2. Enable AI companion + reminders if they lift retention.
3. Decide monetization from price signal; run a paid test.
4. Partnership pilot (one club/pharmacy) if organic signal is positive.
- **[ФОУНДЪР]** timeline & the ONE metric that unlocks each step.

## Open questions / risks
- Will 50+ users adopt a phone-first daily ritual, or need SMS/print/family involvement?
- Retention beyond novelty — does the streak actually pull people back?
- Willingness to pay in the BG 50+ market at any price.
- Distribution: reaching 50+ cost-effectively.
- **[ФОУНДЪР]** biggest single risk you'd de-risk first.

## Stakeholders / contacts
- Founder: Peter Stoyanov (peterstoyanov83@gmail.com)
- **[ФОУНДЪР]** collaborators, advisors, pilot partners.
