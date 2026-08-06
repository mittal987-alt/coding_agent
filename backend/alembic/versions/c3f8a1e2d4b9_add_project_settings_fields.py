"""add github_token system_prompt description default_branch to projects

Revision ID: c3f8a1e2d4b9
Revises: 5eea438582e4
Create Date: 2026-08-05 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f8a1e2d4b9'
down_revision: Union[str, Sequence[str], None] = '5eea438582e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('description', sa.String(2000), nullable=True))
    op.add_column('projects', sa.Column('github_token', sa.String(500), nullable=True))
    op.add_column('projects', sa.Column('system_prompt', sa.String(5000), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'system_prompt')
    op.drop_column('projects', 'github_token')
    op.drop_column('projects', 'description')
