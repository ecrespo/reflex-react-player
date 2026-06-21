# reflex-react-player

A [Reflex](https://reflex.dev) custom component that wraps
[**react-player** v3](https://github.com/cookpete/react-player) — a versatile
media player that plays files, audio, HLS, DASH, YouTube, Vimeo, Wistia, Mux,
Spotify, Twitch and TikTok by inspecting the URL.

It gives you a Pythonic, typed API for props and events, plus imperative control
(play, pause, seek, fullscreen) from your Python event handlers — and ships with
a full demo app reproducing every example from the official react-player demo.

> Built with **Spec-Driven Design**. The full specs (PRD, architecture, component
> contract, plan, tasks) live in [`docs/sdd/`](docs/sdd/).

## Features

- 🎬 One component for many providers — file/audio, HLS (`.m3u8`), DASH (`.mpd`),
  YouTube, Vimeo, Wistia, Mux, Spotify, Twitch, TikTok.
- 🐍 Pythonic props (`snake_case` → `camelCase`), typed with `rx.Var`.
- 🔔 Events that deliver **serializable media-state dicts** (played, loaded,
  duration, ...) — not raw browser events.
- 🎛️ Imperative control helpers: `play`, `pause`, `seek_to`, `seek_relative`,
  `seek_fraction`, `set_volume`, `set_playback_rate`, `request_fullscreen`,
  `get_current_time`, `get_duration`.
- 🌗 Light (thumbnail-first) mode, picture-in-picture, per-player `config`.
- 🧪 Smoke tests + a complete demo app.

## Installation

```bash
pip install reflex-react-player
```

Or install from source (editable) for development:

```bash
git clone https://github.com/ecrespo/reflex-react-player.git
cd reflex-react-player
pip install -e .
```

Requires **Reflex ≥ 0.8.0** and **Python ≥ 3.9**. The npm dependency
(`react-player@3.4.0`) is added to your Reflex project automatically on build.

## Quickstart

```python
import reflex as rx
from reflex_react_player import react_player


class State(rx.State):
    playing: bool = False

    @rx.event
    def toggle(self):
        self.playing = not self.playing


def index() -> rx.Component:
    return rx.vstack(
        react_player(
            id="player",
            src="https://www.youtube.com/watch?v=oUFJJNQGwhk",
            playing=State.playing,
            controls=True,
            width="640px",
            height="360px",
            style={"aspectRatio": "16 / 9"},
        ),
        rx.button("Play / Pause", on_click=State.toggle),
    )


app = rx.App()
app.add_page(index)
```

## Tracking progress (events)

Most events deliver a **media-state dict** with `played` (0..1), `loaded` (0..1),
`played_seconds`, `duration`, etc.

```python
class State(rx.State):
    played: float = 0.0
    loaded: float = 0.0
    duration: float = 0.0

    @rx.event
    def on_time_update(self, s: dict):
        self.played = s["played"]

    @rx.event
    def on_progress(self, s: dict):
        self.loaded = s["loaded"]

    @rx.event
    def on_duration(self, seconds: float):
        self.duration = seconds


react_player(
    id="player",
    src="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",  # HLS
    controls=True,
    on_time_update=State.on_time_update,
    on_progress=State.on_progress,
    on_duration_change=State.on_duration,
)
```

## Imperative control

Give the player an `id`, then drive it from Python:

```python
from reflex_react_player import controls

rx.button("Play",     on_click=controls.play("player"))
rx.button("Pause",    on_click=controls.pause("player"))
rx.button("-10s",     on_click=controls.seek_relative("player", -10))
rx.button("+10s",     on_click=controls.seek_relative("player", 10))
rx.button("Fullscreen", on_click=controls.request_fullscreen("player"))
```

## API reference

See the full contract in
[`docs/sdd/03-component-spec.md`](docs/sdd/03-component-spec.md). Summary:

**Props:** `src`, `playing`, `loop`, `controls`, `light`, `volume`, `muted`,
`playback_rate`, `pip`, `plays_inline`, `width`, `height`, `style`, `auto_play`,
`preload`, `cross_origin`, `poster`, `disable_remote_playback`,
`disable_picture_in_picture`, `preview_tab_index`, `preview_aria_label`,
`o_embed_url`, `config`.

**Events:** `on_ready`, `on_start`, `on_play`, `on_pause`, `on_ended`,
`on_error`, `on_duration_change`, `on_progress`, `on_time_update`, `on_seeking`,
`on_seeked`, `on_waiting`, `on_playing`, `on_rate_change`, `on_volume_change`,
`on_enter_picture_in_picture`, `on_leave_picture_in_picture`, `on_click_preview`.

**Control helpers:** `controls.play/pause/seek_to/seek_relative/seek_fraction/
set_volume/set_playback_rate/request_fullscreen/get_current_time/get_duration`.

## Per-player config

```python
react_player(
    src="https://www.youtube.com/watch?v=oUFJJNQGwhk",
    config={"youtube": {"color": "white"}, "vimeo": {"color": "ffffff"}},
)
```

Keys: `html`, `hls`, `dash`, `mux`, `youtube`, `vimeo`, `wistia`, `spotify`,
`twitch`, `tiktok`.

## Run the demo

```bash
cd reflex_react_player_demo
pip install -e ..          # install the component
pip install -r requirements.txt
reflex init                # first time only (creates .web)
reflex run
```

Open http://localhost:3000 — the demo includes a provider switcher, transport
controls, speed buttons, a seek slider, a volume slider, controls/muted/loop/
light toggles, the Played + Loaded progress bars, and a live time readout.

## How it works

- **Client-only:** react-player touches `window`, so the component subclasses
  `NoSSRComponent` (rendered via `dynamic(import(...), {ssr:false})`).
- **Default export:** `is_default = True` (omitting it is the classic
  "Invalid Element Type" failure).
- **Events:** native `SyntheticEvent`s are reduced, on the client, to a small
  serializable dict read from the underlying `HTMLMediaElement`.
- **Imperative API:** react-player v3 exposes its instance API through the
  forwarded ref (`ref.currentTime`, `ref.play()` ...); helpers drive it via
  `rx.call_script` against `refs['ref_<id>'].current`.

Details and decisions: [`docs/sdd/02-architecture.md`](docs/sdd/02-architecture.md).

## Limitations

react-player **v3** has not yet ported every v2 provider. **DailyMotion,
SoundCloud, Streamable, Facebook, Mixcloud and Kaltura are not supported** here;
stay on react-player v2 if you need them.

## Development

```bash
pip install -e ".[dev]"
pytest -q
python -m build          # build sdist + wheel
```

## License

[Apache-2.0](LICENSE) © 2026 Ernesto Crespo.

`react-player` is a separate project by Pete Cook / Mux, under its own license.
