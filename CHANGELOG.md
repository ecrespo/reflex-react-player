# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-06-21

### Added
- Initial release: `ReactPlayer` Reflex component wrapping `react-player@3.4.0`
  (`NoSSRComponent`, default export).
- Full prop surface: `src`, `playing`, `loop`, `controls`, `light`, `volume`,
  `muted`, `playback_rate`, `pip`, `plays_inline`, `width`, `height`, `style`,
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

### Known limitations
- v3 does not yet support DailyMotion, SoundCloud, Streamable, Facebook,
  Mixcloud, or Kaltura.
