# Session log: planning and orchestrated implementation of `montepi`

A record of one Claude Code session (2026-10-22, Claude Opus 5.5, medium effort,
concise output style). User messages and inline remarks are verbatim. Claude's
replies are condensed; tool calls are summarised in brackets.

## 1. Request a plan

**User:**
> Let's write a small package that calculates PI from a Monte Carlo integral in a unit square / circle. We need a module with tests and visualisation.
> Write a short plan for the implementation. Make sure the plan is ready for parallel implementation.

**Claude:** [checked the empty directory and the available tools: `uv`, `pixi`] Wrote
`PLAN.md`. Its key idea for parallel work is an interface contract frozen up front,
so that every work package codes against signatures, not against other packages.
- WP-0 (scaffold) runs first, sequentially.
- WP-A (core), WP-B (core tests), WP-C (plotting and its tests) and WP-D (CLI and README) touch disjoint files and run in parallel.
- An integration step follows.

The first contract had a `PiEstimate` dataclass, an `inside_circle` helper, `estimate_pi(n, seed)`, `running_estimate`, and a CLI.

## 2. Put the plan under version control

**User:**
> Git init and commit the plan. My comments will be inline changes

**Claude:** [`git init`, committed `PLAN.md`]

## 3. Review by inline remarks

The user edited `PLAN.md` directly. Claude read the remarks from `git diff`:

```
<!-- Don't use unicode for equations. Use $$ and latex equations. -->
# Let's remove the command-line interface. Target is an importable module.
# No object orientation. Just a few functions calling each other.
# THat's too much indirection / nesting. Let's keep the whole logic from the (x,y) sequence to pi in one function.
<!-- Let's also check symmetry. The result should not depend on x<->y swaps. -->
```

**User:**
> See my remarks. List them all. Summarize. Generalize.

**Claude:** Listed the five remarks and summarised them: drop the CLI and the dataclass, put
the whole computation in one function, write equations in LaTeX, and test symmetry.
It then generalised them into principles:
- Build the minimal API: flat functions, with structure added only on request.
- Keep the computation readable in one place.
- Add no unrequested surface such as CLIs.
- Write math as LaTeX.
- Test mathematical invariances, not only shapes and values.

## 4. Revise the plan, codify the principles

**User:**
> Ok.
> 1. rewrite the plan accordingly.
> 2. write the general principles into a CLAUDE.md

**Claude:** Rewrote `PLAN.md`. The new contract has `sample_points(n, seed) -> (x, y)`,
`estimate_pi(x, y) -> (pi_hat, std_error)` and `running_estimate(x, y)`, plus
`plot_samples` and `plot_convergence`. The plan has LaTeX equations, a symmetry test,
and WP-D reduced to the README. Claude wrote the principles to `CLAUDE.md` and dropped a
duplicate memory note.

Design decision Claude made explicitly: `estimate_pi` and `running_estimate` each contain
the full path from (x, y) to pi, so the inside test appears twice rather than in a helper.

## 5. Implement with orchestration

**User:**
> Plan accepted. COmmit plan and CLAUDE.md.
>
> Then, go on and implement. Use a subagent for the WP0 (scaffold). Then use /workflows with opus medium for testing and sonnet medium for implementers and opus medium for reviewers / refuters. You fix what the reviewers find in the end.

**Claude:**
1. Committed the plan and `CLAUDE.md`.
2. Ran WP-0 with a single Sonnet subagent, checked its output (pytest collected 0 tests and exited with code 5), and committed it.
3. Launched one workflow in three phases:
   - **Implement:** a barrier over 5 parallel agents. Sonnet wrote `core.py`, `plot.py` and `README.md`. Opus wrote `test_core.py` and `test_plot.py` against the contract only.
   - **Review:** 3 Opus reviewers with distinct lenses: correctness, test quality, and adherence to PLAN.md and CLAUDE.md.
   - **Refute:** one Opus refuter per finding, pipelined behind its reviewer and told to default to "refuted".

   The workflow used 13 agents, about 480k subagent tokens and about 85 s.
4. Results: 5 findings, of which 4 were confirmed and 1 refuted.
   - Confirmed: matplotlib was only in the `plot` extra, so a plain `uv sync && uv run pytest` silently skipped all plot tests.
   - Confirmed: no test covered the inside/outside colouring.
   - Confirmed: no test covered the quarter-circle arc or the artist count.
   - Confirmed: no test covered the ±2σ band.
   - Refuted: the claimed std-error bug for x and y of unequal length did not reproduce.
5. Claude fixed all four itself: it added matplotlib to the dev group and wrote three new tests. It mutation-checked each new test against a deliberately broken `plot.py` in a scratch copy, and each mutation made exactly one test fail. It also ran the README example (pi_hat = 3.1414 ± 0.0016 at n = 10^6). The final result was 38 tests passing.

## 6. Wrap up

**User:**
> OK. Commit this. And also commit a summary of my interactions with you (as verbatim as possible) so I can use this for training and illustration.

**Claude:** Committed the implementation and this file.

## Takeaways for orchestration

- Freeze the interface contract before parallel work; it is what makes disjoint work packages possible.
- Review a plan by inline edits in git, then ask the model to list, summarise and generalise the remarks. The generalisations go into `CLAUDE.md`, so every later subagent inherits them.
- Mix models by role: cheaper implementers, stronger test writers and reviewers. Test writers code against the contract, not against the implementation.
- Put an adversarial refuter behind each review finding. Here it removed one false positive.
- The orchestrator verifies the final fixes itself. Mutation checks show that new tests can fail.
