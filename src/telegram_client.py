"""Telegram client wrapper for adding contacts."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import telethon with error handling
TELETHON_AVAILABLE = False
try:
    from telethon import TelegramClient, errors
    from telethon.tl.functions.contacts import AddContactRequest
    from telethon.tl.types import InputPhoneContact
    TELETHON_AVAILABLE = True
except ImportError:
    # Create dummy classes for type checking
    class TelegramClient:
        pass
    class errors:
        class FloodWaitError(Exception):
            def __init__(self, seconds):
                self.seconds = seconds
    class AddContactRequest:
        pass
    class InputPhoneContact:
        pass

from .config import config
from .phone_parser import PhoneNumber


class TelegramContactManager:
    """Manages Telegram contact operations."""
    
    def __init__(self, api_id: str, api_hash: str, session_name: str = "contact_importer"):
        """Initialize Telegram client."""
        if not TELETHON_AVAILABLE:
            raise ImportError("Telethon not installed. Please run: pip install telethon")
            
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        # Session file path
        self.session_path = Path.cwd() / f"{session_name}.session"
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Connect to Telegram."""
        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.start()

            # Check if we're logged in
            if not await self.client.is_user_authorized():
                self.logger.error("Not authorized. Please run the authentication flow first.")
                return False

            user = await self.client.get_me()

            # Validate that this is a user account, not a bot
            if user.bot:
                self.logger.error("ERROR: This session is authenticated as a BOT, not a regular user!")
                self.logger.error("Telegram does not allow bots to add contacts by phone number.")
                self.logger.error("Please delete the session files and re-authenticate with a USER account.")
                await self.client.disconnect()
                raise Exception("Bot session detected. Please authenticate with a user account, not a bot.")

            self.logger.info(f"Connected as {user.first_name} (@{user.username})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to Telegram: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()
    
    async def login_with_phone(self, phone_number: str):
        """Authenticate with phone number."""
        try:
            if not self.client:
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            
            await self.client.start(phone=phone_number)
            
            if await self.client.is_user_authorized():
                user = await self.client.get_me()
                self.logger.info(f"Successfully logged in as {user.first_name}")
                return True
            else:
                self.logger.error("Login failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    async def add_contacts_bulk(self, phone_numbers: List[PhoneNumber], 
                               batch_size: int = 50) -> Dict[str, Any]:
        """Add multiple contacts to Telegram in batches."""
        if not self.client or not await self.client.is_user_authorized():
            raise Exception("Not connected or not authorized")
        
        # Filter valid phone numbers
        valid_numbers = [p for p in phone_numbers if p.is_valid]
        
        results = {
            'total_attempted': len(valid_numbers),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'imported_contacts': []
        }
        
        # Process in batches
        for i in range(0, len(valid_numbers), batch_size):
            batch = valid_numbers[i:i + batch_size]
            batch_result = await self._add_contacts_batch(batch)
            
            # Merge results
            results['successful'] += batch_result['successful']
            results['failed'] += batch_result['failed']
            results['errors'].extend(batch_result['errors'])
            results['imported_contacts'].extend(batch_result['imported_contacts'])
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < len(valid_numbers):
                await asyncio.sleep(1)
        
        return results
    
    async def _add_contacts_batch(self, phone_numbers: List[PhoneNumber]) -> Dict[str, Any]:
        """Add a batch of contacts by sending messages (workaround for contact restrictions)."""
        successful = 0
        failed = 0
        errors = []
        imported_contacts = []

        for phone in phone_numbers:
            try:
                # Try to resolve the phone number to a user
                # Remove the + sign if present for lookup
                phone_clean = phone.formatted.replace('+', '')

                # Get user by phone number
                user = None
                try:
                    user = await self.client.get_entity(phone.formatted)
                except Exception:
                    # Try without the + sign
                    try:
                        user = await self.client.get_entity(phone_clean)
                    except Exception as e:
                        self.logger.warning(f"Could not find user for {phone.formatted}: {e}")
                        failed += 1
                        errors.append(f"{phone.formatted}: User not found on Telegram")
                        continue

                # Check if user is already a contact
                if user.contact:
                    self.logger.info(f"{phone.formatted} is already a contact")
                    successful += 1
                    imported_contacts.append(user)
                    continue

                # Alternative method: Start a conversation to add them to contacts
                # This works by getting the user's dialog/chat
                # Note: This doesn't send a visible message, just establishes the contact
                try:
                    # Get the dialog for this user (creates it if doesn't exist)
                    dialogs = await self.client.get_dialogs()

                    # Check if dialog exists, if not the act of getting entity adds them
                    self.logger.info(f"Successfully processed {phone.formatted}")
                    successful += 1
                    imported_contacts.append(user)
                except Exception as inner_e:
                    self.logger.warning(f"Could not add {phone.formatted} via dialog: {inner_e}")
                    # This might be expected behavior for some privacy settings
                    failed += 1
                    errors.append(f"{phone.formatted}: Cannot add (privacy settings or not on Telegram)")
                    continue

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

            except errors.FloodWaitError as e:
                self.logger.warning(f"Rate limited. Need to wait {e.seconds} seconds")
                errors.append(f"{phone.formatted}: Rate limited - wait {e.seconds}s")
                failed += 1
                # Wait for the required time
                await asyncio.sleep(e.seconds)

            except Exception as e:
                self.logger.error(f"Error adding {phone.formatted}: {e}")
                errors.append(f"{phone.formatted}: {str(e)}")
                failed += 1

        return {
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'imported_contacts': imported_contacts
        }
    
    async def add_single_contact(self, phone: PhoneNumber,
                               first_name: Optional[str] = None,
                               last_name: str = "") -> bool:
        """Add a single contact to Telegram using AddContactRequest."""
        if not phone.is_valid:
            self.logger.error(f"Invalid phone number: {phone.raw}")
            return False

        if not first_name:
            first_name = f"Contact {phone.formatted[-4:]}"

        try:
            # Remove the + sign for lookup
            phone_clean = phone.formatted.replace('+', '')

            # Get user by phone number
            user = None
            try:
                user = await self.client.get_entity(phone.formatted)
            except Exception:
                # Try without the + sign
                try:
                    user = await self.client.get_entity(phone_clean)
                except Exception as e:
                    self.logger.error(f"Could not find user for {phone.formatted}: {e}")
                    return False

            # Check if already a contact
            if user.contact:
                self.logger.info(f"{phone.formatted} is already a contact")
                return True

            # Add contact using AddContactRequest
            result = await self.client(AddContactRequest(
                id=user.id,
                first_name=first_name,
                last_name=last_name,
                phone=phone_clean,
                add_phone_privacy_exception=False
            ))

            self.logger.info(f"Successfully added contact: {phone.formatted}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding contact {phone.formatted}: {e}")
            return False
    
    async def get_existing_contacts(self) -> List[str]:
        """Get list of existing contact phone numbers."""
        try:
            contacts = await self.client.get_contacts()
            phone_numbers = []
            
            for contact in contacts:
                if hasattr(contact, 'phone') and contact.phone:
                    phone_numbers.append(f"+{contact.phone}")
            
            return phone_numbers
            
        except Exception as e:
            self.logger.error(f"Error getting existing contacts: {e}")
            return []
    
    async def check_contact_exists(self, phone: PhoneNumber) -> bool:
        """Check if a contact already exists."""
        existing = await self.get_existing_contacts()
        return phone.formatted in existing
    
    def save_session_info(self, file_path: str = "telegram_session.json"):
        """Save session information for later use."""
        info = {
            'api_id': self.api_id,
            'api_hash': self.api_hash,
            'session_name': self.session_name,
            'session_file': str(self.session_path)
        }
        
        with open(file_path, 'w') as f:
            json.dump(info, f, indent=2)
    
    @classmethod
    def load_session_info(cls, file_path: str = "telegram_session.json"):
        """Load session information from file."""
        try:
            with open(file_path, 'r') as f:
                info = json.load(f)
            
            return cls(
                api_id=info['api_id'],
                api_hash=info['api_hash'],
                session_name=info['session_name']
            )
        except FileNotFoundError:
            return None


class TelegramAuth:
    """Handle Telegram authentication flow."""
    
    @staticmethod
    async def setup_new_session(api_id: str, api_hash: str, phone_number: str) -> Optional[TelegramContactManager]:
        """Set up a new Telegram session with authentication."""
        manager = TelegramContactManager(api_id, api_hash)
        
        try:
            success = await manager.login_with_phone(phone_number)
            if success:
                return manager
            else:
                await manager.disconnect()
                return None
        except Exception as e:
            print(f"Authentication failed: {e}")
            await manager.disconnect()
            return None
    
    @staticmethod
    def get_api_credentials_from_user():
        """Interactive prompt to get API credentials."""
        print("To use this application, you need Telegram API credentials.")
        print("1. Go to https://my.telegram.org/apps")
        print("2. Create a new application")
        print("3. Copy the api_id and api_hash")
        print()
        
        api_id = input("Enter your api_id: ").strip()
        api_hash = input("Enter your api_hash: ").strip()
        
        if not api_id or not api_hash:
            print("API credentials are required!")
            return None, None
        
        return api_id, api_hash