# test-writer

Write hermetic pytest tests with coverage, mocking, and tempfile fixtures.

**Load this skill at the start of every implementation task, before writing any implementation code.**

## Patterns

- All tests are hermetic — no network calls, no real API
- Mock `requests.Response` with `Mock(spec=requests.Response)`
- CLI tests use `capsys` fixture
- Temp files: `NamedTemporaryFile(mode="w", ...)` + `path.unlink(missing_ok=True)` in `finally`
- Parametrize with `@pytest.mark.parametrize`
- Group tests in classes: `TestFoo`, `TestFooAdditional`
