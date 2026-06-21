"""A Reflex wrapper around react-player v3 (https://github.com/cookpete/react-player).

react-player v3 is a ground-up rewrite that aligns its public surface with the
native ``HTMLMediaElement`` interface:

* The media URL prop was renamed ``url`` -> ``src``.
* Callbacks use native media-event names (``onTimeUpdate``, ``onProgress``,
  ``onDurationChange``, ``onWaiting``, ``onPlaying`` ...).
* Instance methods are read/written directly on the forwarded ref
  (``ref.currentTime``, ``ref.duration``, ``ref.play()`` ...).

Because react-player instantiates browser-only SDKs (it touches ``window``), the
component MUST render on the client only. We therefore subclass
``NoSSRComponent`` so Reflex emits a Next.js ``dynamic(import(...), {ssr: false})``.

react-player is a *default* export, so ``is_default = True`` is mandatory.
"""

from __future__ import annotations

from typing import Any, Union

import reflex as rx
from reflex.components.component import NoSSRComponent
from reflex.vars import Var

# Pinned npm version for reproducible builds. Bump deliberately.
REACT_PLAYER_VERSION = "react-player@3.4.0"


# ---------------------------------------------------------------------------
# Event argument specs
#
# react-player v3 forwards native React ``SyntheticEvent`` objects to most of
# its callbacks. A raw SyntheticEvent is not JSON serializable, so instead of
# shipping it to the backend untouched we extract the useful media state from
# ``event.target`` (the underlying HTMLMediaElement) on the client and send a
# small, plain dict to the Python event handler.
# ---------------------------------------------------------------------------


def _media_state_spec(e: Var) -> list[Var]:
    """Extract a serializable snapshot of media state from a media event.

    Returns a single dict argument with the most useful fields. ``played`` and
    ``loaded`` are normalized 0..1 fractions (handy for progress bars / sliders).
    """
    expr = (
        "(() => {"
        f" const t = {e!s}?.target;"
        " if (!t) return {current_time: 0, duration: 0, played: 0,"
        " played_seconds: 0, loaded: 0, loaded_seconds: 0,"
        " playback_rate: 1, volume: 1, muted: false, paused: true};"
        " const d = t.duration || 0;"
        " let le = 0;"
        " try { le = (t.buffered && t.buffered.length)"
        " ? t.buffered.end(t.buffered.length - 1) : 0; } catch (_) { le = 0; }"
        " return {"
        " current_time: t.currentTime || 0,"
        " duration: d,"
        " played: d ? (t.currentTime || 0) / d : 0,"
        " played_seconds: t.currentTime || 0,"
        " loaded: d ? le / d : 0,"
        " loaded_seconds: le,"
        " playback_rate: t.playbackRate || 1,"
        " volume: (t.volume === undefined ? 1 : t.volume),"
        " muted: !!t.muted,"
        " paused: !!t.paused"
        " };"
        "})()"
    )
    return [Var(_js_expr=expr, _var_type=dict)]


def _duration_spec(e: Var) -> list[Var]:
    """``onDurationChange`` -> send the duration in seconds (float)."""
    return [Var(_js_expr=f"({e!s}?.target?.duration || 0)", _var_type=float)]


def _empty_spec() -> list[Var]:
    """Callbacks where no useful argument is forwarded (e.g. ``onReady``)."""
    return []


def _error_spec(e: Var) -> list[Var]:
    """``onError`` -> best-effort stringified error message."""
    return [
        Var(
            _js_expr=(
                f"(({e!s} && ({e!s}.message || ({e!s}.target && {e!s}.target.error"
                f" && {e!s}.target.error.message))) || 'media error')"
            ),
            _var_type=str,
        )
    ]


