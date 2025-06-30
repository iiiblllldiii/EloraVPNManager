"""Rename mode to config_mode in inbound_config

Revision ID: aa840f3a8058
Revises: 254098d74fbf
Create Date: 2025-06-30 12:39:12.060731

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "aa840f3a8058"
down_revision = "254098d74fbf"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("inbound_config", "mode", new_column_name="config_mode")


def downgrade():
    op.alter_column("inbound_config", "config_mode", new_column_name="mode")
