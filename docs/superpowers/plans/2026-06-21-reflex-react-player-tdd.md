# reflex-react-player — TDD Greenfield Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the `reflex_react_player` component library (`react_player.py`, `controls.py`, `__init__.py`) from scratch, test-first, so every prop/event/helper in `docs/sdd/03-component-spec.md` is driven by a failing-then-passing unit test.

**Architecture:** A Reflex `NoSSRComponent` subclass wraps the react-player v3 default export. Client-side event arg-specs extract a serializable media-state dict from native `HTMLMediaElement` events. Imperative control is decoupled from the instance via `rx.call_script` against `refs['ref_<id>'].current`. All three behaviours are unit-testable in pure Python (no Node/browser) by inspecting the rendered component, its event triggers, the arg-spec JS strings, and the `call_script` payloads.

**Tech Stack:** Python 3.13 (floor 3.9), Reflex 0.9.5 (floor 0.8.0), pytest 9, react-player@3.4.0 (npm, pinned).

## Global Constraints

Copied verbatim from the SDD specs — every task implicitly includes these:

- **NFR-1:** Pin `react-player@3.4.0` exactly in `library` (ADR-6). String must be `"react-player@3.4.0"`.
- **NFR-2:** Component is a `NoSSRComponent` (client-only). Subclass `reflex.components.component.NoSSRComponent`.
- **NFR-3:** `is_default = True` (react-player is a default export). Omitting it is the canonical "Invalid Element Type" failure.
- **NFR-4:** Works with Reflex ≥ 0.8.0 and Python ≥ 3.9.
- **ADR-3:** Events deliver serializable media-state dicts, never raw SyntheticEvents.
- **ADR-4:** Imperative control uses refs + `rx.call_script`; all JS uses optional chaining (`?.`) because the ref is null before mount.
- **ADR-5:** Rely on Reflex auto snake_case→camelCase; use `_rename_props` only for names that need it (`o_embed_url` → `oEmbedUrl`).
- **Public API:** `from reflex_react_player import react_player, ReactPlayer, controls` must work (component-spec §1).
- **Known trap (discovered during planning):** Do **NOT** declare a `style` prop. `style` is built into every Reflex component; redeclaring it as `rx.Var[dict]` breaks `Component._post_init` on Reflex 0.9.5 with `TypeError: 'NoneType' object is not a mapping`. Layout via `width`/`height` props + the built-in `style`.
- **Media-state dict keys (the public payload contract, ADR-3 / arch §5):** `current_time, duration, played, played_seconds, loaded, loaded_seconds, playback_rate, volume, muted, paused`.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `pyproject.toml` | Add `[tool.pytest.ini_options]` so `reflex_react_player` imports from `custom_components/` without an editable install. |
| `custom_components/reflex_react_player/react_player.py` | `ReactPlayer(NoSSRComponent)` + the four event arg-spec functions. |
| `custom_components/reflex_react_player/controls.py` | Imperative ref helpers returning `rx.call_script` `EventSpec`s. |
| `custom_components/reflex_react_player/__init__.py` | Public API surface + `__version__`. |
| `tests/test_wiring.py` | Library/tag/default/NoSSR wiring (component-spec §7, ADR-1/2). |
| `tests/test_props.py` | Prop declaration + camelCase rendering (component-spec §2). |
| `tests/test_arg_specs.py` | Arg-spec JS extraction (ADR-3, arch §5). |
| `tests/test_events.py` | All event triggers exist and are wired to the right spec (component-spec §3). |
| `tests/test_controls.py` | Each control helper's `call_script` JS + callback (component-spec §4). |
| `tests/test_public_api.py` | Import contract (component-spec §1). |

**Note on scope:** Tasks 0–11 are the greenfield TDD rebuild (pure-Python, fully automatable). Tasks 12–15 are environment-gated verification (need Node/browser) and open backlog items; they are listed for completeness with explicit manual steps, not red/green cycles.

---

### Task 0: Test harness & clean slate

Make the package importable under pytest, then blank the implementation so every later test starts genuinely red.

