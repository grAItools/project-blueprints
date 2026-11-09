# project-blueprints

Recommended project blueprints for modern software development processes leveraging coding agents.

## Contents

- [`knowledge/harness-agnostic-project.md`](knowledge/harness-agnostic-project.md): Standalone foundation for sharing instructions, skills, and tool configuration across supported AI coding harnesses, for both new and existing project repositories.
- [`knowledge/python-project.md`](knowledge/python-project.md): Shared Python baseline for solo maintainers and small teams, with strong automated checks and little coordination overhead.
- [`knowledge/python-project-community.md`](knowledge/python-project-community.md): Extends the Python baseline with contributor governance, compatibility commitments, downstream testing, and shared release/access processes; includes applicable Scientific Python SPEC guidance.

Use the foundation, then the Python baseline. Add the community extension when
external contributions, shared maintainership, downstream consumers, or ecosystem
commitments need formal coordination. Tool configuration and commands are owned
by the baseline and inherited by the extension, including all four blocking
type checkers.

Blueprints link only to their prerequisites; this index owns profile selection.

## Credits

Harness integration reference: [davidgibsonp's gist](https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05).
