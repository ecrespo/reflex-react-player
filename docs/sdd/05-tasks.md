# Tasks — reflex-react-player

**Status:** Living · **Owner:** Ernesto Crespo · **Last updated:** 2026-06-21

Granular, trackable work items mapped to phases (`04-plan.md`) and requirements
(`01-prd.md`). `[x]` done · `[ ]` open.

## Phase 0 — Research & SDD baseline
- [x] T0.1 Extract react-player v3 props/defaults from source. (FR-2,4,5,6)
- [x] T0.2 Extract v3 event names + payloads + ref API. (FR-7,8,9)
- [x] T0.3 Confirm Reflex NoSSR + default-export + arg-spec + ref patterns.
- [x] T0.4 Write `00-overview`, `01-prd`, `02-architecture`, `03-component-spec`, `04-plan`, `05-tasks`.
- [x] T0.5 `git init`, set `main`, baseline commit.

## Phase 1 — Core component
- [x] T1.1 Define class wiring (`library`, `tag`, `alias`, `is_default`). (NFR-1,3)
- [x] T1.2 Declare playback props. (FR-2)
- [x] T1.3 Declare layout props (`width`, `height`, `style`). (FR-4)
- [x] T1.4 Declare light/preview props. (FR-5)
- [x] T1.5 Declare native passthrough props (autoPlay, preload, poster, ...).
- [x] T1.6 Declare `config` prop. (FR-6)
- [x] T1.7 `_rename_props` for `o_embed_url`. (ADR-5)
- [x] T1.8 Export `react_player` factory.

## Phase 2 — Events
- [x] T2.1 Implement `_media_state_spec` extraction JS. (ADR-3)
- [x] T2.2 Implement `_duration_spec`, `_error_spec`, `_empty_spec`.
- [x] T2.3 Wire all event triggers. (FR-7,8,12, FR-10)

## Phase 3 — Imperative control
- [x] T3.1 `play`, `pause`. (FR-9)
- [x] T3.2 `seek_to`, `seek_relative`, `seek_fraction`. (FR-9)
- [x] T3.3 `set_volume`, `set_playback_rate`, `request_fullscreen`. (FR-9)
- [x] T3.4 `get_current_time`, `get_duration` with callback. (FR-11)

## Phase 4 — Demo
- [x] T4.1 `PlayerState` with controlled fields + handlers.
- [x] T4.2 Provider source switcher (file/HLS/DASH/YouTube/Vimeo/Wistia). (FR-3)
- [x] T4.3 Transport controls (stop/play-pause/±10s/fullscreen).
- [x] T4.4 Speed buttons (0.5/1/1.5/2x).
- [x] T4.5 Seek slider + Played/Loaded progress bars. (FR-8)
- [x] T4.6 Volume slider.
- [x] T4.7 Controls/Muted/Loop/Light toggles. (FR-5)
- [x] T4.8 Live state/time readout (elapsed/duration/remaining).
- [ ] T4.9 Manual QA across providers (needs Node + browser). (FR-3)
- [ ] T4.10 Add custom-URL loader input (enhancement).

## Phase 5 — Packaging & docs
- [x] T5.1 `pyproject.toml` (setuptools, package dir). (G6)
- [x] T5.2 LICENSE (Apache-2.0). (NFR-6)
- [x] T5.3 `.gitignore`.
- [x] T5.4 README (install, quickstart, API tables, limitations).
- [x] T5.5 CHANGELOG.
- [ ] T5.6 Type stubs `.pyi` for editor autocomplete. (enhancement)

## Phase 6 — Verification & publish
- [x] T6.1 Smoke tests (`tests/test_component.py`). (NFR-5)
- [ ] T6.2 `python -m build` produces sdist + wheel (run where deps install).
- [ ] T6.3 `reflex run` demo frontend build smoke (needs Node).
- [ ] T6.4 Create public GitHub repo, push `main`.
- [ ] T6.5 (Optional) Publish to PyPI via `twine`.

## Backlog / future
- [ ] B.1 Media Chrome custom-controls skin.
- [ ] B.2 `<source>`/`<track>` children helper (multi-source + captions).
- [ ] B.3 CI workflow (lint + tests) on GitHub Actions.
