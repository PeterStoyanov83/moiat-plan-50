# 1Step — Product Transformation Brief (Personal Life Companion)

> Grounded, project-specific version of the redesign brief. Keeps the philosophy;
> corrects it to this codebase (Django, Bulgarian, 50+, one-step ritual already shipped).
> `[DECISION]` = needs a founder call. `[HAVE]` = already built. `[BUILD]` = new.

---

## ROLE
You are lead Product Designer, UX Researcher, Creative Director and **Django** frontend
architect for **1Step / „Една стъпка"**. This is a philosophy shift, not a visual reskin.
The app is a **personal life companion** — it helps people build a better life through
**one small step every day**. Every screen answers: *"How can we make this person feel
better today?"* If an element doesn't, remove it.

## HARD PROJECT CONTEXT (do not violate)
- **Stack:** Django + server-rendered templates. Ritual/progress = standalone **Tailwind (CDN)**;
  home/questionnaire/result/profile/allauth = a calm **Bootstrap-on-cream `base.html`**.
  **No React** — deliver Django templates, views, template partials, and CSS/inline-SVG, not JSX.
- **Audience:** **Bulgarians 50+.** All copy in **Bulgarian**. Accessibility is non-negotiable:
  body ≥ 18px, touch targets ≥ 48px, WCAG AA→AAA, no reliance on hover, respect
  `prefers-reduced-motion`.
- **Not medical.** „Общи препоръки"; disclaimer + GDPR consent + `/privacy` already present.
- **Much of this already exists** — this is a *transformation of what's shipped*, not greenfield.

## EMOTIONAL GOAL
After every session: *„Днес направих нещо добро за себе си."* Calm, warm, human, optimistic,
gentle. Never guilt, never clinical, never "work". Like a kind, wise friend.

## REMOVE THE OLD MENTAL MODEL
Kill any feeling of: calorie counter · diet planner · fitness tracker · medical app ·
dashboard · productivity tool. Replace with: daily guidance · encouragement · reflection ·
growth · emotional wellbeing.

---

## WHAT EXISTS vs WHAT CHANGES (per screen)

| Screen / file | State | Transformation |
|---|---|---|
| **Onboarding** `questionnaire.html` (18-q form) | `[HAVE]` a form | `[BUILD]` **conversational** onboarding — a caring coach, one question per view, warm intros, simple choices. No wall of fields. Prefill name from Google. |
| **Home / ritual** `ritual.html` | `[HAVE]` single-step ritual + „Направих го/Покажи ми друга" + AI greeting line | Keep the one-step model; add **daily inspirational line**, **„защо"** under the step, **Reflection** entry, and the **living tree** (see below). |
| **Progress** `progress.html` | `[HAVE]` streak + 7-day bar chart + recent | `[BUILD]` **replace charts/gamified feel with the living tree** as the primary progress metaphor; keep streak as quiet text. |
| **Full plan / PDF** `result.html`, `pdf_plan.html` | `[HAVE]` 7-day plan | Demote further / reframe as „моят план" reference; ensure it doesn't reintroduce dashboard feel. |
| **Profile / auth** `profile.html`, allauth pages | `[HAVE]` | Keep; ensure calm tone + warm copy. |
| **Base/shell** `base.html`, `templates/allauth/layouts/base.html` | `[HAVE]` cream calm base | Extend palette/typography per design system below. |

`[DECISION]` **One step vs three.** You shipped **one step at a time** (offer next on done);
this brief also mentions "three actions". Decide: (a) **one headline step** (current), or
(b) **one step + up to 3 concrete micro-actions each with a „защо"**. Recommendation: (b) —
one emotional headline, ≤3 tiny actions beneath, each with its reason. Everything below assumes (b) unless you choose (a).

---

## THE DAILY EXPERIENCE (home structure)
Greeting → daily inspirational sentence → **Today's one step** → ≤3 personalized actions
(each: the action **+ защо**) → Reflection button → your growing tree. **Nothing else.**

