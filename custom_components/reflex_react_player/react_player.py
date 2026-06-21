"""A Reflex wrapper around react-player v3 (https://github.com/cookpete/react-player)."""

from __future__ import annotations

from typing import Any, Union

import reflex as rx
from reflex.components.component import NoSSRComponent
from reflex.vars import Var

# Pinned npm version for reproducible builds (ADR-6). Bump deliberately.
REACT_PLAYER_VERSION = "react-player@3.4.0"


def _media_state_spec(e: Var) -> list[Var]:
    """Extract a serializable media-state snapshot from a native media event.

    `played`/`loaded` are normalized 0..1 fractions (handy for progress bars).
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
    """`onDurationChange` -> duration in seconds (float)."""
    return [Var(_js_expr=f"({e!s}?.target?.duration || 0)", _var_type=float)]


def _empty_spec() -> list[Var]:
    """Callbacks with no useful forwarded argument (e.g. `onReady`)."""
    return []


def _error_spec(e: Var) -> list[Var]:
    """`onError` -> best-effort stringified error message."""
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
    """A versatile media player wrapping react-player v3."""

    library = REACT_PLAYER_VERSION
    tag = "ReactPlayer"
    alias = "ReactPlayer"
    is_default = True  # react-player is the package's default export.

    # --- core playback props (snake_case -> camelCase automatically) ------
    src: rx.Var[str]
    playing: rx.Var[bool]
    loop: rx.Var[bool]
    controls: rx.Var[bool]
    light: rx.Var[Union[bool, str]]
    volume: rx.Var[float]
    muted: rx.Var[bool]
    playback_rate: rx.Var[float]          # -> playbackRate
    pip: rx.Var[bool]
    plays_inline: rx.Var[bool]            # -> playsInline

    # --- layout (NOTE: no `style` prop — it is built in) ------------------
    width: rx.Var[Union[str, int]]
    height: rx.Var[Union[str, int]]

    # --- native passthrough attributes ------------------------------------
    auto_play: rx.Var[bool]               # -> autoPlay
    preload: rx.Var[str]
    cross_origin: rx.Var[str]             # -> crossOrigin
    poster: rx.Var[str]
    disable_remote_playback: rx.Var[bool]        # -> disableRemotePlayback
    disable_picture_in_picture: rx.Var[bool]     # -> disablePictureInPicture

    # --- light / preview-mode props ---------------------------------------
    preview_tab_index: rx.Var[int]        # -> previewTabIndex
    preview_aria_label: rx.Var[str]       # -> previewAriaLabel
    o_embed_url: rx.Var[str]              # -> oEmbedUrl (see _rename_props)

    # --- per-player configuration -----------------------------------------
    config: rx.Var[dict[str, Any]]

    # snake_case -> camelCase covers everything except names that need a hint.
    _rename_props: dict[str, str] = {
        "o_embed_url": "oEmbedUrl",
    }


react_player = ReactPlayer.create
