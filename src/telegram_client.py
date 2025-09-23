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
    from telethon.tl.functions.contacts import ImportContactsRequest
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
    class ImportContactsRequest:
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
        """Add a batch of contacts."""
        contacts = []
        
        for i, phone in enumerate(phone_numbers):
            # Create contact with phone number as first name
            contact = InputPhoneContact(
                client_id=i,  # Unique ID for this import
                phone=phone.formatted,
                first_name=f"Contact {phone.formatted[-4:]}",  # Use last 4 digits
                last_name=""
            )
            contacts.append(contact)
        
        try:
            # Import contacts
            result = await self.client(ImportContactsRequest(contacts))
            
            return {
                'successful': len(result.imported),
                'failed': len(contacts) - len(result.imported),
                'errors': [],
                'imported_contacts': result.imported
            }
            
        except errors.FloodWaitError as e:
            self.logger.warning(f"Rate limited. Need to wait {e.seconds} seconds")
            return {
                'successful': 0,
                'failed': len(contacts),
                'errors': [f"Rate limited: wait {e.seconds} seconds"],
                'imported_contacts': []
            }
            
        except Exception as e:
            self.logger.error(f"Error importing batch: {e}")
            return {
                'successful': 0,
                'failed': len(contacts),
                'errors': [str(e)],
                'imported_contacts': []
            }
    
    async def add_single_contact(self, phone: PhoneNumber, 
                               first_name: Optional[str] = None, 
                               last_name: str = "") -> bool:
        """Add a single contact to Telegram."""
        if not phone.is_valid:
            self.logger.error(f"Invalid phone number: {phone.raw}")
            return False
        
        if not first_name:
            first_name = f"Contact {phone.formatted[-4:]}"
        
        contact = InputPhoneContact(
            client_id=0,
            phone=phone.formatted,
            first_name=first_name,
            last_name=last_name
        )
        
        try:
            result = await self.client(ImportContactsRequest([contact]))
            
            if result.imported:
                self.logger.info(f"Successfully added contact: {phone.formatted}")
                return True
            else:
                self.logger.warning(f"Failed to add contact: {phone.formatted}")
                return False
                
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