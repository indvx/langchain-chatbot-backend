"""make document employee_id nullable

Revision ID: a1b2c3d4e5f6
Revises: 71831401e14c
Create Date: 2026-10-30 12:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '71831401e14c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('documents', 'employee_id',
               existing_type=sa.Integer(),
               nullable=True)
    try:
        op.drop_index('ix_documents_type', table_name='documents')
        op.create_index(op.f('ix_documents_type'), 'documents', ['type'], unique=False)
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_index('ix_documents_type', table_name='documents')
        op.create_index(op.f('ix_documents_type'), 'documents', ['type'], unique=True)
    except Exception:
        pass
    op.alter_column('documents', 'employee_id',
               existing_type=sa.Integer(),
               nullable=False)
