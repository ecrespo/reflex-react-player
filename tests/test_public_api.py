def test_top_level_imports():
    from reflex_react_player import (  # noqa: F401
        REACT_PLAYER_VERSION,
        ReactPlayer,
        controls,
        react_player,
    )

    assert react_player == ReactPlayer.create
    assert REACT_PLAYER_VERSION == "react-player@3.4.0"
    assert hasattr(controls, "play")
    assert hasattr(controls, "seek_relative")


def test_version_string_present():
    import reflex_react_player

    assert isinstance(reflex_react_player.__version__, str)
