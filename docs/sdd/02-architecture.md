# Architecture / Technical Design — reflex-react-player

**Status:** Approved · **Owner:** Ernesto Crespo · **Last updated:** 2026-06-21
**Audience:** Contributors implementing or reviewing the component internals.

## 1. Context

Reflex compiles Python components into a Next.js/React frontend and runs a Python
backend that holds application state. A "custom component" is a Python class that
emits a specific React import + JSX. Our job is to map react-player v3's React
surface onto Reflex's component model correctly.

## 2. High-level architecture

```
┌─────────────────────────── Reflex app (Python) ───────────────────────────┐
│  State (rx.State)                                                            │
│   ├─ controlled values: src, playing, volume, ...                           │
│   └─ event handlers: handle_progress, handle_time_update, ...               │
│                          │  props ▼            ▲ events (serialized dict)    │
│  ReactPlayer(NoSSRComponent)  ──────────────────────────────────────────┐  │
└───────────────────────────────────────────────────────────────────────┼──┘
                                                                          │ compiles to
                                  ▼                                       │
┌─────────────────────────── Next.js frontend (React) ──────────────────────┐
│  dynamic(() => import('react-player'), { ssr:false })                       │
│   └─ <ReactPlayer src=... onTimeUpdate=... ref=... />                        │
│        └─ lazy-loads provider element (youtube-video-element, hls, ...)      │
│             └─ underlying HTMLMediaElement / iframe SDK                      │
│  refs['ref_<id>'].current  ──► imperative API (currentTime, play(), ...)    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. Key design decisions (ADRs)

### ADR-1 — Subclass `NoSSRComponent`
**Context:** react-player instantiates browser SDKs and references `window`.
SSR would crash with `window is not defined`.
**Decision:** Subclass `reflex.components.component.NoSSRComponent`, which makes
Reflex emit `dynamic(() => import(...), { ssr: false })`.
**Consequences:** The player only renders on the client. A forwarded `ref` points
at a Next.js "loadable" wrapper until the client mounts the real element — reads
must be guarded (see ADR-4). Alternatives (manual `is_dynamic`/`ssr=False` on
`rx.Component`) are equivalent but less idiomatic.

### ADR-2 — `is_default = True`
**Context:** react-player is the package's **default** export
(`import ReactPlayer from 'react-player'`).
**Decision:** Set `is_default = True` so Reflex generates a default import.
**Consequences:** Omitting this produces a named import `{ ReactPlayer }` =
`undefined` → React "Element type is invalid" error. This is the single most
common failure mode and is covered by `test_library_wiring`.

### ADR-3 — Events deliver serializable media-state dicts, not SyntheticEvents
**Context:** react-player v3 forwards native React `SyntheticEvent`s to most
callbacks. These are not JSON-serializable, so sending them to the Python backend
yields empty/garbage payloads.
**Decision:** Each event uses an **arg spec** that, on the client, extracts a
small plain object from `event.target` (the `HTMLMediaElement`): `current_time`,
`duration`, `played` (0..1), `played_seconds`, `loaded` (0..1), `loaded_seconds`,
`playback_rate`, `volume`, `muted`, `paused`. `on_duration_change` sends a float;
`on_error` sends a best-effort message string; `on_ready`/`on_start`/PiP send no
args.
**Consequences:** Python handlers receive ergonomic, typed data. The extraction
JS lives in `react_player.py` (`_media_state_spec`). The payload shape is part of
the public contract (`03-component-spec.md`).

### ADR-4 — Imperative control via refs + `rx.call_script`
**Context:** react-player v3 removed method-style getters; the ref *is* the
`HTMLMediaElement`. Reflex cannot hold a JS ref server-side.
**Decision:** Components are given an `id`; Reflex exposes the ref globally as
`refs['ref_<id>'].current`. Helper functions in `controls.py` return
`rx.call_script(...)` events that read/write that element (`currentTime`,
`play()`, `pause()`, `requestFullscreen()`, `volume`, `playbackRate`). Reads use a
`callback=` to return values to the backend.
**Consequences:** Imperative control is decoupled from the component instance and
works from any event handler. All JS uses optional chaining (`?.`) because the
ref is null before mount (ADR-1).

### ADR-5 — snake_case → camelCase, minimal `_rename_props`
**Context:** Reflex auto-camelCases prop names (`playback_rate` → `playbackRate`).
**Decision:** Rely on auto-conversion for nearly all props; use `_rename_props`
only for names that don't camelCase cleanly (`o_embed_url` → `oEmbedUrl`).
**Consequences:** Minimal surprise; the component reads like idiomatic Reflex.

### ADR-6 — Pin `react-player@3.4.0`
**Context:** v3 transitive deps (provider web-components) are still evolving;
mismatches cause "Invalid Element Type" / loadable errors.
**Decision:** Pin an exact version in `library`. Bumps are deliberate and tested.

### ADR-7 — Do not declare a `style` prop
**Context:** `style` is a built-in field on every Reflex component. Declaring
`style: rx.Var[dict]` on the subclass overrides it with a `None` default and
breaks `Component._post_init` (`TypeError: 'NoneType' object is not a mapping`)
on Reflex ≥ 0.9. **Decision:** Layout uses `width`/`height` props plus the
built-in `style`; the component declares no `style` prop. Covered by
`tests/test_props.py::test_no_style_prop_declared`.

### ADR-8 — Target Reflex 0.10; build and release without `reflex component`
**Context:** Reflex 0.10 requires Python ≥ 3.11 and removed the
`reflex component` CLI (`init`/`build`/`publish`/`share`); the official
component template now builds with standard tooling and publishes from CI.
**Decision:** Depend on `reflex>=0.10.0`, `requires-python >=3.11`. Keep the
setuptools layout and the committed `react_player.pyi`, regenerated with
`python -m reflex_base.utils.pyi_generator`. Build with `python -m build`;
publish via GitHub Actions Trusted Publishing on `v*` tags (`publish.yml`, which
verifies tag == `pyproject` version). The demo configures its theme through
`rx.plugins.RadixThemesPlugin`, and CI compiles it with Node 24.

## 4. Module layout

```
custom_components/reflex_react_player/
├── __init__.py        # public API: react_player, ReactPlayer, controls
├── react_player.py    # ReactPlayer(NoSSRComponent) + event arg specs
└── controls.py        # imperative ref helpers (rx.call_script)
```

## 5. Data / payload shapes

The "media state" dict delivered to most event handlers:

```python
{
  "current_time": float,    # seconds
  "duration": float,        # seconds (0 until known)
  "played": float,          # 0..1
  "played_seconds": float,
  "loaded": float,          # 0..1 (buffered)
  "loaded_seconds": float,
  "playback_rate": float,
  "volume": float,          # 0..1
  "muted": bool,
  "paused": bool,
}
```

## 6. Error handling

- Playback errors surface through `on_error(message: str)`.
- Ref reads are defensive; a missing element yields safe defaults (zeros).
- Provider selection is react-player's responsibility; an unsupported URL simply
  doesn't match a player and falls back to the native element / errors.

## 7. Security / privacy

- No backend network calls are added by the component; media is fetched
  client-side by the provider SDKs.
- `o_embed_url` (light mode thumbnails) defaults to react-player's endpoint; apps
  may override it.

## 8. Performance

- Providers are lazy-loaded by react-player (separate chunks), so only the active
  provider's code is downloaded.
- `on_time_update` fires frequently (native cadence). Handlers should keep work
  light; the demo only assigns fields. Apps that don't need per-frame updates can
  omit the handler.

## 9. Future enhancements

- Optional Media Chrome skin (custom controls UI).
- Helper for `<source>`/`<track>` children (multi-source, captions).
