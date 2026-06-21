from reflex_react_player.react_player import ReactPlayer, react_player

# snake_case props that should auto-camelCase or pass straight through.
PLAIN_PROPS = [
    "src", "playing", "loop", "controls", "light", "volume", "muted", "pip",
    "width", "height", "poster", "preload", "config",
]

# snake_case -> expected camelCase JS prop name.
RENAMED_PROPS = {
    "playback_rate": "playbackRate",
    "plays_inline": "playsInline",
    "auto_play": "autoPlay",
    "cross_origin": "crossOrigin",
    "disable_remote_playback": "disableRemotePlayback",
    "disable_picture_in_picture": "disablePictureInPicture",
    "preview_tab_index": "previewTabIndex",
    "preview_aria_label": "previewAriaLabel",
    "o_embed_url": "oEmbedUrl",
}


def test_all_documented_props_declared():
    declared = set(ReactPlayer.get_props())
    for name in PLAIN_PROPS + list(RENAMED_PROPS):
        assert name in declared, f"prop not declared as rx.Var: {name}"


def test_no_style_prop_declared():
    # style is built into every Reflex component; redeclaring it breaks _post_init
    # on Reflex >= 0.9 (TypeError: 'NoneType' object is not a mapping). See ADR-7.
    assert "style" not in ReactPlayer.get_props()


def test_renamed_props_render_camelcase():
    comp = react_player(
        playback_rate=1.5,
        plays_inline=True,
        auto_play=True,
        cross_origin="anonymous",
        disable_remote_playback=True,
        disable_picture_in_picture=True,
        preview_tab_index=2,
        preview_aria_label="play",
        o_embed_url="https://oembed.example/x",
    )
    out = str(comp.render())
    for snake, camel in RENAMED_PROPS.items():
        assert camel in out, f"{snake} did not render as {camel}"
    # No style passed -> declared props must NOT leak into a css blob.
    assert "css:" not in out, "declared props leaked into css (are they declared?)"
