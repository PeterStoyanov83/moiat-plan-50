# Design-System Prompt for Fable 5 — "1Step"

Paste everything under the line into Fable 5. It is written so Fable 5 *formalizes and
elevates the existing look* (green/nature, Nunito, rounded cards) rather than inventing a
new brand — and hardens it for the 50+ audience (large type, high contrast, big targets).

---

## ROLE
You are a senior product designer building a **design system** for a web app aimed at
**Bulgarian adults aged 50+**. Output must be practical and implementation-ready:
design tokens + component specs + a few page compositions. Prioritize **accessibility and
warmth** over trendiness.

## PRODUCT CONTEXT
"1Step" is a Django web app that generates a personalized **7-day health plan**
(movement, nutrition, daily habits, one social task, one finance habit) after an 18-question
questionnaire. Tone: encouraging, calm, respectful, never clinical or patronizing. All UI
copy is in **Bulgarian**. It is *not* medical advice — a disclaimer is always present.

## AUDIENCE CONSTRAINTS (non-negotiable)
- Base body text **≥ 18px (1.1rem)**; primary actions **≥ 20px**. Never go below 16px.
- **Touch/click targets ≥ 48×48px**, generous spacing between them.
- Color contrast **WCAG AA minimum, target AAA** for body text.
- One primary action per screen; avoid dense multi-column forms.
- No reliance on hover to reveal meaning; no tiny icons as sole labels.
- Plain, reassuring language. Support left-to-right long Bulgarian words without clipping.

## BRAND STARTING POINT (extend these — do not replace the hues)
Current tokens already in production — treat as the seed of the system and fill the gaps
(hover/active/disabled, surfaces, semantic states, dark-on-light pairings):
```
--primary:        #2E7D32   (green)      hover/active: #1B5E20
--primary-light:  #4CAF50
--accent:         #FF8F00   (warm orange) hover/active: #E65100
--bg:             #F9FBF9   (off-white green tint)
--text:           #2c3e50
--muted:          #6c757d
--card-bg:        #ffffff
gradients: #E8F5E9 → #F1F8E9 (calm), #FFF8E1 → #FFF3E0 (goal/attention)
font: 'Nunito' (400/600/700/800); headings 800
cards: radius 16px, shadow 0 4px 20px rgba(0,0,0,0.07)
buttons: pill (radius 50px)
```
Framework in use: **Bootstrap 5** + a small custom CSS layer. Keep the system expressible
as CSS custom properties + utility classes that sit on top of Bootstrap.

## DELIVERABLES
1. **Design tokens** — full set, as CSS custom properties AND a JSON token map:
   - Color: brand, surfaces, text (default/muted/inverse), border, and **semantic**
     (success/warning/danger/info) each with a WCAG-checked on-color. Include a contrast
     note (ratio) for every text-on-surface pairing.
   - Typography: a modular scale (display, h1–h4, body-lg, body, small) with px + rem,
     line-heights (body ~1.7–1.8), and weights. Nunito.
   - Spacing scale (4px base), radius scale, shadow scale (2–3 elevations), max content
     width (~860px), and focus-ring spec (visible, ≥3:1 against background).
   - Motion: durations/easings for subtle feedback only (150–250ms), plus a
     `prefers-reduced-motion` fallback.
2. **Components** (states: default / hover / active / focus / disabled / error where
   relevant; each with a11y notes):
   - Buttons: primary (green), accent (orange), tertiary/ghost, and a large "next" CTA.
   - Form controls: text input, textarea, select, and **large radio & checkbox** styled as
     tappable cards (the questionnaire is all radios/checkboxes) with clear selected state.
   - Question block / step card (with the existing 48px circular step-number badge).
   - Content card (`card-custom`) + section header with emoji icon.
   - Progress indicator for the 18-question flow (step X of N).
   - Disclaimer / callout (info, warning, success variants).
   - Navbar and footer.
   - Result "plan section" cards for the 6 areas (nutrition 🥗, movement 🚶, habits ✨,
     finance 💰, social 🤝, 90-day goal 🎯) and a **level badge** (Ниво: Старт / Базова
     форма / Активни 50+).
3. **Page compositions** (desktop + mobile, annotated):
   - Home / hero with single clear "Започни моя план" CTA.
   - Questionnaire step (one question focus, progress, big radio cards, back/next).
   - Result page (profile header, the 6 plan cards, level badges, PDF + feedback CTAs).
   - A **print/PDF theme** note (the plan is exported via WeasyPrint — high-contrast,
     no gradients required, A4-friendly).
4. **Accessibility checklist** the build can verify against (contrast, target size, focus
   order, reduced motion, font-size floors).
5. **Do / Don't** examples specific to a 50+ audience.

## OUTPUT FORMAT
- Start with a 3–4 sentence design rationale (why these choices suit 50+ Bulgarian users).
- Then tokens (CSS vars + JSON), then components, then page compositions, then the
  a11y checklist. Use tables for token values. Keep it copy-pasteable.
- Every color pairing used for text must state its contrast ratio.

## EXPLICITLY OUT OF SCOPE
No rebrand of the green identity, no new logo, no marketing illustration system, no
backend/code — this is a visual design system to hand to a Django + Bootstrap build.
