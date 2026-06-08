## Purpose

Owns the Ink (React) terminal UI for Hermes — `hermes --tui`. Replaces the classic prompt_toolkit CLI with a modern terminal interface. TypeScript owns the screen; Python owns the agent via JSON-RPC over stdio.

## Ownership

- `src/` — React/Ink components, stores, hooks
- `src/app.tsx` — Root Ink component, route composition
- `src/store/` — Shared nanostores (session, state, theme)
- `tui_gateway/` (sibling dir) — Python JSON-RPC backend
- `src/themes.ts` + `branding.tsx` — Theme/skin integration

## Local Contracts

- TypeScript owns rendering; Python owns sessions, tools, model calls, slash commands
- Transport: newline-delimited JSON-RPC over stdio
- Prefer small nanostores over component state for shared/data
- Route roots are thin — they compose routes and shell
- Components that render from an atom use `useStore`; non-rendering actions read with `$atom.get()`
- No monolithic hooks — one hook = one narrow job
- The main transcript/composer belongs to Ink — do not re-implement in the dashboard
- Dashboard embeds real `hermes --tui` via PTY bridge — not a rewrite

## Work Guidance

- `npm run dev` for watch-mode development
- TypeScript strict mode
- Prettier for formatting, ESLint for linting
- Vitest for tests

## Verification

- `npm test` — vitest suite passes
- `npm run type-check` — tsc with no errors
- `npm run build` — production build succeeds

## Child DOX Index

No child AGENTS.md files in this subtree.
