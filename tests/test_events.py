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
    triggers = react_player().get_event_triggers()
    custom = {k for k in triggers if k.startswith("on_")} - set(ALL_EVENTS)
    # Reflex injects base handlers (e.g. on_mount/on_unmount, mouse/UI events); allow those.
    base = {
        "on_mount", "on_unmount",
        # Mouse/UI event handlers injected by Reflex base class
        "on_click", "on_double_click", "on_context_menu",
        "on_mouse_enter", "on_mouse_leave", "on_mouse_over", "on_mouse_out",
        "on_mouse_down", "on_mouse_up", "on_mouse_move",
        "on_focus", "on_blur",
        "on_scroll", "on_scroll_end",
    }
    assert custom <= base, f"unexpected triggers: {custom - base}"
