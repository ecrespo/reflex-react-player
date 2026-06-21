"""Imperative client-side control helpers for :class:`ReactPlayer`.

react-player v3 exposes its instance API through the forwarded ref, which points
at the underlying ``HTMLMediaElement``. Reflex stores a component's ref (when it
has an ``id``) in the global ``refs`` object as ``refs['ref_<id>']``. These
helpers return ``rx.call_script(...)`` events so the player can be driven from any
Python event handler. All JS uses optional chaining because the ref is null
before the client mounts (ADR-4).
"""

from __future__ import annotations

import reflex as rx
from reflex.event import EventSpec


def _ref(player_id: str) -> str:
    """JS expression resolving to the player's HTMLMediaElement (or undefined)."""
    return f"refs['ref_{player_id}']?.current"


def play(player_id: str) -> EventSpec:
    """Start playback."""
    return rx.call_script(f"{_ref(player_id)}?.play?.()")


def pause(player_id: str) -> EventSpec:
    """Pause playback."""
    return rx.call_script(f"{_ref(player_id)}?.pause?.()")


def request_fullscreen(player_id: str) -> EventSpec:
    """Request native fullscreen for the player element."""
    return rx.call_script(f"{_ref(player_id)}?.requestFullscreen?.()")


def seek_to(player_id: str, seconds: float) -> EventSpec:
    """Seek to an absolute time in seconds."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.currentTime = {seconds}; }}"
    )


def seek_relative(player_id: str, delta_seconds: float) -> EventSpec:
    """Seek forward (positive) or backward (negative) by ``delta_seconds``."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.currentTime = "
        f"(p.currentTime || 0) + ({delta_seconds}); }}"
    )


def seek_fraction(player_id: str, fraction: float) -> EventSpec:
    """Seek to a 0..1 fraction of the total duration (slider scrubbing)."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p && p.duration) "
        f"p.currentTime = ({fraction}) * p.duration; }}"
    )


def set_volume(player_id: str, volume: float) -> EventSpec:
    """Set volume (0..1) directly on the element."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.volume = {volume}; }}"
    )


def set_playback_rate(player_id: str, rate: float) -> EventSpec:
    """Set the playback rate directly on the element."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.playbackRate = {rate}; }}"
    )


def get_current_time(player_id: str, callback) -> EventSpec:
    """Read ``currentTime`` and pass it to a backend event handler.

    ``callback`` is a state setter / event handler accepting a float.
    """
    return rx.call_script(
        f"({_ref(player_id)}?.currentTime || 0)", callback=callback
    )


def get_duration(player_id: str, callback) -> EventSpec:
    """Read ``duration`` and pass it to a backend event handler."""
    return rx.call_script(
        f"({_ref(player_id)}?.duration || 0)", callback=callback
    )
