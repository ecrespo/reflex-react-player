# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-10-25

### Changed
- **Requires Reflex ≥ 0.10.0 and Python ≥ 3.11** (Reflex 0.10 dropped 3.10).
  Tested on Python 3.11, 3.12, 3.13 and 3.14.
- Regenerated `react_player.pyi` with the Reflex 0.10 stub generator
  (`python -m reflex_base.utils.pyi_generator`); `reflex component build` was
  removed in Reflex 0.10.
- Demo: theme moved from `rx.App(theme=...)` (deprecated) to
  `rx.plugins.RadixThemesPlugin` in `rxconfig.py`; sitemap plugin disabled
  explicitly.
- Build backend requires `setuptools>=78.1.1`; license declared as an SPDX
  expression (`Apache-2.0`).

### CI / release
- GitHub Actions upgraded to Node 24 runtimes (`checkout@v7`,
  `setup-python@v7`, `setup-node@v7`, `upload-artifact@v7`,
  `download-artifact@v8`); new demo job builds the frontend on Node 24.
- New `publish.yml`: pushing a `vX.Y.Z` tag tests, builds and publishes to PyPI
  via Trusted Publishing.

## [0.1.0] — 2026-06-21

### Added
- Initial release: `ReactPlayer` Reflex component wrapping `react-player@3.4.0`
  (`NoSSRComponent`, default export).
- Full prop surface: `src`, `playing`, `loop`, `controls`, `light`, `volume`,
  `muted`, `playback_rate`, `pip`, `plays_inline`, `width`, `height` (plus
  Reflex's built-in `style`, not redeclared — see ADR-7),
  native passthrough attrs, light/preview props, and per-player `config`.
- Event triggers delivering serializable media-state dicts: `on_play`,
  `on_pause`, `on_ended`, `on_progress`, `on_time_update`, `on_duration_change`,
  `on_seeking`, `on_seeked`, `on_waiting`, `on_playing`, `on_rate_change`,
  `on_volume_change`, `on_ready`, `on_start`, `on_error`, PiP and preview events.
- `controls` helpers for imperative ref-based control (play, pause, seek,
  volume, rate, fullscreen, time/duration read-back).
- Demo app reproducing the official react-player examples.
- Spec-Driven Design documents under `docs/sdd/`.
- Apache-2.0 license, packaging (`pyproject.toml`), smoke tests.

### Packaging (publish-readiness)
- Aligned `pyproject.toml` with the official `reflex component init` template:
  added the required `reflex-custom-components` keyword (Reflex gallery / PyPI
  discovery), set `requires-python >=3.10` (Reflex 0.9 dropped 3.9), and added
  `wheel` to the build-system requires.
- Build with `reflex component build` (or `uv build`); publish with `uv publish`.

### Known limitations
- v3 does not yet support DailyMotion, SoundCloud, Streamable, Facebook,
  Mixcloud, or Kaltura.
