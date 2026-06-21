# Implementation Plan — reflex-react-player

**Status:** Approved · **Owner:** Ernesto Crespo · **Last updated:** 2026-06-21
**Audience:** Maintainers tracking delivery.

Phases are sequenced; each has verifiable **Done** criteria. References to specs:
PRD (`01-prd.md`), Architecture (`02-architecture.md`), Component Spec
(`03-component-spec.md`).

## Phase 0 — Research & SDD baseline
**Scope:** Read react-player v3 source (props/events/methods/examples) and Reflex
custom-component docs (NoSSR, default export, event arg specs, refs, packaging).
Author all SDD documents. Initialize the repo on `main`.
**Done when:**
- [x] react-player v3 surface documented (props, events, ref API, providers).
- [x] Reflex wrapping approach documented.
- [x] `docs/sdd/00..05` written; README drafted.
- [x] Git repo initialized on `main` with baseline commit.

## Phase 1 — Core component wrapper
**Scope:** `ReactPlayer(NoSSRComponent)` with `library`, `tag`, `alias`,
`is_default=True`, and all controlled/layout/native/light/config props (FR-1..6,
NFR-1..3).
**Done when:**
- [x] All props from `03-component-spec.md` §2 declared as typed `rx.Var`.
- [x] `_rename_props` maps non-camelCase names.
- [x] `react_player = ReactPlayer.create` exported.

## Phase 2 — Events & state contract
**Scope:** Declare every event trigger with arg specs that extract a serializable
media-state dict (ADR-3); `on_duration_change`→float, `on_error`→str, no-arg
events (FR-7, FR-8, FR-12).
**Done when:**
- [x] All events from `03-component-spec.md` §3 exposed.
- [x] Media-state extraction implemented in `_media_state_spec`.
- [x] Payload shape matches the spec.

## Phase 3 — Imperative control helpers
**Scope:** `controls.py` with play/pause/seek (absolute/relative/fraction)/
volume/rate/fullscreen and read-back helpers via `rx.call_script` + refs
(FR-9, FR-11; ADR-4).
**Done when:**
- [x] All helpers from `03-component-spec.md` §4 implemented with defensive `?.`.
- [x] Read helpers accept a `callback`.

## Phase 4 — Demo application
**Scope:** A Reflex app reproducing the official react-player demo: provider
source switcher, transport controls, speed buttons, seek slider, volume slider,
controls/muted/loop/light toggles, Played + Loaded progress bars, time readout,
custom-URL loader (FR-3, G5).
**Done when:**
- [x] Demo renders the player + all controls on one page.
- [x] Every MUST event drives visible state.
- [ ] Manual QA: at least one file, HLS, DASH, YouTube, Vimeo source plays.

## Phase 5 — Packaging & docs
**Scope:** `pyproject.toml` (setuptools, `custom_components` package dir),
LICENSE (Apache-2.0), `.gitignore`, README quickstart + API tables, CHANGELOG
(G6, NFR-6).
**Done when:**
- [x] `python -m build` produces sdist + wheel.
- [x] README documents install, quickstart, props, events, helpers, limitations.

## Phase 6 — Verification & publish
**Scope:** Smoke tests; demo build smoke; create public GitHub repo and push
`main`; (optional) publish to PyPI.
**Done when:**
- [x] `pytest` passes (component wiring, prop rendering, triggers, helpers).
- [ ] `reflex run` in the demo builds the frontend with no Invalid-Element-Type
      error (requires Node; run on a dev machine).
- [ ] Public GitHub repo created and `main` pushed.
- [ ] (Optional) `reflex-react-player` published to PyPI.

## Definition of Done (every PR)
- Behavioral changes update the relevant SDD doc in the same PR.
- New props/events are reflected in `03-component-spec.md` and the tests.
- README examples remain runnable.