**Files:**
- Modify: `pyproject.toml` (append a pytest config table)
- Modify: `custom_components/reflex_react_player/react_player.py` (reduce to a stub)
- Modify: `custom_components/reflex_react_player/controls.py` (reduce to a stub)
- Modify: `custom_components/reflex_react_player/__init__.py` (reduce to a stub)
- Delete: `tests/test_component.py` (replaced by the focused suites below)

**Interfaces:**
- Produces: a pytest run that collects `tests/` with `custom_components/` on `sys.path`.

- [ ] **Step 1: Add pytest config to `pyproject.toml`**

Append at the end of the file:

```toml
[tool.pytest.ini_options]
pythonpath = ["custom_components"]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 2: Blank the implementation files to stubs**

`custom_components/reflex_react_player/react_player.py`:

```python
"""Stub — rebuilt test-first in the TDD plan."""
```

`custom_components/reflex_react_player/controls.py`:

```python
"""Stub — rebuilt test-first in the TDD plan."""
```

`custom_components/reflex_react_player/__init__.py`:

```python
"""Stub — rebuilt test-first in the TDD plan."""
```

- [ ] **Step 3: Remove the old smoke test**

```bash
git rm tests/test_component.py
```

- [ ] **Step 4: Verify pytest collects an empty suite cleanly**

Run: `uv run --no-project python -m pytest`
Expected: `no tests ran` (exit code 5) — NOT an import/collection error. This proves the harness works before any test exists.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml custom_components/reflex_react_player tests
git commit -m "test: reset component to stubs and wire pytest pythonpath for TDD rebuild"
```

---

### Task 1: Library / export wiring

**Files:**
- Modify: `custom_components/reflex_react_player/react_player.py`
- Test: `tests/test_wiring.py`

**Interfaces:**
- Produces: `ReactPlayer` (a `NoSSRComponent` subclass) with `library`, `tag`, `alias`, `is_default`; and `react_player = ReactPlayer.create`.

- [ ] **Step 1: Write the failing test**

`tests/test_wiring.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_wiring.py`
Expected: FAIL — `ImportError: cannot import name 'ReactPlayer'`.

- [ ] **Step 3: Write minimal implementation**

Replace `react_player.py` with:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_wiring.py`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/react_player.py tests/test_wiring.py
git commit -m "feat: ReactPlayer NoSSR wiring (library/tag/default export)"
```

---

### Task 2: Core, layout, native & light props (camelCase rendering)

**Files:**
- Modify: `custom_components/reflex_react_player/react_player.py`
- Test: `tests/test_props.py`

**Interfaces:**
- Consumes: `react_player` factory from Task 1.
- Produces: typed `rx.Var` props that render to the documented camelCase JS names. **No `style` prop** (built-in; see Global Constraints).

- [ ] **Step 1: Write the failing test**

`tests/test_props.py`:

> **Why `get_props()` and not just substring-in-render:** Reflex routes *undeclared*
> kwargs into a `css:({...})` blob rather than rejecting them, so a bare
> `assert "playbackRate" in render()` passes even when the prop is **not** declared —
> the test could never go red. `ReactPlayer.get_props()` returns only the names
> declared as `rx.Var` (snake_case), so membership there is the real driver. The
> render check then confirms the rename actually reaches the JSX **and** that nothing
> leaked into `css:`.

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_props.py`
Expected: FAIL — `test_all_documented_props_declared` fails because `get_props()` is empty
(no props declared yet); `test_renamed_props_render_camelcase` fails on the `css:` leak
assertion (undeclared kwargs land in css).

- [ ] **Step 3: Write minimal implementation**

In `react_player.py`, add imports and the prop declarations + `_rename_props` to the class. Insert after the existing imports:

```python
from typing import Any, Union

