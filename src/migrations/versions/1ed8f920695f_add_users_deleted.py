# SPDX-License-Identifier: Apache-2.0
"""Add users.deleted flag for soft-deleted accounts.

Revision ID: 1ed8f920695f
Revises: 50699d0a61d4
Create Date: 2026-08-21 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1ed8f920695f"
down_revision = "50699d0a61d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("deleted", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("deleted")
