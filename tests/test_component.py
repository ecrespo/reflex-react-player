"""Smoke tests for the reflex-react-player component.

Run with: pytest -q  (requires `reflex` and `reflex-react-player` installed).
"""

import reflex as rx

from reflex_react_player import ReactPlayer, controls, react_player


def test_library_wiring():
    assert ReactPlayer.library.startswith("react-player@")
    assert ReactPlayer.tag == "ReactPlayer"
    assert ReactPlayer.is_default is True


def test_create_renders_props():
    comp = react_player(
        src="https://www.youtube.com/watch?v=oUFJJNQGwhk",
        playing=True,
        controls=True,
        volume=0.5,
        playback_rate=1.5,
        plays_inline=True,
    )
    assert isinstance(comp, ReactPlayer)
    code = comp.render()
    rendered = str(code)
    # snake_case props must be camelCased in the rendered output.
    assert "playbackRate" in rendered
    assert "playsInline" in rendered


def test_event_triggers_exist():
    triggers = react_player().get_event_triggers()
    for name in [
        "on_ready",
        "on_play",
        "on_progress",
        "on_time_update",
        "on_duration_change",
        "on_error",
    ]:
        assert name in triggers, f"missing event trigger: {name}"


def test_controls_helpers_return_event_specs():
    # These build client-side rx.call_script events; just ensure they construct.
    assert controls.play("p") is not None
    assert controls.seek_relative("p", 10) is not None
    assert controls.seek_fraction("p", 0.5) is not None
