"""Demo Reflex app for reflex-react-player.

Reproduces the official react-player demo (cookpete.github.io/react-player):
a provider source-switcher, transport controls (play/pause/stop/fullscreen/PiP),
playback-speed buttons, a seek slider, a volume slider, controls/muted/loop/
light toggles, the Played and Loaded progress bars (the "graphs"), a live time
readout, and a custom-URL loader.
"""

from __future__ import annotations

import reflex as rx

from reflex_react_player import controls, react_player

PLAYER_ID = "demo_player"

# Sample sources grouped by provider, mirroring the upstream demo.
SOURCES: dict[str, list[tuple[str, str]]] = {
    "File (HTML)": [
        ("MP4", "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4"),
        ("WebM", "https://test-videos.co.uk/vids/bigbuckbunny/webm/vp9/720/Big_Buck_Bunny_720_10s_1MB.webm"),
        ("MP3 (audio)", "https://storage.googleapis.com/media-session/elephants-dream/the-wires.mp3"),
    ],
    "HLS / DASH": [
        ("HLS .m3u8", "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"),
        ("DASH .mpd", "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd"),
    ],
    "YouTube": [
        ("Video A", "https://www.youtube.com/watch?v=oUFJJNQGwhk"),
        ("Video B", "https://www.youtube.com/watch?v=jNgP6d9HraI"),
        ("Playlist", "https://www.youtube.com/playlist?list=PLogRWNZ498ETeQNYrOlqikEML3bKJcdcx"),
    ],
    "Vimeo / Wistia": [
        ("Vimeo", "https://vimeo.com/90509568"),
        ("Wistia", "https://home.wistia.com/medias/e4a27b971d"),
    ],
}

DEFAULT_SRC = SOURCES["YouTube"][0][1]


class PlayerState(rx.State):
    """All controlled state for the player, mirroring the upstream demo."""

    src: str = DEFAULT_SRC
    playing: bool = False
    controls: bool = True
    light: bool = False
    loop: bool = False
    muted: bool = False
    volume: float = 0.8
    playback_rate: float = 1.0
    pip: bool = False

    # Progress / timing (the "graphs").
    played: float = 0.0  # 0..1
    loaded: float = 0.0  # 0..1
    duration: float = 0.0  # seconds
    played_seconds: float = 0.0

    seeking: bool = False
    last_event: str = "—"

    # --- source switching ---
    @rx.event
    def load(self, src: str):
        self.src = src
        self.played = 0.0
        self.loaded = 0.0
        self.played_seconds = 0.0
        self.duration = 0.0
        self.playing = True
        self.last_event = f"load({src[:48]}...)"

    @rx.event
    def stop(self):
        self.src = ""
        self.playing = False
        self.last_event = "stop"

    @rx.event
    def toggle_play(self):
        self.playing = not self.playing

    # --- toggles ---
    @rx.event
    def set_controls(self, v: bool):
        self.controls = v

    @rx.event
    def set_light(self, v: bool):
        self.light = v

    @rx.event
    def set_loop(self, v: bool):
        self.loop = v

    @rx.event
    def set_muted(self, v: bool):
        self.muted = v

    # --- sliders ---
    @rx.event
    def set_volume(self, value: list[int | float]):
        self.volume = float(value[0]) / 100.0

    @rx.event
    def set_rate(self, rate: float):
        self.playback_rate = rate

    @rx.event
    def on_seek_change(self, value: list[int | float]):
        # While dragging, update the displayed position and seek the player.
        self.seeking = True
        self.played = float(value[0]) / 100.0
        return controls.seek_fraction(PLAYER_ID, self.played)

    @rx.event
    def on_seek_commit(self, value: list[int | float]):
        self.seeking = False
        self.played = float(value[0]) / 100.0
        return controls.seek_fraction(PLAYER_ID, self.played)

    # --- player events ---
    @rx.event
    def handle_ready(self):
        self.last_event = "ready"

    @rx.event
    def handle_play(self, state: dict):
        self.playing = True
        self.last_event = "play"

    @rx.event
    def handle_pause(self, state: dict):
        self.playing = False
        self.last_event = "pause"

    @rx.event
    def handle_ended(self, state: dict):
        self.playing = self.loop
        self.last_event = "ended"

    @rx.event
    def handle_duration(self, seconds: float):
        self.duration = seconds

    @rx.event
    def handle_progress(self, state: dict):
        # Buffered/loaded changed -> update the Loaded bar.
        self.loaded = state.get("loaded", 0.0)

    @rx.event
    def handle_time_update(self, state: dict):
        # currentTime changed -> update the Played bar (unless mid-scrub).
        if not self.seeking:
            self.played = state.get("played", 0.0)
            self.played_seconds = state.get("played_seconds", 0.0)
        if state.get("duration"):
            self.duration = state.get("duration", self.duration)

    @rx.event
    def handle_error(self, message: str):
        self.last_event = f"error: {message}"

    # --- derived display values ---
    @rx.var
    def played_pct(self) -> float:
        return round(self.played * 100, 3)

    @rx.var
    def loaded_pct(self) -> float:
        return round(self.loaded * 100, 3)

    @rx.var
    def elapsed_label(self) -> str:
        return _fmt(self.played_seconds)

    @rx.var
    def remaining_label(self) -> str:
        return "-" + _fmt(max(self.duration - self.played_seconds, 0))

    @rx.var
    def duration_label(self) -> str:
        return _fmt(self.duration)


