"""Alter extra column length to 2048

Revision ID: 254098d74fbf
Revises: 57b0e3b6f599
Create Date: 2025-06-28 11:04:47.587795

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "254098d74fbf"
down_revision = "57b0e3b6f599"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "inbound_config",
        "extra",
        existing_type=sa.String(128),
        type_=sa.String(2048),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "inbound_config",
        "extra",
        existing_type=sa.String(2048),
        type_=sa.String(128),
        existing_nullable=True,
    )
