# Fixing the "Bot API" Error

## Problem

You're getting this error:
```
ERROR: Cannot get entity by phone number as a bot
```

This means your Telegram session is authenticated as a **BOT** instead of a regular **USER account**.

Telegram's API has restrictions:
- **Bots cannot** add contacts by phone number
- **Bots cannot** look up users by phone number
- Only **regular user accounts** can add contacts

## Solution

You need to reset your session and re-authenticate with a USER account:

### Step 1: Reset the Session

Run the reset script:
```bash
./reset_session.sh
```

Or manually delete the files:
```bash
rm *.session telegram_config.json
```

### Step 2: Re-authenticate with a USER Account

1. Run the CLI:
   ```bash
   python main.py
   ```

2. Choose option `1` (Setup/Login to Telegram)

3. **IMPORTANT**: Enter **USER API credentials**, not bot credentials:
   - Go to https://my.telegram.org/apps
   - Log in with YOUR personal Telegram account
   - Create a new application (or use existing one)
   - Copy the `api_id` and `api_hash`
   - **Do NOT use a bot token!**

4. Enter your **personal phone number** (e.g., `+254712345678`)

5. You'll receive a verification code via Telegram - enter it

6. If you have 2FA enabled, enter your password

### Step 3: Test

After authentication, the app will now work correctly because you're using a USER account.

## How to Tell if You're Using Bot vs User Credentials

**User Credentials:**
- `api_id`: A number (e.g., `12345678`)
- `api_hash`: A 32-character hex string (e.g., `a1b2c3d4e5f6...`)
- Created at: https://my.telegram.org/apps
- Requires phone verification

**Bot Credentials (DON'T USE THESE):**
- Bot token: Format like `123456789:ABCdefGHIjklMNOpqr...`
- Created with @BotFather
- Starts with numbers followed by a colon

## Verification

After re-authentication, the app will automatically check if you're a bot and reject bot sessions with a clear error message.

You can also run the diagnostic:
```bash
python check_session.py
```

This will show:
```
=== Session Information ===
User ID: 123456789
Name: Your Name
Username: @yourusername
Phone: +254712345678
Is Bot: False
Is User: True

✅ This is a valid USER session
```

If it says `Is Bot: True`, you need to reset and use user credentials instead.
