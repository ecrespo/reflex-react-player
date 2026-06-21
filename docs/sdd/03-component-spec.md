# Component Specification (API Contract) — reflex-react-player

**Status:** Approved · **Owner:** Ernesto Crespo · **Last updated:** 2026-06-21
**Audience:** Developers using the component; the contract tests verify against this.

This is the public contract: every prop, event, and control helper. A developer
should be able to build an integration from this document alone.

## 1. Import

```python
from reflex_react_player import react_player, ReactPlayer, controls
```

- `react_player` — factory (`ReactPlayer.create`), the normal entry point.
- `ReactPlayer` — the component class (for subclassing / introspection).
- `controls` — imperative, ref-based helpers.

## 2. Props

All props are optional. Python `snake_case` maps to react-player `camelCase`.

| Python prop | JS prop | Type | Default | Description |
|-------------|---------|------|---------|-------------|
| `src` | `src` | `str` | — | Media URL. Inspected to pick the provider. |
| `playing` | `playing` | `bool` | unset | Play (`True`) / pause (`False`). Leave unset to let the element self-manage. |
| `loop` | `loop` | `bool` | `False` | Loop playback. |
| `controls` | `controls` | `bool` | `False` | Show native controls. |
| `light` | `light` | `bool \| str` | `False` | Thumbnail-first mode; `str` = custom image URL. |
| `volume` | `volume` | `float` | `1.0` | 0..1. |
| `muted` | `muted` | `bool` | `False` | Mute (needed for autoplay). |
| `playback_rate` | `playbackRate` | `float` | `1.0` | Speed multiplier. |
| `pip` | `pip` | `bool` | `False` | Picture-in-picture (supported players only). |
| `plays_inline` | `playsInline` | `bool` | `False` | iOS inline playback. |
| `width` | `width` | `str \| int` | `"320px"` | Player width. |
| `height` | `height` | `str \| int` | `"180px"` | Player height. |
| `style` | `style` | `dict` | `{}` | Inline styles (e.g. `aspectRatio`). |
| `auto_play` | `autoPlay` | `bool` | `False` | Native autoplay. |
| `preload` | `preload` | `str` | — | Native preload hint. |
| `cross_origin` | `crossOrigin` | `str` | — | Native crossOrigin. |
| `poster` | `poster` | `str` | — | Poster image (video). |
| `disable_remote_playback` | `disableRemotePlayback` | `bool` | `False` | Native attr. |
| `disable_picture_in_picture` | `disablePictureInPicture` | `bool` | `False` | Native attr. |
| `preview_tab_index` | `previewTabIndex` | `int` | `0` | Light-mode preview tabIndex. |
| `preview_aria_label` | `previewAriaLabel` | `str` | `""` | Light-mode preview aria-label. |
| `o_embed_url` | `oEmbedUrl` | `str` | react-player default | oEmbed endpoint for thumbnails. |
| `config` | `config` | `dict` | — | Per-player options (see §5). |

Standard Reflex props (`id`, `class_name`, `style`, ...) also apply. **Set `id`**
if you want to use the imperative helpers in §4.

## 3. Events

Most events deliver a **media-state dict** (see shape below). Exceptions noted.

| Python handler | JS callback | Payload | When |
|----------------|-------------|---------|------|
| `on_ready` | `onReady` | — (no args) | Media loaded & ready. |
| `on_start` | `onStart` | — (no args) | First play only. |
| `on_play` | `onPlay` | media-state dict | Playback started/resumed. |
| `on_pause` | `onPause` | media-state dict | Paused. |
| `on_ended` | `onEnded` | media-state dict | Finished (not when looping). |
| `on_error` | `onError` | `message: str` | Playback error. |
| `on_duration_change` | `onDurationChange` | `seconds: float` | Duration known/changed. |
| `on_progress` | `onProgress` | media-state dict | Buffered/loaded changed. |
| `on_time_update` | `onTimeUpdate` | media-state dict | Current time changed (frequent). |
| `on_seeking` | `onSeeking` | media-state dict | Seek started. |
| `on_seeked` | `onSeeked` | media-state dict | Seek finished. |
| `on_waiting` | `onWaiting` | media-state dict | Buffering started. |
| `on_playing` | `onPlaying` | media-state dict | Resumed after buffering. |
| `on_rate_change` | `onRateChange` | media-state dict | Playback rate changed. |
| `on_volume_change` | `onVolumeChange` | media-state dict | Volume/mute changed. |
| `on_enter_picture_in_picture` | `onEnterPictureInPicture` | — | Entered PiP. |
| `on_leave_picture_in_picture` | `onLeavePictureInPicture` | — | Left PiP. |
| `on_click_preview` | `onClickPreview` | — | Light-mode preview clicked. |

### Media-state dict

```python
{
  "current_time": float, "duration": float,
  "played": float, "played_seconds": float,      # played: 0..1 fraction
  "loaded": float, "loaded_seconds": float,        # loaded: 0..1 fraction
  "playback_rate": float, "volume": float,
  "muted": bool, "paused": bool,
}
```

Handler signatures:

```python
@rx.event
def handle_time_update(self, state: dict):
    self.played = state["played"]

@rx.event
def handle_duration(self, seconds: float):
    self.duration = seconds

@rx.event
def handle_error(self, message: str):
    self.error = message
```

## 4. Imperative control helpers (`controls`)

Require the player to have an `id`. Each returns a Reflex event (usable in
`on_click=...` or returned from a handler).

| Helper | Effect |
|--------|--------|
| `controls.play(id)` | `element.play()` |
| `controls.pause(id)` | `element.pause()` |
| `controls.seek_to(id, seconds)` | `currentTime = seconds` |
| `controls.seek_relative(id, delta)` | `currentTime += delta` |
| `controls.seek_fraction(id, frac)` | `currentTime = frac * duration` |
| `controls.set_volume(id, v)` | `volume = v` (0..1) |
| `controls.set_playback_rate(id, r)` | `playbackRate = r` |
| `controls.request_fullscreen(id)` | `requestFullscreen()` |
| `controls.get_current_time(id, cb)` | reads `currentTime` → `cb(float)` |
| `controls.get_duration(id, cb)` | reads `duration` → `cb(float)` |

```python
rx.button("Skip +10s", on_click=controls.seek_relative("demo_player", 10))
```

## 5. `config` (per-player options)

`config` is keyed by player; only the active player's sub-object is forwarded.

```python
react_player(
    src="https://www.youtube.com/watch?v=oUFJJNQGwhk",
    config={
        "youtube": {"color": "white"},   # YouTube player vars
        "vimeo": {"color": "ffffff"},     # Vimeo embed params
        "hls": {...},                      # hls.js config
        "spotify": {"preferVideo": True},
    },
)
```

Keys: `html`, `hls`, `dash`, `mux`, `youtube`, `vimeo`, `wistia`, `spotify`,
`twitch`, `tiktok`.

## 6. Supported sources

File/audio (mp4, webm, ogg/ogv, mov, m4v, mp3, wav, aac, m4a, oga), HLS
(`.m3u8`), DASH (`.mpd`), Mux, YouTube (videos/shorts/live/playlists), Vimeo,
Wistia, Spotify, Twitch, TikTok. Cloudflare Stream is available at the element
layer.

**Not supported in v3 (limitation):** DailyMotion, SoundCloud, Streamable,
Facebook, Mixcloud, Kaltura. Stay on react-player v2 if you need these.

## 7. Contract tests

`tests/test_component.py` asserts: library/tag/default wiring; that
`playback_rate`/`plays_inline` render as camelCase; that the documented event
triggers exist; that control helpers construct. Any contract change updates this
file and the tests together.
