# Claude Project Instructions — 1Step

## At session start (read first, every session)

To restore context between sessions, read these before doing anything else:

1. **[HANDOFF.md](HANDOFF.md)** — current technical/operational state + what's next.
2. **[BHANDOFF.md](BHANDOFF.md)** — current business/product state + open founder decisions.
3. **[bos/CONSTITUTION.md](bos/CONSTITUTION.md)** and **[bos/STATUS.md](bos/STATUS.md)** — the governing rules and what's built vs. open.

These are the between-sessions memory. Keep `HANDOFF.md` / `BHANDOFF.md` updated at the
end of meaningful work. The per-engine specs in `bos/engines/` are **not** read at startup —
read the specific one on demand, before changing that engine's code (see below).

---

Before making any code changes:

1. Read **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)**.
2. Read every relevant **engine document** (`bos/engines/`).
3. Never implement business logic that contradicts the documentation.
4. Never invent progression rules.
5. Never invent verification logic.
6. Never modify JSON contracts without documenting the change.
7. If implementation reveals a weakness in the design:
   - Do **NOT** silently fix it.
   - Instead: **explain the issue → propose improvements → wait for approval.**

Always think like:

- **Product Architect**
- **Behavioral Psychologist**
- **Senior Software Engineer**
- **UX Designer**

The objective is not to build features.

The objective is to build **the world's best behavioral transformation platform**.

---

## Where the truth lives

This project is governed by the **BOS** (Behavioral Operating System) in [`bos/`](bos/):

- [`bos/CONSTITUTION.md`](bos/CONSTITUTION.md) — the source of truth. **Documentation wins** over code.
- [`bos/README.md`](bos/README.md) — navigation, the engine pipeline, and non-negotiables.
- [`bos/engines/`](bos/engines/) — one single-responsibility spec per engine. **Never mix rules between engines.**
- [`bos/STATUS.md`](bos/STATUS.md) — what's built vs open, mapped to the code.

Operational/technical state: [`HANDOFF.md`](HANDOFF.md). Business/product state: [`BHANDOFF.md`](BHANDOFF.md).
