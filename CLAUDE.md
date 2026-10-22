# Working principles

## Scope

- Build only what is asked for. The target is an importable module; add no command-line interface or other entry points unless requested.
- Prefer the smallest API that does the job.

## Code structure

- Use plain functions that call each other. No classes or dataclasses for results; return plain values or tuples.
- Keep a calculation readable in one place. Do not split a short computation into tiny helpers; avoid indirection and nesting.

## Math

- Write equations in LaTeX inside `$$ … $$` (inline: `$ … $`), not in Unicode symbols.

## Tests

- Besides shapes, ranges and known values, test the mathematical properties of the result, such as symmetries and invariances.
