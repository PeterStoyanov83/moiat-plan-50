# 7 — AI Planner Engine

> Source of truth: [`../CONSTITUTION.md`](../CONSTITUTION.md). Single responsibility:
> **compose the daily plan.** It orchestrates the other engines' outputs into one calm,
> personalized morning — it does not redefine their rules.

## Responsibility
Every morning, generate the user's day in a way that removes overwhelm and always
explains WHY.

## Rules (binding)
The morning generation produces exactly:
- **Today's One Step** (the single smallest realistic action),
- **Three concrete actions**,
- **One optional mission**,
- **One explanation** (the WHY),
- **One reflection question**.

Tone is warm, calm, human. **Never overwhelm, never shame.** Prefer consistency over intensity.

## Inputs considered
current level · age · medical limitations (contraindications) · weather · season ·
history · wearables · completion history · recovery state · habit stability · tree state.

## Current implementation
- `plans/ai_companion.py` — Claude (Haiku) picks a step + writes a warm line; **falls back
  to rule-based** when the API/key is absent.
- `plans/daily.py::today_actions()` — the rule-based 3-action selection (core first + a
  mission), level-scaled, each with its `why`. Rendered in `ritual.html` (task + why).
- **Gap vs spec:** does not yet incorporate weather, contraindications, habit stability,
  or emit a **reflection question**; "one optional mission" is not yet distinct from the 3.

## Boundaries (do NOT do here)
- Difficulty scaling → Behavior. Verification → Verification. Promotion → Level.
- The planner **reads** those outputs; it must not reimplement them.

## Open / next
- `/api/today` producing the full morning payload (one step + 3 actions + mission +
  explanation + reflection question).
- Feed weather/season + `contraindications` + `HabitStability` into selection.
- Persist the reflection answer (storage decision) for the AI to learn from.

## Security (binding for any endpoint that sends user text to the LLM)

User text that reaches the model is **untrusted input**. Every AI-facing endpoint (the
reflection learning loop today; a chat tomorrow) MUST:

1. **Auth + isolation** — session/authenticated; a user reaches only their own data. The
   prompt NEVER contains another user's data, secrets, API keys, or internal ids.
2. **Input bounds** — cap message length and how many prior messages/answers are fed
   (server-side; client caps are bypassable via the API). *Done for reflect:*
   `MAX_ANSWER`/`MAX_QUESTION` on store + `PROMPT_ANSWER_CAP` on what's fed to the prompt.
3. **Rate limiting + cost caps** — per-user rate + daily cap (Claude calls cost money →
   spam = DoS/cost attack); `max_tokens` cap, timeout, Haiku tier, cache per day where
   possible. *Gap:* the companion call currently runs on every ritual load — add a per-day
   cache / rate limit before a chat ships.
4. **Prompt-injection resistance** — user content is clearly delimited and labelled
   untrusted; the system prompt ignores instructions embedded in it; the model has **no
   tools, no DB, no actions** — it only returns text. Output is schema/format-constrained.
5. **Output is escaped** — render model output as text, never raw HTML (XSS). Django
   auto-escaping stays on; no `|safe` on model output.
6. **Scope + safety** — stays in general-wellbeing tone, not medical advice; gentle refusal
   for harmful/off-scope requests; graceful fallback on any failure (never break the ritual).
7. **CSRF (web) / token auth (mobile)**; POST only. Health-category text → same GDPR
   handling; never forward user text to analytics.
