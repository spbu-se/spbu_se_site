# model-definer

Define or modify Pydantic v2 models.

## Conventions

- `from __future__ import annotations`
- `str | None` — never `Optional`
- `field_validator` (v2 style)
- `model_dump(mode="json", exclude_none=True)`
