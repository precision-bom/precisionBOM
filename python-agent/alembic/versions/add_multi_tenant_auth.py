"""add multi-tenant authentication

Revision ID: add_multi_tenant
Revises: 0757229302c7
Create Date: 2026-01-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_multi_tenant'
down_revision: Union[str, Sequence[str], None] = '0757229302c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add multi-tenant support with clients table and client_id on projects/api_keys."""

    # 1. Create clients table
    op.create_table(
        'clients',
        sa.Column('client_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('oidc_issuer', sa.String(length=512), nullable=True),
        sa.Column('oidc_audience', sa.String(length=255), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('client_id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_clients_slug', 'clients', ['slug'], unique=False)
    op.create_index('ix_clients_oidc_issuer', 'clients', ['oidc_issuer'], unique=False)

    # 2. Create default client for existing data migration
    op.execute("""
        INSERT INTO clients (client_id, name, slug, is_active, settings, created_at, updated_at)
        VALUES ('cli_default', 'Default Client', 'default', true, '{}', now(), now())
    """)

    # 3. Add client_id to api_keys (nullable first for migration)
    op.add_column('api_keys', sa.Column('client_id', sa.String(length=64), nullable=True))

    # 4. Update existing API keys to use default client
    op.execute("UPDATE api_keys SET client_id = 'cli_default' WHERE client_id IS NULL")

    # 5. Make client_id non-nullable and add FK
    op.alter_column('api_keys', 'client_id', nullable=False)
    op.create_foreign_key('fk_api_keys_client', 'api_keys', 'clients', ['client_id'], ['client_id'])
    op.create_index('ix_api_keys_client_id', 'api_keys', ['client_id'], unique=False)

    # 6. Add client_id to projects (nullable first for migration)
    op.add_column('projects', sa.Column('client_id', sa.String(length=64), nullable=True))

    # 7. Update existing projects to use default client
    op.execute("UPDATE projects SET client_id = 'cli_default' WHERE client_id IS NULL")

    # 8. Make client_id non-nullable and add FK
    op.alter_column('projects', 'client_id', nullable=False)
    op.create_foreign_key('fk_projects_client', 'projects', 'clients', ['client_id'], ['client_id'])
    op.create_index('ix_projects_client_id', 'projects', ['client_id'], unique=False)


def downgrade() -> None:
    """Remove multi-tenant support."""

    # Remove projects client_id
    op.drop_constraint('fk_projects_client', 'projects', type_='foreignkey')
    op.drop_index('ix_projects_client_id', table_name='projects')
    op.drop_column('projects', 'client_id')

    # Remove api_keys client_id
    op.drop_constraint('fk_api_keys_client', 'api_keys', type_='foreignkey')
    op.drop_index('ix_api_keys_client_id', table_name='api_keys')
    op.drop_column('api_keys', 'client_id')

    # Drop clients table
    op.drop_index('ix_clients_oidc_issuer', table_name='clients')
    op.drop_index('ix_clients_slug', table_name='clients')
    op.drop_table('clients')
