## Test Writing Guidelines

1. Name every test function with a clear and descriptive `test_` prefix.
2. Keep tests independent; no test should rely on the result or side effects of another.
3. Write small, focused tests that validate only one behavior.
4. Prefer a single logical assertion per test when possible.
5. Use fixtures for shared setup/teardown logic instead of duplicating code.
6. Define fixture scopes explicitly (`function`, `module`, `session`) based on lifecycle needs.
7. Use parametrization to test multiple inputs for the same logic.
8. Mark tests with `@pytest.mark` to enable selective execution.
9. Group related tests into classes or modules by feature or domain.
10. Skip tests explicitly when blocked by environment or external constraints.
11. Use `xfail` for known bugs instead of breaking the pipeline.
12. Avoid printing or logging unless debugging; rely on assertions.
13. Keep test logic simpler than production logic.
14. Maintain tests as first-class code that evolves with features.
15. Track coverage and eliminate untested critical paths.
16. Never test implementation details—only observable behavior.
17. Avoid hard-coded sleeps; use proper synchronization or mocks.
18. Do not mock what you don’t own unless strictly necessary.
19. Prefer deterministic inputs over random data.
20. Fail fast: tests should surface errors as early as possible.

## Test Folder Structure Guidelines

21. Keep all tests in a top-level `tests/` directory.
22. Mirror the application structure inside `tests/`.
23. Separate test logic, fixtures, and helpers into subfolders.
24. Store shared fixtures in `tests/fixtures/`.
25. Use a single `tests/conftest.py` for global fixture discovery.
26. Group functional tests under `tests/test_functions/`.
27. Place integration tests in a dedicated folder (e.g. `tests/integration/`).
28. Keep test utilities in `tests/helpers/`.
29. Store test outputs (reports, coverage, XML) in `tests/test_results/`.
30. Never mix production code inside the `tests/` directory.
31. Name test files using `test_*.py` or `*_test.py`.
32. Keep one test module per production module when possible.
33. Avoid deeply nested test folders (max 2–3 levels).
34. Ensure tests can run from project root with a single `pytest` command.
35. Version control the structure, not generated artifacts.