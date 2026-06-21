"""A Reflex wrapper around react-player v3 (https://github.com/cookpete/react-player)."""

from __future__ import annotations

from reflex.components.component import NoSSRComponent

# Pinned npm version for reproducible builds (ADR-6). Bump deliberately.
REACT_PLAYER_VERSION = "react-player@3.4.0"


class ReactPlayer(NoSSRComponent):
    """A versatile media player wrapping react-player v3."""

    library = REACT_PLAYER_VERSION
    tag = "ReactPlayer"
    alias = "ReactPlayer"
    is_default = True  # react-player is the package's default export.


react_player = ReactPlayer.create
