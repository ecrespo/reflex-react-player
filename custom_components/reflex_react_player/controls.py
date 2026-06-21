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
