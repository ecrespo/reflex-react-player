from reflex.components.component import NoSSRComponent

from reflex_react_player.react_player import ReactPlayer, react_player


def test_subclasses_no_ssr():
    assert issubclass(ReactPlayer, NoSSRComponent)


def test_library_pinned_exactly():
    assert ReactPlayer.library == "react-player@3.4.0"


def test_tag_and_alias():
    assert ReactPlayer.tag == "ReactPlayer"
    assert ReactPlayer.alias == "ReactPlayer"


def test_is_default_export():
    assert ReactPlayer.is_default is True


def test_factory_creates_instance():
    assert isinstance(react_player(), ReactPlayer)