def _fmt(seconds: float) -> str:
    """Format seconds as m:ss or h:mm:ss (mirrors the upstream Duration cmp)."""
    seconds = int(seconds or 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


def source_buttons() -> rx.Component:
    groups = []
    for group, items in SOURCES.items():
        groups.append(
            rx.vstack(
                rx.text(group, size="1", weight="bold", color_scheme="gray"),
                rx.hstack(
                    *[
                        rx.button(
                            label,
                            on_click=PlayerState.load(url),
                            size="1",
                            variant="soft",
                        )
                        for label, url in items
                    ],
                    wrap="wrap",
                    spacing="2",
                ),
                align="start",
                spacing="1",
            )
        )
    return rx.vstack(*groups, spacing="3", align="start", width="100%")


def transport_controls() -> rx.Component:
    return rx.hstack(
        rx.button("Stop", on_click=PlayerState.stop, size="2", variant="outline"),
        rx.button(
            rx.cond(PlayerState.playing, "Pause", "Play"),
            on_click=PlayerState.toggle_play,
            size="2",
        ),
        rx.button("⏪ -10s", on_click=controls.seek_relative(PLAYER_ID, -10), size="2", variant="soft"),
        rx.button("+10s ⏩", on_click=controls.seek_relative(PLAYER_ID, 10), size="2", variant="soft"),
        rx.button("Fullscreen", on_click=controls.request_fullscreen(PLAYER_ID), size="2", variant="soft"),
        wrap="wrap",
        spacing="2",
    )


def speed_buttons() -> rx.Component:
    return rx.hstack(
        rx.text("Speed:", size="2"),
        *[
            rx.button(
                f"{rate}x",
                on_click=[PlayerState.set_rate(rate), controls.set_playback_rate(PLAYER_ID, rate)],
                size="1",
                variant=rx.cond(PlayerState.playback_rate == rate, "solid", "soft"),
            )
            for rate in (0.5, 1.0, 1.5, 2.0)
        ],
        spacing="2",
        align="center",
    )


def toggles() -> rx.Component:
    return rx.hstack(
        rx.checkbox("Controls", checked=PlayerState.controls, on_change=PlayerState.set_controls),
        rx.checkbox("Muted", checked=PlayerState.muted, on_change=PlayerState.set_muted),
        rx.checkbox("Loop", checked=PlayerState.loop, on_change=PlayerState.set_loop),
        rx.checkbox("Light", checked=PlayerState.light, on_change=PlayerState.set_light),
        spacing="4",
        wrap="wrap",
    )


def progress_bars() -> rx.Component:
    return rx.vstack(
        rx.text("Seek", size="1", weight="bold"),
        rx.slider(
            min=0,
            max=100,
            step=0.1,
            value=[PlayerState.played_pct],
            on_change=PlayerState.on_seek_change,
            on_value_commit=PlayerState.on_seek_commit,
            width="100%",
        ),
        rx.hstack(
            rx.text("Played", size="1", width="60px"),
            rx.progress(value=PlayerState.played_pct, max=100, width="100%", color_scheme="grass"),
            width="100%",
            align="center",
        ),
        rx.hstack(
            rx.text("Loaded", size="1", width="60px"),
            rx.progress(value=PlayerState.loaded_pct, max=100, width="100%", color_scheme="gray"),
            width="100%",
            align="center",
        ),
        rx.hstack(
            rx.text("Volume", size="1", width="60px"),
            rx.slider(
                min=0, max=100, step=1,
                value=[PlayerState.volume * 100],
                on_change=PlayerState.set_volume,
                width="100%",
            ),
            width="100%",
            align="center",
        ),
        spacing="3",
        width="100%",
    )


def state_readout() -> rx.Component:
    def row(label: str, value) -> rx.Component:
        return rx.hstack(
            rx.text(label, size="1", color_scheme="gray", width="90px"),
            rx.text(value, size="1", weight="medium"),
            width="100%",
        )

    return rx.vstack(
        row("elapsed", PlayerState.elapsed_label),
        row("duration", PlayerState.duration_label),
        row("remaining", PlayerState.remaining_label),
        row("played", PlayerState.played_pct.to_string()),
        row("loaded", PlayerState.loaded_pct.to_string()),
        row("playing", PlayerState.playing.to_string()),
        row("rate", PlayerState.playback_rate.to_string()),
        row("last event", PlayerState.last_event),
        spacing="1",
        width="100%",
    )


def player() -> rx.Component:
    return react_player(
        id=PLAYER_ID,
        src=PlayerState.src,
        playing=PlayerState.playing,
        controls=PlayerState.controls,
        light=PlayerState.light,
        loop=PlayerState.loop,
        muted=PlayerState.muted,
        volume=PlayerState.volume,
        playback_rate=PlayerState.playback_rate,
        width="100%",
        height="100%",
        style={"width": "100%", "height": "100%", "aspectRatio": "16 / 9"},
        config={
            "youtube": {"color": "white"},
            "vimeo": {"color": "ffffff"},
        },
        on_ready=PlayerState.handle_ready,
        on_play=PlayerState.handle_play,
        on_pause=PlayerState.handle_pause,
        on_ended=PlayerState.handle_ended,
        on_duration_change=PlayerState.handle_duration,
        on_progress=PlayerState.handle_progress,
        on_time_update=PlayerState.handle_time_update,
        on_error=PlayerState.handle_error,
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("reflex-react-player", size="7"),
            rx.text("A Reflex wrapper for react-player v3 — full demo.", color_scheme="gray"),
            rx.box(
                player(),
                width="100%",
                max_width="900px",
                border_radius="12px",
                overflow="hidden",
                box_shadow="0 8px 30px rgba(0,0,0,0.12)",
            ),
            transport_controls(),
            speed_buttons(),
            progress_bars(),
            toggles(),
            rx.divider(),
            rx.heading("Sources", size="4"),
            source_buttons(),
            rx.divider(),
            rx.heading("State", size="4"),
            state_readout(),
            spacing="4",
            align="start",
            width="100%",
            padding_y="2rem",
        ),
        size="3",
    )


app = rx.App(theme=rx.theme(appearance="light", accent_color="violet"))
app.add_page(index, title="reflex-react-player demo")
