# SDD Overview & Phases — reflex-react-player

**Status:** Approved (baseline) · **Owner:** Ernesto Crespo · **Last updated:** 2026-06-21
**Audience:** Contributors and maintainers of `reflex-react-player`.

This repository is developed using **Spec-Driven Design (SDD)**: specifications are
the primary artifact. We define *what* to build, *why*, and *how* before writing
code. The documents in `docs/sdd/` are version-controlled and updated whenever
requirements change.

## What we are building

`reflex-react-player` is a **Reflex custom component** that wraps the npm library
[`react-player` v3](https://github.com/cookpete/react-player). It lets Reflex
(Python) developers embed a versatile media player — files, audio, HLS, DASH,
YouTube, Vimeo, Wistia, Mux, Spotify, Twitch and TikTok — with a Pythonic API
for props, events and imperative control. The repository ships the component
**plus a demo app** that reproduces every example from the official react-player
demo.

## SDD document set

This is a new, self-contained library with a non-trivial JS interop surface, so
we maintain the full document set (adapted to a component library rather than a
service):

| Document | Role in SDD flow | File |
|----------|------------------|------|
| Overview & Phases | Project framing, the phase plan | `00-overview.md` (this file) |
| PRD | The **What** and **Why** | `01-prd.md` |
| Architecture / Tech Design | The **How** | `02-architecture.md` |
| Component Specification (API contract) | The **Contract** (props/events/methods) | `03-component-spec.md` |
| Implementation Plan | Phases with verifiable "Done" criteria | `04-plan.md` |
| Tasks | Granular, trackable work items | `05-tasks.md` |

> There is no traditional data-model document: the component is stateless on the
> server; "state" is the controlled React props plus media events. The closest
> analog (the event/state payload shapes) is specified in `03-component-spec.md`.

## Phase plan (high level)

```
Phase 0  Research & SDD baseline      ── this branch (main)
Phase 1  Core component wrapper       ── props + NoSSR + default export
Phase 2  Events & state contract      ── media-event arg specs
Phase 3  Imperative control helpers   ── ref-based seek/play/pause
Phase 4  Demo application             ── all react-player examples
Phase 5  Packaging & docs             ── pyproject, README, type stubs
Phase 6  Verification & publish       ── tests, manual QA, GitHub + PyPI
```

Each phase and its acceptance criteria are detailed in `04-plan.md`; the task
breakdown is in `05-tasks.md`.

## Guiding principles

1. **Client-only by design.** react-player touches `window`, so the wrapper is a
   `NoSSRComponent`. This is non-negotiable and underpins the architecture.
2. **Faithful to react-player v3.** We track v3 semantics (`src` not `url`,
   native `HTMLMediaElement` events, ref-based instance methods) rather than v2.
3. **Pythonic ergonomics.** snake_case props, typed `rx.Var`s, event handlers
   that receive plain serializable dicts — not raw SyntheticEvents.
4. **Versatile demo.** The demo is living documentation and the manual test bed;
   it must cover every supported provider and control.
5. **Specs as living code.** Any behavioral change updates the relevant spec in
   the same PR (Definition of Done).

## Cross-spec validation checklist

- [ ] Every PRD MUST requirement maps to a prop/event/helper in the component spec.
- [ ] Every prop/event in the component spec is exercised by the demo or a test.
- [ ] Architecture decisions (NoSSR, default export, event extraction) are
      reflected in the implementation and called out in the README.
- [ ] The implementation plan references every spec and covers every phase.
