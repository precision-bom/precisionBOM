"""add x402 wallet address to clients

Revision ID: add_x402_wallet
Revises: add_multi_tenant
Create Date: 2026-01-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_x402_wallet'
down_revision: Union[str, Sequence[str], None] = 'add_multi_tenant'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add wallet_address column to clients for x402 payment support."""

    # Add wallet_address column to clients table
    op.add_column(
        'clients',
        sa.Column('wallet_address', sa.String(length=42), nullable=True)
    )

    # Add index for wallet lookups
    op.create_index(
        'ix_clients_wallet_address',
        'clients',
        ['wallet_address'],
        unique=False
    )


def downgrade() -> None:
    """Remove wallet_address column from clients."""

    op.drop_index('ix_clients_wallet_address', table_name='clients')
    op.drop_column('clients', 'wallet_address')