import reflex as rx
```

Add inside `class ReactPlayer` (after `is_default = True`):

```python
    # --- core playback props (snake_case -> camelCase automatically) ------
    src: rx.Var[str]
    playing: rx.Var[bool]
    loop: rx.Var[bool]
    controls: rx.Var[bool]
    light: rx.Var[Union[bool, str]]
    volume: rx.Var[float]
    muted: rx.Var[bool]
    playback_rate: rx.Var[float]          # -> playbackRate
    pip: rx.Var[bool]
    plays_inline: rx.Var[bool]            # -> playsInline

    # --- layout (NOTE: no `style` prop — it is built in) ------------------
    width: rx.Var[Union[str, int]]
    height: rx.Var[Union[str, int]]

    # --- native passthrough attributes ------------------------------------
    auto_play: rx.Var[bool]               # -> autoPlay
    preload: rx.Var[str]
    cross_origin: rx.Var[str]             # -> crossOrigin
    poster: rx.Var[str]
    disable_remote_playback: rx.Var[bool]        # -> disableRemotePlayback
    disable_picture_in_picture: rx.Var[bool]     # -> disablePictureInPicture

    # --- light / preview-mode props ---------------------------------------
    preview_tab_index: rx.Var[int]        # -> previewTabIndex
    preview_aria_label: rx.Var[str]       # -> previewAriaLabel
    o_embed_url: rx.Var[str]              # -> oEmbedUrl (see _rename_props)

    # --- per-player configuration -----------------------------------------
    config: rx.Var[dict[str, Any]]

    # snake_case -> camelCase covers everything except names that need a hint.
    _rename_props: dict[str, str] = {
        "o_embed_url": "oEmbedUrl",
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_props.py`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/react_player.py tests/test_props.py
git commit -m "feat: declare react-player props with camelCase rendering (no style prop)"
```

---

### Task 3: Event arg specs (media-state extraction JS)

**Files:**
- Modify: `custom_components/reflex_react_player/react_player.py`
- Test: `tests/test_arg_specs.py`

**Interfaces:**
- Produces: `_media_state_spec(e) -> list[Var]`, `_duration_spec(e) -> list[Var]`, `_error_spec(e) -> list[Var]`, `_empty_spec() -> list[Var]`. Each non-empty spec returns a one-element list whose `[0]._js_expr` is the generated client JS.

- [ ] **Step 1: Write the failing test**

`tests/test_arg_specs.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_arg_specs.py`
Expected: FAIL — `ImportError: cannot import name '_media_state_spec'`.

- [ ] **Step 3: Write minimal implementation**

In `react_player.py`, add `from reflex.vars import Var` to the imports, then insert these module-level functions **above** `class ReactPlayer`:

```python
def _media_state_spec(e: Var) -> list[Var]:
    """Extract a serializable media-state snapshot from a native media event.

    `played`/`loaded` are normalized 0..1 fractions (handy for progress bars).
    """
    expr = (
        "(() => {"
        f" const t = {e!s}?.target;"
        " if (!t) return {current_time: 0, duration: 0, played: 0,"
        " played_seconds: 0, loaded: 0, loaded_seconds: 0,"
        " playback_rate: 1, volume: 1, muted: false, paused: true};"
        " const d = t.duration || 0;"
        " let le = 0;"
        " try { le = (t.buffered && t.buffered.length)"
        " ? t.buffered.end(t.buffered.length - 1) : 0; } catch (_) { le = 0; }"
        " return {"
        " current_time: t.currentTime || 0,"
        " duration: d,"
        " played: d ? (t.currentTime || 0) / d : 0,"
        " played_seconds: t.currentTime || 0,"
        " loaded: d ? le / d : 0,"
        " loaded_seconds: le,"
        " playback_rate: t.playbackRate || 1,"
        " volume: (t.volume === undefined ? 1 : t.volume),"
        " muted: !!t.muted,"
        " paused: !!t.paused"
        " };"
        "})()"
    )
    return [Var(_js_expr=expr, _var_type=dict)]


def _duration_spec(e: Var) -> list[Var]:
    """`onDurationChange` -> duration in seconds (float)."""
    return [Var(_js_expr=f"({e!s}?.target?.duration || 0)", _var_type=float)]


def _empty_spec() -> list[Var]:
    """Callbacks with no useful forwarded argument (e.g. `onReady`)."""
    return []


def _error_spec(e: Var) -> list[Var]:
    """`onError` -> best-effort stringified error message."""
    return [
        Var(
            _js_expr=(
                f"(({e!s} && ({e!s}.message || ({e!s}.target && {e!s}.target.error"
                f" && {e!s}.target.error.message))) || 'media error')"
            ),
            _var_type=str,
        )
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_arg_specs.py`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/react_player.py tests/test_arg_specs.py
git commit -m "feat: event arg specs extracting serializable media-state (ADR-3)"
```

---

### Task 4: Event triggers wired to arg specs

**Files:**
- Modify: `custom_components/reflex_react_player/react_player.py`
- Test: `tests/test_events.py`

**Interfaces:**
- Consumes: the arg-spec functions from Task 3.
- Produces: 18 `rx.EventHandler` triggers on `ReactPlayer`, exposed via `get_event_triggers()`.

- [ ] **Step 1: Write the failing test**

`tests/test_events.py`:

```python
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
    # Reflex injects base handlers (e.g. on_mount/on_unmount); allow those.
    base = {"on_mount", "on_unmount"}
    assert custom <= base, f"unexpected triggers: {custom - base}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_events.py`
Expected: FAIL — most names missing from `get_event_triggers()`.

- [ ] **Step 3: Write minimal implementation**

Add inside `class ReactPlayer` (after the `config` prop, before `_rename_props`):

```python
    # --- event triggers ---------------------------------------------------
    on_ready: rx.EventHandler[_empty_spec]
    on_start: rx.EventHandler[_empty_spec]
    on_play: rx.EventHandler[_media_state_spec]
    on_pause: rx.EventHandler[_media_state_spec]
    on_ended: rx.EventHandler[_media_state_spec]
    on_error: rx.EventHandler[_error_spec]
    on_duration_change: rx.EventHandler[_duration_spec]   # -> onDurationChange
    on_progress: rx.EventHandler[_media_state_spec]
    on_time_update: rx.EventHandler[_media_state_spec]    # -> onTimeUpdate
    on_seeking: rx.EventHandler[_media_state_spec]
    on_seeked: rx.EventHandler[_media_state_spec]
    on_waiting: rx.EventHandler[_media_state_spec]
    on_playing: rx.EventHandler[_media_state_spec]
    on_rate_change: rx.EventHandler[_media_state_spec]    # -> onRateChange
    on_volume_change: rx.EventHandler[_media_state_spec]  # -> onVolumeChange
    on_enter_picture_in_picture: rx.EventHandler[_empty_spec]
    on_leave_picture_in_picture: rx.EventHandler[_empty_spec]
    on_click_preview: rx.EventHandler[_empty_spec]        # light-mode preview
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_events.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/react_player.py tests/test_events.py
git commit -m "feat: wire all 18 react-player event triggers"
```

---

### Task 5: Imperative controls — play / pause / fullscreen

**Files:**
- Create: `custom_components/reflex_react_player/controls.py`
- Test: `tests/test_controls.py`

**Interfaces:**
- Produces: `play(player_id) -> EventSpec`, `pause(player_id) -> EventSpec`, `request_fullscreen(player_id) -> EventSpec`, and a private `_ref(player_id) -> str`. JS is extractable via `spec.args[0][1]._var_value`.

- [ ] **Step 1: Write the failing test**

`tests/test_controls.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: FAIL — `module 'controls' has no attribute 'play'` (or import error).

- [ ] **Step 3: Write minimal implementation**

Create `controls.py`:

```python
"""Imperative client-side control helpers for :class:`ReactPlayer`.

react-player v3 exposes its instance API through the forwarded ref, which points
at the underlying ``HTMLMediaElement``. Reflex stores a component's ref (when it
has an ``id``) in the global ``refs`` object as ``refs['ref_<id>']``. These
helpers return ``rx.call_script(...)`` events so the player can be driven from any
Python event handler. All JS uses optional chaining because the ref is null
before the client mounts (ADR-4).
"""

from __future__ import annotations

import reflex as rx
from reflex.event import EventSpec


def _ref(player_id: str) -> str:
    """JS expression resolving to the player's HTMLMediaElement (or undefined)."""
    return f"refs['ref_{player_id}']?.current"


def play(player_id: str) -> EventSpec:
    """Start playback."""
    return rx.call_script(f"{_ref(player_id)}?.play?.()")


def pause(player_id: str) -> EventSpec:
    """Pause playback."""
    return rx.call_script(f"{_ref(player_id)}?.pause?.()")


def request_fullscreen(player_id: str) -> EventSpec:
    """Request native fullscreen for the player element."""
    return rx.call_script(f"{_ref(player_id)}?.requestFullscreen?.()")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/controls.py tests/test_controls.py
git commit -m "feat: controls play/pause/fullscreen via call_script + refs"
```

---

### Task 6: Imperative controls — seek (absolute / relative / fraction)

**Files:**
- Modify: `custom_components/reflex_react_player/controls.py`
- Test: `tests/test_controls.py`

**Interfaces:**
- Consumes: `_ref`, `js_of` test helper from Task 5.
- Produces: `seek_to(player_id, seconds)`, `seek_relative(player_id, delta_seconds)`, `seek_fraction(player_id, fraction)`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_controls.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: FAIL — `module 'controls' has no attribute 'seek_to'`.

- [ ] **Step 3: Write minimal implementation**

Append to `controls.py`:

```python
def seek_to(player_id: str, seconds: float) -> EventSpec:
    """Seek to an absolute time in seconds."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.currentTime = {seconds}; }}"
    )


def seek_relative(player_id: str, delta_seconds: float) -> EventSpec:
    """Seek forward (positive) or backward (negative) by ``delta_seconds``."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.currentTime = "
        f"(p.currentTime || 0) + ({delta_seconds}); }}"
    )


