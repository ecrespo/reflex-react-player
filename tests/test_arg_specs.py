from reflex.vars import Var

from reflex_react_player.react_player import (
    _duration_spec,
    _empty_spec,
    _error_spec,
    _media_state_spec,
)

E = Var(_js_expr="_ev")

MEDIA_KEYS = [
    "current_time", "duration", "played", "played_seconds",
    "loaded", "loaded_seconds", "playback_rate", "volume", "muted", "paused",
]


def test_media_spec_returns_single_dict_var():
    spec = _media_state_spec(E)
    assert len(spec) == 1
    assert spec[0]._var_type is dict


def test_media_spec_contains_all_contract_keys():
    js = str(_media_state_spec(E)[0]._js_expr)
    for key in MEDIA_KEYS:
        assert key in js, f"media-state spec missing key: {key}"


def test_media_spec_uses_optional_chaining():
    js = str(_media_state_spec(E)[0]._js_expr)
    assert "?.target" in js  # null-safe before mount (ADR-1/ADR-4)


def test_duration_spec_reads_target_duration_as_float():
    spec = _duration_spec(E)
    assert len(spec) == 1
    assert spec[0]._var_type is float
    js = str(spec[0]._js_expr)
    assert "?.target?.duration" in js


def test_error_spec_is_string_with_fallback():
    spec = _error_spec(E)
    assert spec[0]._var_type is str
    assert "media error" in str(spec[0]._js_expr)


def test_empty_spec_is_empty_list():
    assert _empty_spec() == []
