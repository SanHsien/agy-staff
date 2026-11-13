## Dispatch

- Continue a completed job with `continue --job <id> --prompt "..."` when the task and persona are the same and prior context helps, even if the user does not say "continue". Keep each job ID with its assignment; if the target is unclear, check known jobs before asking the user.
- Start fresh for a different task or persona, an independent opinion, or an explicit fresh start. Carry relevant findings and artifact paths into the new brief.
- Pass the user's task and explicit authorizations verbatim. On follow-up, add decisions and constraints from the host chat that the worker has not seen. Continuation does not expand authorization.
- Run the companion unsandboxed; in Codex, request escalated execution. Follow `../jobs/SKILL.md` for collection and recovery. After an execution timeout, obtain explicit user confirmation before continuing or restarting.

## Model selection

- Worker defaults use Gemini 4 Hydrogen. `--effort low|medium|high|xhigh` selects its tier; `--model` accepts `hydrogen`, `carbon`, `argon`, `flash`, `pro`, or an effort-suffixed ID. Carbon and Argon have low/medium/high tiers; requesting xhigh on those families selects high with a warning.
- `flash` remains an explicit Gemini 3.8 Flash alias. Continuation keeps the recorded model unless overridden. Unavailable models fail with diagnostics and compatible recommendations; do not automatically retry or switch models.
