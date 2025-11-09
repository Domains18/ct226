#!/usr/bin/env python3
"""Diagnostic script to check Telegram session type."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.telegram_client import TelegramContactManager
import json

async def check_session():
    """Check if the session is a user or bot session."""

    # Load config
    try:
        with open("telegram_config.json", 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ No telegram_config.json found")
        return

    api_id = config.get('api_id')
    api_hash = config.get('api_hash')

    if not api_id or not api_hash:
        print("❌ Missing API credentials in config")
        return

    manager = TelegramContactManager(api_id, api_hash)

    try:
        await manager.connect()

        # Get current user info
        me = await manager.client.get_me()

        print("\n=== Session Information ===")
        print(f"User ID: {me.id}")
        print(f"Name: {me.first_name} {me.last_name or ''}")
        print(f"Username: @{me.username or 'N/A'}")
        print(f"Phone: {me.phone or 'N/A'}")
        print(f"Is Bot: {me.bot}")
        print(f"Is User: {not me.bot}")

        if me.bot:
            print("\n⚠️  WARNING: This session is for a BOT, not a regular user!")
            print("You need to authenticate with a regular user account to add contacts.")
            print("\nTo fix this:")
            print("1. Delete the session files: rm *.session telegram_config.json")
            print("2. Re-run the CLI and authenticate with your personal phone number")
            print("3. Make sure you use USER API credentials from https://my.telegram.org/apps")
        else:
            print("\n✅ This is a valid USER session")

        await manager.disconnect()

    except Exception as e:
        print(f"❌ Error checking session: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_session())
