#!/bin/bash
# Reset Telegram session and config

echo "=== Telegram Session Reset ==="
echo ""
echo "This will delete your current session and allow you to re-authenticate."
echo ""
read -p "Are you sure you want to continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Removing session files..."
rm -f *.session
# rm -f telegram_config.json

echo "✅ Session files removed"
