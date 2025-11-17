"""initial schema with bookings approvals timeline approver_parties

Revision ID: 001
Revises:
Create Date: 2025-01-17 22:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    # Create enums using raw SQL with IF NOT EXISTS (separate statements for asyncpg)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE affiliation_enum AS ENUM ('Ingeborg', 'Cornelia', 'Angelika');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE status_enum AS ENUM ('Pending', 'Denied', 'Confirmed', 'Canceled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE decision_enum AS ENUM ('NoResponse', 'Approved', 'Denied');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$
        """
    )

    # Create Python enum references (without creating the type in DB)
    affiliation_enum = postgresql.ENUM(
        "Ingeborg", "Cornelia", "Angelika", name="affiliation_enum", create_type=False
    )
    status_enum = postgresql.ENUM(
        "Pending", "Denied", "Confirmed", "Canceled", name="status_enum", create_type=False
    )
    decision_enum = postgresql.ENUM(
        "NoResponse", "Approved", "Denied", name="decision_enum", create_type=False
    )

    # Create approver_parties table
    op.create_table(
        "approver_parties",
        sa.Column("party", affiliation_enum, nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("notification_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("party"),
        sa.UniqueConstraint("email"),
    )

    # Seed approver_parties data (BR-003)
    op.execute(
        """
        INSERT INTO approver_parties (party, email, notification_enabled) VALUES
        ('Ingeborg', 'ingeborg@example.com', TRUE),
        ('Cornelia', 'cornelia@example.com', TRUE),
        ('Angelika', 'angelika@example.com', TRUE)
        ON CONFLICT (party) DO NOTHING
        """
    )

    # Create bookings table
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_days", sa.Integer(), nullable=False),
        sa.Column("party_size", sa.Integer(), nullable=False),
        sa.Column("affiliation", affiliation_enum, nullable=False),
        sa.Column("requester_first_name", sa.String(length=40), nullable=False),
        sa.Column("requester_email", sa.String(length=254), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", status_enum, nullable=False, server_default="Pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("end_date >= start_date", name="check_end_after_start"),
        sa.CheckConstraint("party_size >= 1 AND party_size <= 10", name="check_party_size_range"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for bookings
    op.create_index("idx_bookings_status", "bookings", ["status"])
    op.create_index("idx_bookings_requester_email", "bookings", ["requester_email"])
    op.create_index(
        "idx_bookings_last_activity",
        "bookings",
        ["last_activity_at"],
        postgresql_ops={"last_activity_at": "DESC"},
    )
    # GiST index for date range overlap detection (BR-002, BR-029)
    op.execute(
        """
        CREATE INDEX idx_bookings_date_range ON bookings
        USING GIST (daterange(start_date, end_date, '[]'))
        """
    )

    # Create trigger to update updated_at (separate statements for asyncpg)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER update_bookings_updated_at
        BEFORE UPDATE ON bookings
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column()
        """
    )

    # Create approvals table
    op.create_table(
        "approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party", affiliation_enum, nullable=False),
        sa.Column("decision", decision_enum, nullable=False, server_default="NoResponse"),
        sa.Column("comment", sa.String(length=500), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id", "party", name="uq_booking_party"),
    )

    # Create indexes for approvals
    op.create_index("idx_approvals_booking", "approvals", ["booking_id"])
    op.create_index("idx_approvals_decision", "approvals", ["decision"])
    op.create_index("idx_approvals_party_decision", "approvals", ["party", "decision"])

    # Create timeline_events table
    op.create_table(
        "timeline_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("when", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("actor", sa.String(length=50), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for timeline_events
    op.create_index("idx_timeline_booking", "timeline_events", ["booking_id"])
    op.create_index(
        "idx_timeline_when",
        "timeline_events",
        ["when"],
        postgresql_ops={"when": "DESC"},
    )


def downgrade() -> None:
    """Drop all tables and enums."""
    op.drop_index("idx_timeline_when", table_name="timeline_events")
    op.drop_index("idx_timeline_booking", table_name="timeline_events")
    op.drop_table("timeline_events")

    op.drop_index("idx_approvals_party_decision", table_name="approvals")
    op.drop_index("idx_approvals_decision", table_name="approvals")
    op.drop_index("idx_approvals_booking", table_name="approvals")
    op.drop_table("approvals")

    op.execute("DROP TRIGGER IF EXISTS update_bookings_updated_at ON bookings")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    op.drop_index("idx_bookings_date_range", table_name="bookings")
    op.drop_index("idx_bookings_last_activity", table_name="bookings")
    op.drop_index("idx_bookings_requester_email", table_name="bookings")
    op.drop_index("idx_bookings_status", table_name="bookings")
    op.drop_table("bookings")

    op.drop_table("approver_parties")

    op.execute("DROP TYPE IF EXISTS decision_enum")
    op.execute("DROP TYPE IF EXISTS status_enum")
    op.execute("DROP TYPE IF EXISTS affiliation_enum")
