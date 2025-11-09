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
rm -f telegram_config.json

echo "✅ Session files removed"
echo ""
echo "Next steps:"
echo "1. Run: python main.py"
echo "2. Choose option 1 to setup/login"
echo "3. Enter your API credentials from https://my.telegram.org/apps"
echo "   ⚠️  IMPORTANT: Use USER API credentials, NOT bot credentials!"
echo "4. Enter your PERSONAL phone number (e.g., +1234567890)"
echo "5. You'll receive a code via Telegram - enter it"
echo ""
echo "After authentication, you'll be able to add contacts."
