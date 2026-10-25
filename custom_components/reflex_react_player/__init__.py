"""reflex-react-player: a Reflex wrapper for react-player v3.

Public API::

    from reflex_react_player import react_player, ReactPlayer
    from reflex_react_player import controls  # imperative ref helpers
"""

from . import controls
from .react_player import REACT_PLAYER_VERSION, ReactPlayer, react_player

__version__ = "0.2.0"

__all__ = [
    "ReactPlayer",
    "react_player",
    "controls",
    "REACT_PLAYER_VERSION",
    "__version__",
]
