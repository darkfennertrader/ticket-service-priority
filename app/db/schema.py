from sqlalchemy import MetaData, Table, Column, String, Text, DateTime

metadata = MetaData()

tickets = Table(
    "tickets",
    metadata,
    Column("id", String, primary_key=True),
    Column("title", String(255), nullable=False),
    Column("description", Text, nullable=False),
    Column("priority", String(10), nullable=False),
    Column("status", String(15), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)
