# PRD — reflex-react-player

**Status:** Approved · **Owner:** Ernesto Crespo · **Last updated:** 2026-06-21
**Audience:** Maintainers, contributors, and Reflex developers evaluating the library.

## 1. Problem & context

Reflex (https://reflex.dev) lets developers build full-stack web apps in pure
Python. It has no first-party, full-featured media player. Developers who need to
embed YouTube/Vimeo/HLS/file playback must hand-wrap a React library, which
requires knowledge of Reflex's React-interop internals (NoSSR, default exports,
event arg specs, refs). This is a recurring, non-trivial barrier.

[`react-player` v3](https://github.com/cookpete/react-player) is the de-facto
React media player: a single component that inspects a URL and loads the right
provider (file, audio, HLS, DASH, YouTube, Vimeo, Wistia, Mux, Spotify, Twitch,
TikTok). Wrapping it once, correctly, as a reusable Reflex component removes the
barrier for everyone.

## 2. Goals

- **G1** — Provide a Reflex component that embeds react-player v3 with a Pythonic,
  typed API.
- **G2** — Expose react-player's full prop surface (playback, layout, light mode,
  per-player config).
- **G3** — Expose react-player's events as Reflex event handlers that deliver
  serializable, useful payloads (media state), not raw browser events.
- **G4** — Provide imperative control (play, pause, seek, fullscreen, volume,
  rate) from Python.
- **G5** — Ship a demo app reproducing **all** official react-player examples.
- **G6** — Be installable (`pip install reflex-react-player`) and importable
  (`from reflex_react_player import react_player`).

## 3. Non-goals (out of scope)

- **N1** — Re-implementing media playback ourselves; we wrap react-player.
- **N2** — Supporting react-player **v2** providers not yet ported to v3
  (DailyMotion, SoundCloud, Streamable, Facebook, Mixcloud, Kaltura). Documented
  as a limitation.
- **N3** — A custom skinned controls UI (Media Chrome). Out of scope for v0.1;
  noted as a future enhancement.
- **N4** — Server-side rendering of the player (impossible; react-player is
  client-only).
- **N5** — Mobile-native playback (this is web only).

## 4. Users & use cases

- **Reflex app developer** embeds a YouTube video on a marketing page with custom
  play/pause buttons.
- **Course/LMS builder** plays HLS lecture streams and tracks watched progress
  via `on_time_update`.
- **Podcast/audio app** plays MP3 files with a volume slider and seek bar.
- **Dashboard builder** shows a Mux/Wistia stream with a light-mode thumbnail.

## 5. Requirements

Priority: **MUST** (v0.1), **SHOULD** (near-term), **MAY** (future).

### Functional

| ID | Priority | Requirement | Acceptance criteria |
|----|----------|-------------|---------------------|
| FR-1 | MUST | Render react-player via `react_player(src=...)` | Component mounts client-side; a YouTube/file URL plays. |
| FR-2 | MUST | Controlled playback props: `playing`, `loop`, `controls`, `muted`, `volume`, `playback_rate` | Toggling each Python value changes player behavior. |
| FR-3 | MUST | `src` switching across providers | Loading a YouTube, file, HLS and Vimeo URL each plays. |
| FR-4 | MUST | Layout props: `width`, `height`, `style` | Player respects 16:9 responsive style. |
| FR-5 | MUST | Light (thumbnail) mode via `light` (bool or image URL) | Thumbnail shows; click starts playback. |
| FR-6 | MUST | Per-player `config` dict | YouTube/Vimeo color config applies. |
| FR-7 | MUST | Events: `on_ready`, `on_play`, `on_pause`, `on_ended`, `on_error` | Each fires and updates demo state. |
| FR-8 | MUST | Progress events: `on_progress` (loaded), `on_time_update` (played), `on_duration_change` | Played & Loaded bars and duration update live. |
| FR-9 | MUST | Imperative control from Python: play, pause, seek absolute/relative/fraction, fullscreen, set volume, set rate | Buttons in demo perform each action. |
| FR-10 | MUST | Picture-in-Picture via `pip` + enter/leave events | PiP toggles where supported. |
| FR-11 | SHOULD | Read `currentTime`/`duration` back into Python via callback | `controls.get_current_time(id, cb)` returns a float. |
| FR-12 | SHOULD | Seek/transport events: `on_seeking`, `on_seeked`, `on_waiting`, `on_playing`, `on_rate_change`, `on_volume_change` | Available as handlers. |
| FR-13 | MAY | Native `<source>`/`<track>` children support | Documented usage. |

### Non-functional

| ID | Priority | Requirement |
|----|----------|-------------|
| NFR-1 | MUST | Pin `react-player@3.x` for reproducible builds. |
| NFR-2 | MUST | Component is `NoSSRComponent` (client-only). |
| NFR-3 | MUST | `is_default = True` (react-player default export). |
| NFR-4 | MUST | Works with Reflex ≥ 0.8.0 and Python ≥ 3.9. |
| NFR-5 | SHOULD | Smoke tests for wiring, prop rendering, event triggers. |
| NFR-6 | SHOULD | Apache-2.0 license (matches Reflex ecosystem). |

## 6. Success metrics

- A new user can install and render a working YouTube player in under 5 minutes
  following the README quickstart.
- The demo app exercises every MUST requirement on one page.
- `reflex run` in the demo builds the frontend with no JS "Invalid Element Type"
  errors (the canonical default-export/NoSSR failure mode).

## 7. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| react-player v3 dep churn breaks the build | Pin exact version; document upgrade procedure. |
| Reflex internal API (Var/event specs) shifts between releases | Use documented public API where possible; pin a known-good Reflex floor; cover with tests. |
| Refs under NoSSR are null before mount | Helpers use optional chaining; read only after `on_ready`. |
| Unsupported v2 providers confuse users | Explicit limitations section in README + PRD N2. |
