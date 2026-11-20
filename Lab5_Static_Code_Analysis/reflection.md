# Lab 5: Reflection

**Name:** Pramay Dubey  
**SRN:** PES2UG24CS361  

**1. Which issues were the easiest to fix, and which were the hardest? Why?**

The easiest were the style issues: blank lines (E302/E305), long lines, trailing whitespace, docstrings, snake_case names and the unused variable and imports. They are mechanical and don't change what the program does.

The hardest was the `eval()` in `applyAdjustment`. I couldn't just delete it, because the supervisor formula is a real feature. I had to write a small evaluator using `ast` that only allows `current`, whole numbers and `+ - * //`, and then decide what to do with bad results like division by zero or a negative quantity. The hard-coded password was also harder than it looked: removing it from the code means the program needs another way to get it (an environment variable), and the demo needs to behave sensibly when it isn't set. The MD5 warning took thought rather than effort. Replacing it with SHA-256 would have changed every bin label already printed, so the right fix was to keep MD5 and mark it `usedforsecurity=False`.

**2. Did the static analysis tools report any false positives? If so, describe one example.**

Yes. Bandit's B324 rated MD5 as **High** severity, but here MD5 only produces a 6-character label checksum; it isn't used for passwords or signatures. The finding was technically right but not a real vulnerability in this context. Marking it `usedforsecurity=False` documents that and satisfies the tool. Bandit's B307 on `eval("print('stock audit complete')")` was also not exploitable, because the string is fixed. It was still worth removing since it is a pointless risk.

The opposite also happened: the tools missed the most serious bugs. None of them noticed that issuing 500 units silently deleted WID-001, that negative stock was accepted, or that the integer SKU `404` came back as the string `"404"` after saving and loading. I only found those by running the program and reading the output, as the README suggested.

**3. How would you integrate static analysis tools into your actual software development workflow?**

- Run Pylint and Flake8 in the editor (VS Code extensions) so problems show while typing.
- Add a `pre-commit` hook that runs Flake8 and Bandit, so style and security issues are caught before a commit.
- Add a CI job (e.g. GitHub Actions) that runs all three tools on every push and pull request, failing the build on any Bandit Medium/High finding or a Pylint score below about 9.5.
- Keep shared `.pylintrc` / `.flake8` config files in the repo so the whole team uses the same rules, and suppress a warning only deliberately, with a comment explaining why (as with the MD5 checksum).
- Keep unit tests alongside, since static analysis didn't catch the logic bugs in this program.

**4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?**

- **Security:** The supervisor formula can no longer run arbitrary Python, the password is no longer in the source code, and Bandit reports no issues.
- **Correctness:** Stock can't go negative, over-issuing no longer silently deletes a SKU, unknown SKUs and invalid input are rejected, and SKU types stay consistent after save/load.
- **Robustness:** Files are always closed, a missing or corrupt JSON file no longer crashes the program, and the bare `except` no longer hides errors.
- **Traceability:** Every receipt, issue and rejection is logged, and the audit log now records the old and new quantity for each adjustment.
- **Readability:** PEP 8 names, docstrings, f-strings and consistent layout.
- **Measured:** Pylint went from 4.48/10 to 10.00/10, Flake8 from 19 violations to 0, and Bandit from 5 issues to 0.