Every action explains **why** — meaning creates motivation. Example (BG):
- *„Изпий две чаши вода повече днес. Защо? За да поддържаш енергията си."*
- *„Добави белтъчини на обяд. Защо? За да се чувстваш сит по-дълго и да пазиш мускулите си."*

Content comes from the existing **knowledge base** (`plans/data/knowledge_base.json`) via
`step_engine.py`; the **AI companion** (`plans/ai_companion.py`, Claude Haiku) already picks
+ frames the step — extend its system prompt to also emit the „защо" and (optionally) 2 more
micro-actions. Keep the rule-based fallback.

## PROGRESS = A LIVING TREE `[BUILD]`
Remove points/badges. Introduce a **tree that grows** with completed steps: leaves weekly,
flowers monthly, later birds/sunlight. It is a **metaphor for growth, not a reward**.
- Implementation: inline **SVG** tree with stages driven by `today_progress`/total counts;
  gentle CSS/JS growth + sway animations (respect reduced-motion). No real images (Tailwind/CSS only).
- Replaces the bar chart as the emotional centerpiece; streak stays as one quiet line.

## REFLECTION `[BUILD]`
A soft daily prompt („Как се чувстваш днес?") — optional, one tap, never required.
`[DECISION]` store reflections (new tiny model) or keep ephemeral?

---

## DESIGN SYSTEM (use our real tokens)
Japanese minimalism · Scandinavian calm · Apple-Health simplicity · nature · morning light.
Whitespace, rounded cards, soft shadows, large type. Current tokens to standardize/extend:
```
--cream/warm-white: #FBF7EE   card: #FEFCF7
--sage/green:       #4CAF50   forest: #2E7D32 / #1B5E20
--sky-blue accent:  #2F6E8F / #4A90A4 (calm blue)
--muted-gold/sun:   #FFB74D / #C57A1E
--ink: #22302A      muted: #5F6F66
```
No red, no neon, no aggressive contrast. Font: **Nunito** (already in use), large sizes.

## ILLUSTRATION & IMAGERY
No stock fitness photos. **Watercolor-style nature** (trees, tea, books, walking, sunrise,
gardens). NOTE constraint: previews/templates use **CSS + inline SVG only** (no external
images). So: soft hand-drawn **SVG** illustrations + the living tree; if raster watercolor is
wanted later, `[DECISION]` on an asset pipeline (WeasyPrint/static). Icons already are warm,
animated inline SVG (walk/water/friends/sun) — extend that style.

## MICRO-INTERACTIONS
Alive but never flashy: tree grows, leaves sway, sunlight shifts, cards fade up, gentle
transitions, soft check-off, discreet confetti on day complete. All `prefers-reduced-motion` safe.

## COPY / LANGUAGE (Bulgarian, caring)
Never: „Провали се" · „Пропусна целта" · „Трябва да…". Instead: „Винаги можеш да продължиш
утре." · „Всяка стъпка има значение." · „Вече напредна." · „Изграждаш здрави навици."

## AI PERSONALITY
Part psychologist, part wellness coach, part trusted friend. Listens first, advises second,
never judges/pressures/scares. Extend `ai_companion.py` system prompt accordingly; keep it
cheap/fast (Haiku), timeout + graceful fallback.

---

## EXPECTED OUTPUT (Django, not React)
1. UX redesign plan (per-screen, referencing the files above).
2. Information architecture + simplified navigation (Днес · Напредък/Дърво · Спътник · Профил).
3. New user flow (conversational onboarding → daily ritual → reflection → tree).
4. Redesigned screen hierarchy + component/partial hierarchy (Django templates/partials).
5. Design system + palette (extend tokens above) + typography scale + illustration + animation + copy guidelines (all BG).
6. **Django** changes: templates, views, URLs, any small models (reflection, tree state),
   `step_engine`/`ai_companion` extensions — **not** React components.
7. Files to refactor (list from the table) + suggested implementation order + concrete code changes.

Treat as a complete product transformation grounded in the existing Django app — reuse the
step engine, knowledge base, AI companion, and calm shell; don't rebuild from scratch.