class ReactPlayer(NoSSRComponent):
    """A versatile media player wrapping react-player v3.

    Plays files (mp4/webm/ogg/mp3/...), HLS (.m3u8), DASH (.mpd), YouTube,
    Vimeo, Wistia, Mux, Spotify, Twitch and TikTok by inspecting ``src``.
    """

    # --- library / export wiring ------------------------------------------
    library = REACT_PLAYER_VERSION
    tag = "ReactPlayer"
    alias = "ReactPlayer"
    is_default = True  # react-player is the package's default export.

    # --- core playback props (snake_case -> camelCase automatically) ------
    # Media source URL. Renamed from v2's ``url``.
    src: rx.Var[str]
    # Play/pause. Leave unset to let the element manage itself.
    playing: rx.Var[bool]
    # Loop playback.
    loop: rx.Var[bool]
    # Show the player's native controls.
    controls: rx.Var[bool]
    # Thumbnail-first ("light") mode. True fetches a thumbnail via oEmbed; a
    # string uses that image URL as the preview.
    light: rx.Var[Union[bool, str]]
    # Volume, 0..1.
    volume: rx.Var[float]
    # Mute audio (required for autoplay in most browsers).
    muted: rx.Var[bool]
    # Playback speed multiplier (e.g. 1.5). -> playbackRate
    playback_rate: rx.Var[float]
    # Picture-in-picture toggle (supported players only).
    pip: rx.Var[bool]
    # iOS inline playback. -> playsInline
    plays_inline: rx.Var[bool]

    # --- layout -----------------------------------------------------------
    width: rx.Var[Union[str, int]]
    height: rx.Var[Union[str, int]]
    style: rx.Var[dict[str, Any]]

    # --- native passthrough attributes ------------------------------------
    auto_play: rx.Var[bool]  # -> autoPlay
    preload: rx.Var[str]
    cross_origin: rx.Var[str]  # -> crossOrigin
    poster: rx.Var[str]
    disable_remote_playback: rx.Var[bool]  # -> disableRemotePlayback
    disable_picture_in_picture: rx.Var[bool]  # -> disablePictureInPicture

    # --- light / preview-mode props ---------------------------------------
    preview_tab_index: rx.Var[int]  # -> previewTabIndex
    preview_aria_label: rx.Var[str]  # -> previewAriaLabel
    o_embed_url: rx.Var[str]  # -> oEmbedUrl

    # --- per-player configuration -----------------------------------------
    # Keyed by player ("youtube", "vimeo", "hls", "spotify", "tiktok", ...).
    config: rx.Var[dict[str, Any]]

    # --- event triggers ---------------------------------------------------
    # react-player specific synthetic callbacks.
    on_ready: rx.EventHandler[_empty_spec]
    on_start: rx.EventHandler[_empty_spec]
    # Native media events (forwarded by react-player v3).
    on_play: rx.EventHandler[_media_state_spec]
    on_pause: rx.EventHandler[_media_state_spec]
    on_ended: rx.EventHandler[_media_state_spec]
    on_error: rx.EventHandler[_error_spec]
    on_duration_change: rx.EventHandler[_duration_spec]  # -> onDurationChange
    on_progress: rx.EventHandler[_media_state_spec]  # buffered/loaded changed
    on_time_update: rx.EventHandler[_media_state_spec]  # currentTime changed
    on_seeking: rx.EventHandler[_media_state_spec]
    on_seeked: rx.EventHandler[_media_state_spec]
    on_waiting: rx.EventHandler[_media_state_spec]  # buffering started
    on_playing: rx.EventHandler[_media_state_spec]  # buffering ended / resumed
    on_rate_change: rx.EventHandler[_media_state_spec]  # -> onRateChange
    on_volume_change: rx.EventHandler[_media_state_spec]  # -> onVolumeChange
    on_enter_picture_in_picture: rx.EventHandler[_empty_spec]
    on_leave_picture_in_picture: rx.EventHandler[_empty_spec]
    on_click_preview: rx.EventHandler[_empty_spec]  # light-mode preview clicked

    # snake_case -> camelCase covers almost everything. Map only the names that
    # do not camelCase cleanly to their exact react-player prop names.
    _rename_props: dict[str, str] = {
        "o_embed_url": "oEmbedUrl",
    }


react_player = ReactPlayer.create
