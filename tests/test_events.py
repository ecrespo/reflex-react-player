import reflex as rx
from reflex_react_player.react_player import react_player

ALL_EVENTS = [
    "on_ready", "on_start", "on_play", "on_pause", "on_ended", "on_error",
    "on_duration_change", "on_progress", "on_time_update",
    "on_seeking", "on_seeked", "on_waiting", "on_playing",
    "on_rate_change", "on_volume_change",
    "on_enter_picture_in_picture", "on_leave_picture_in_picture",
    "on_click_preview",
]


def test_all_documented_triggers_exist():
    triggers = react_player().get_event_triggers()
    for name in ALL_EVENTS:
        assert name in triggers, f"missing event trigger: {name}"


def test_no_extra_undocumented_on_handlers():
    # Subtract Reflex's base triggers dynamically (mount/unmount, mouse, focus,
    # scroll, ...) so this stays correct across Reflex versions.
    base = set(rx.box().get_event_triggers())
    custom = set(react_player().get_event_triggers()) - base
    assert custom == set(ALL_EVENTS), f"trigger drift vs documented: {custom ^ set(ALL_EVENTS)}"
