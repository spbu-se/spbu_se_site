# model-definer

<!-- encoding: utf-8 -->

Define or modify SQLAlchemy models and WTForms following SE Site conventions.

## SQLAlchemy Model Pattern

```python
# SPDX-License-Identifier: MIT

import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ExampleModel(db.Model):
    __tablename__ = "example"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
```

## Conventions

- All models in `se_models.py` (single-file pattern)
- Use `sa.Column()` with explicit types, not TypeDecorator shortcuts
- `nullable=True` is the default — be explicit when setting `nullable=False`
- Foreign keys: `sa.Column(sa.Integer, sa.ForeignKey("table.id"))`
- Relationships: `db.relationship("Model", backref=...)`
- Composite keys: `__table_args__ = (sa.PrimaryKeyConstraint("col1", "col2"),)`
- Auto-increment PK: `sa.Column(sa.Integer, primary_key=True)` (SQLite default)

## WTForms Pattern

```python
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired


class ExampleForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    category = SelectField("Category", coerce=int)
```

- Forms live in `se_forms.py` or domain-specific files (`se_review_forms.py`, `se_internship_forms.py`)
- Use `coerce=int` for SelectField with integer IDs
- Custom validators are functions, not methods