def seek_fraction(player_id: str, fraction: float) -> EventSpec:
    """Seek to a 0..1 fraction of the total duration (slider scrubbing)."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p && p.duration) "
        f"p.currentTime = ({fraction}) * p.duration; }}"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/controls.py tests/test_controls.py
git commit -m "feat: controls seek_to/seek_relative/seek_fraction"
```

---

### Task 7: Imperative controls — volume / playback rate

**Files:**
- Modify: `custom_components/reflex_react_player/controls.py`
- Test: `tests/test_controls.py`

**Interfaces:**
- Produces: `set_volume(player_id, volume)`, `set_playback_rate(player_id, rate)`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_controls.py`:

```python
def test_set_volume():
    assert "p.volume = 0.5" in js_of(controls.set_volume("p", 0.5))


def test_set_playback_rate():
    assert "p.playbackRate = 1.5" in js_of(controls.set_playback_rate("p", 1.5))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: FAIL — `module 'controls' has no attribute 'set_volume'`.

- [ ] **Step 3: Write minimal implementation**

Append to `controls.py`:

```python
def set_volume(player_id: str, volume: float) -> EventSpec:
    """Set volume (0..1) directly on the element."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.volume = {volume}; }}"
    )


def set_playback_rate(player_id: str, rate: float) -> EventSpec:
    """Set the playback rate directly on the element."""
    return rx.call_script(
        f"{{ const p = {_ref(player_id)}; if (p) p.playbackRate = {rate}; }}"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: PASS (8 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/controls.py tests/test_controls.py
git commit -m "feat: controls set_volume/set_playback_rate"
```

---

### Task 8: Imperative controls — read-back helpers with callback

**Files:**
- Modify: `custom_components/reflex_react_player/controls.py`
- Test: `tests/test_controls.py`

**Interfaces:**
- Produces: `get_current_time(player_id, callback)`, `get_duration(player_id, callback)`. The JS read expression is at `spec.args[0][1]`; the callback is wired at `spec.args[1][1]` (not the `null` literal).

- [ ] **Step 1: Write the failing test**

Append to `tests/test_controls.py`:

```python
import reflex as rx


class _S(rx.State):
    seconds: float = 0.0

    @rx.event
    def set_seconds(self, v: float):
        self.seconds = v


def test_get_current_time_reads_and_has_callback():
    spec = controls.get_current_time("p", _S.set_seconds)
    js = js_of(spec)
    assert "?.currentTime || 0" in js
    # second call_script arg is the callback; must not be the null literal.
    assert str(spec.args[1][1]) != "null"


def test_get_duration_reads_and_has_callback():
    spec = controls.get_duration("p", _S.set_seconds)
    assert "?.duration || 0" in js_of(spec)
    assert str(spec.args[1][1]) != "null"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: FAIL — `module 'controls' has no attribute 'get_current_time'`.

- [ ] **Step 3: Write minimal implementation**

Append to `controls.py`:

```python
def get_current_time(player_id: str, callback) -> EventSpec:
    """Read ``currentTime`` and pass it to a backend event handler.

    ``callback`` is a state setter / event handler accepting a float.
    """
    return rx.call_script(
        f"({_ref(player_id)}?.currentTime || 0)", callback=callback
    )


def get_duration(player_id: str, callback) -> EventSpec:
    """Read ``duration`` and pass it to a backend event handler."""
    return rx.call_script(
        f"({_ref(player_id)}?.duration || 0)", callback=callback
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_controls.py`
Expected: PASS (10 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/controls.py tests/test_controls.py
git commit -m "feat: controls get_current_time/get_duration with callback read-back"
```

---

### Task 9: Public API surface

**Files:**
- Modify: `custom_components/reflex_react_player/__init__.py`
- Test: `tests/test_public_api.py`

**Interfaces:**
- Consumes: everything above.
- Produces: top-level `react_player`, `ReactPlayer`, `controls`, `REACT_PLAYER_VERSION`, `__version__`.

- [ ] **Step 1: Write the failing test**

`tests/test_public_api.py`:

```python
def test_top_level_imports():
    from reflex_react_player import (  # noqa: F401
        REACT_PLAYER_VERSION,
        ReactPlayer,
        controls,
        react_player,
    )

    # `==` not `is`: ReactPlayer.create is a classmethod — each access yields a
    # fresh bound-method object, so identity fails; equality compares __func__/__self__.
    assert react_player == ReactPlayer.create
    assert REACT_PLAYER_VERSION == "react-player@3.4.0"
    assert hasattr(controls, "play")
    assert hasattr(controls, "seek_relative")


def test_version_string_present():
    import reflex_react_player

    assert isinstance(reflex_react_player.__version__, str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run --no-project python -m pytest tests/test_public_api.py`
Expected: FAIL — names not exported from the stub `__init__.py`.

- [ ] **Step 3: Write minimal implementation**

Replace `__init__.py`:

```python
"""reflex-react-player: a Reflex wrapper for react-player v3.

Public API::

    from reflex_react_player import react_player, ReactPlayer
    from reflex_react_player import controls  # imperative ref helpers
"""

from . import controls
from .react_player import REACT_PLAYER_VERSION, ReactPlayer, react_player

__version__ = "0.1.0"

__all__ = [
    "ReactPlayer",
    "react_player",
    "controls",
    "REACT_PLAYER_VERSION",
    "__version__",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run --no-project python -m pytest tests/test_public_api.py`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add custom_components/reflex_react_player/__init__.py tests/test_public_api.py
git commit -m "feat: export public API (react_player, ReactPlayer, controls)"
```

---

### Task 10: Full-suite green gate

**Files:**
- Test: all of `tests/`

- [ ] **Step 1: Run the whole suite**

Run: `uv run --no-project python -m pytest`
Expected: PASS — all tests green (≈ 27 across 6 files), zero collection errors.

- [ ] **Step 2: Confirm no `style`-prop regression**

Run: `uv run --no-project python -m pytest tests/test_props.py::test_no_style_prop_declared -v`
Expected: PASS — proves the Reflex 0.9.5 `_post_init` `TypeError` trap is closed.

- [ ] **Step 3: Commit (only if any incidental fix was needed; otherwise skip)**

```bash
git add -A
git commit -m "test: full contract suite green"
```

---

### Task 11: Update the SDD task ledger

The specs are living documents (Definition of Done). Record that the component was rebuilt test-first and the `style`-prop bug was fixed.

**Files:**
- Modify: `docs/sdd/05-tasks.md`
- Modify: `docs/sdd/02-architecture.md`

- [ ] **Step 1: Add a note to `02-architecture.md` §4 (module layout) or §6 (error handling)**

Add under §3 a short ADR addendum:

```markdown
### ADR-7 — Do not declare a `style` prop
**Context:** `style` is a built-in field on every Reflex component. Declaring
`style: rx.Var[dict]` on the subclass overrides it with a `None` default and
breaks `Component._post_init` (`TypeError: 'NoneType' object is not a mapping`)
on Reflex ≥ 0.9. **Decision:** Layout uses `width`/`height` props plus the
built-in `style`; the component declares no `style` prop. Covered by
`tests/test_props.py::test_no_style_prop_declared`.
```

- [ ] **Step 2: Reflect the test split in `05-tasks.md`**

Under "Phase 6 — Verification" replace the single `T6.1 Smoke tests` line with:

```markdown
- [x] T6.1 Contract test suite, test-first: wiring, props/camelCase, arg specs,
      event triggers, controls JS, public API (`tests/test_*.py`). (NFR-5)
```

- [ ] **Step 3: Commit**

```bash
git add docs/sdd/02-architecture.md docs/sdd/05-tasks.md
git commit -m "docs: record TDD rebuild + ADR-7 (no style prop) in SDD"
```

---

## Phase 2 — Environment-gated verification (manual; needs Node/browser)

These cannot be unit-tested in pure Python. Run on a machine with Node + a browser. They are listed with concrete commands rather than red/green cycles.

### Task 12: Demo frontend build smoke (FR-1, success-metric §6)

- [ ] In `reflex_react_player_demo/`, install deps: `pip install -r requirements.txt` then `pip install -e ..`.
- [ ] Run `reflex run` and confirm the frontend compiles with **no** "Invalid Element Type" error (the canonical default-export/NoSSR failure).
- [ ] Load the page; confirm the player mounts and a YouTube/file URL plays.
- [ ] Update `docs/sdd/04-plan.md` Phase 6 checkbox once verified.

### Task 13: Cross-provider manual QA (FR-3, T4.9)

- [ ] In the demo, switch source across at least one of each: file, HLS (`.m3u8`), DASH (`.mpd`), YouTube, Vimeo. Confirm each plays.
- [ ] Exercise transport (play/pause/±10s/fullscreen), speed buttons, seek slider, volume, controls/muted/loop/light toggles; confirm Played/Loaded bars + time readout update live.
- [ ] Tick `docs/sdd/05-tasks.md` T4.9.

### Task 14: Packaging build (T6.2)

- [ ] Run `python -m build`; confirm an sdist + wheel are produced under `dist/`.
- [ ] Confirm the wheel contains `reflex_react_player/` (package dir from `custom_components`).
- [ ] Tick `docs/sdd/05-tasks.md` T6.2.

### Task 15 (optional backlog): open enhancements

Pick up only if in scope for this milestone — each can follow the same TDD loop where unit-testable:
- [ ] T4.10 custom-URL loader input in the demo.
- [ ] T5.6 `.pyi` type stubs for editor autocomplete.
- [ ] B.3 CI workflow (the repo already has `.github/workflows/ci.yml` — verify it runs `uv run --no-project python -m pytest`).

---

## Self-Review

**Spec coverage (`03-component-spec.md`):**
- §1 Import → Task 9. ✓
- §2 Props (all rows, incl. camelCase renames + `o_embed_url`) → Task 2. ✓ (`style` intentionally omitted per ADR-7; layout via width/height.)
- §3 Events (all 18 + media-state dict shape) → Tasks 3–4. ✓
- §4 Control helpers (all 10) → Tasks 5–8. ✓
- §5 `config` prop → Task 2. ✓
- §6 Supported sources → exercised in manual QA Task 13 (provider selection is react-player's job; not unit-testable). ✓
- §7 Contract tests → Tasks 1–10 (this plan *is* the contract suite). ✓

**PRD MUST coverage:** FR-1/3 (manual QA, Tasks 12–13); FR-2/4/5/6 (props, Task 2); FR-7/8/10/12 (events, Task 4); FR-9/11 (controls, Tasks 5–8); NFR-1/2/3 (wiring, Task 1); NFR-4 (env: Reflex 0.9.5 ≥ 0.8.0, Py 3.13 ≥ 3.9); NFR-5 (suite, Task 10). ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code; every command states expected output. ✓

**Type/name consistency:** `_ref`/`js_of` defined in Task 5 and reused 6–8; arg-spec function names match between Task 3 (definition) and Task 4 (usage); `react_player`/`ReactPlayer`/`controls`/`REACT_PLAYER_VERSION` consistent across Tasks 1, 9. ✓

**Gap noted:** react-player provider *behaviour* (FR-3, §6 source matrix) and the `reflex run` build (NFR-3 success metric) are inherently Node/browser-gated and live in Phase 2, not the unit suite — by design, called out explicitly above.