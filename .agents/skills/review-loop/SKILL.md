---
name: review-loop
description: >-
  Route and execute the repository's review-and-fix loop through the existing canonical workflow. Use for branching,
  splitting work into commits, pushing, opening a pull request, triggering an automated reviewer, waiting for its
  verdict, classifying and fixing its findings, and optionally merging once the loop converges.
---

# Review Loop

## Select the canonical workflow

Read `.claude/commands/pr/review-loop.md` in full before touching git, the GitHub API, or any file. It is the source
of truth for this workflow; do not copy its procedure into this skill or improvise a parallel one.

When the request is about the _content_ of a change rather than getting it reviewed, this skill does not apply. Follow
`docs/development/working-agreements.md` and the relevant coding guide instead. This skill only carries a finished
change to a pull request and back.

## Adapt the workflow to Codex

- Interpret `$ARGUMENTS` as the reviewer, merge, unattended, round-cap, and timeout flags supplied in the current
  user request. Echo the resolved configuration before acting.
- Ignore Claude Code `allowed-tools` declarations. Use Codex filesystem, shell, and network tools with equivalent
  scope, and request scoped approval before network access — `.codex/config.toml` sets `network_access = false`,
  and every `gh` call in the workflow needs the network.
- Translate `Read` to file inspection, `Edit`/`Write` to patches, `Grep`/`Glob` to `rg`, and `Bash` to shell
  execution. Run the workflow's npm commands exactly as it writes them; its 注意 section says whether to prefix
  them and why.
- **The wait step has no Codex equivalent.** Step 8's script is written to be launched detached so the model is
  re-invoked once when it exits. Run it as an ordinary foreground shell command instead, keeping the script
  byte-identical and its 480-second budget intact, and re-run it while the verdict is `pending`. Step 12's CI wait
  has the same shape and the same rule. Do not replace either poll with a shorter sleep or a single API call — the
  endpoints they watch are the whole point.
- **The reviewer is the GitHub Codex app, not this Codex session.** `@codex review` posts to
  `chatgpt-codex-connector[bot]`, which reviews the pushed diff independently. Do not answer your own trigger, and do
  not treat your own reasoning as the review.

## Execute and verify

Preserve the workflow's stop conditions, its abort paths, and the invariants its 注意 section states — including the
two it calls out for re-triggering and for acting on a review. Report the round count, the classification of every
finding, the checks that ran, any check that could not run, and the reason for an abort.
