#!/usr/bin/env python3

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def create_sample_data():
    engine = create_async_engine("postgresql+asyncpg://opendealz:password@postgres:5432/opendealz", echo=True)

    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO users (email, password_hash, full_name, role, is_verified, is_active) VALUES
            ('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeFBAWd0QoJcZp5G2', 'Admin User', 'admin', true, true),
            ('customer@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeFBAWd0QoJcZp5G2', 'Customer User', 'customer', true, true),
            ('executor@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeFBAWd0QoJcZp5G2', 'Executor User', 'executor', true, true);
        """))
        print("Sample data inserted")

if __name__ == "__main__":
    asyncio.run(create_sample_data())