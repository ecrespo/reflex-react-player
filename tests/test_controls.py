from reflex.event import EventSpec

from reflex_react_player import controls


def js_of(spec) -> str:
    # rx.call_script puts the JS string literal at args[0][1].
    return str(spec.args[0][1]._var_value)


def test_play_calls_element_play():
    spec = controls.play("p")
    assert isinstance(spec, EventSpec)
    js = js_of(spec)
    assert "refs['ref_p']" in js
    assert "?.current" in js
    assert "?.play?.()" in js


def test_pause_calls_element_pause():
    assert "?.pause?.()" in js_of(controls.pause("p"))


def test_request_fullscreen():
    assert "?.requestFullscreen?.()" in js_of(controls.request_fullscreen("p"))


def test_seek_to_sets_current_time():
    js = js_of(controls.seek_to("p", 12))
    assert "p.currentTime = 12" in js


def test_seek_relative_adds_delta():
    js = js_of(controls.seek_relative("p", 10))
    assert "(p.currentTime || 0) + (10)" in js


def test_seek_fraction_scales_duration():
    js = js_of(controls.seek_fraction("p", 0.5))
    assert "(0.5) * p.duration" in js
    assert "p.duration" in js  # guarded: only when duration is known
