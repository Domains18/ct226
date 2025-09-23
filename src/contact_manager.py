"""Contact management utilities and operations."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .phone_parser import PhoneNumber, parse_phone_file
from .telegram_client import TelegramContactManager


@dataclass
class ContactOperation:
    """Represents a contact operation result."""
    phone: PhoneNumber
    success: bool
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ContactManager:
    """High-level contact management operations."""
    
    def __init__(self, telegram_manager: TelegramContactManager):
        """Initialize with Telegram manager."""
        self.telegram_manager = telegram_manager
        self.logger = logging.getLogger(__name__)
        self.operations_log: List[ContactOperation] = []
    
    async def import_from_file(self, file_path: str, 
                             skip_existing: bool = True,
                             batch_size: int = 50,
                             name_prefix: str = "Contact") -> Dict[str, Any]:
        """Import contacts from a file."""
        
        # Parse phone numbers from file
        self.logger.info(f"Parsing phone numbers from {file_path}")
        try:
            phone_numbers, stats = parse_phone_file(file_path)
        except Exception as e:
            self.logger.error(f"Failed to parse file: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': {}
            }
        
        self.logger.info(f"Parsed {stats['total']} numbers, {stats['valid']} valid")
        
        # Filter valid numbers
        valid_numbers = [p for p in phone_numbers if p.is_valid]
        
        if not valid_numbers:
            return {
                'success': False,
                'error': 'No valid phone numbers found',
                'stats': stats
            }
        
        # Check for existing contacts if requested
        if skip_existing:
            self.logger.info("Checking for existing contacts...")
            existing = await self.telegram_manager.get_existing_contacts()
            valid_numbers = [p for p in valid_numbers if p.formatted not in existing]
            self.logger.info(f"Filtered to {len(valid_numbers)} new contacts")
        
        if not valid_numbers:
            return {
                'success': True,
                'message': 'All contacts already exist',
                'stats': stats,
                'operations': []
            }
        
        # Import contacts in batches
        self.logger.info(f"Importing {len(valid_numbers)} contacts in batches of {batch_size}")
        
        total_successful = 0
        total_failed = 0
        all_errors = []
        
        for i in range(0, len(valid_numbers), batch_size):
            batch = valid_numbers[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(valid_numbers) + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} contacts)")
            
            try:
                batch_result = await self._process_batch(batch, name_prefix)
                total_successful += batch_result['successful']
                total_failed += batch_result['failed']
                all_errors.extend(batch_result['errors'])
                
                # Log individual operations
                for phone in batch:
                    success = phone.formatted in [c.phone for c in batch_result.get('imported_contacts', [])]
                    operation = ContactOperation(
                        phone=phone,
                        success=success,
                        error_message=None if success else "Import failed"
                    )
                    self.operations_log.append(operation)
                
                # Small delay between batches
                if i + batch_size < len(valid_numbers):
                    await asyncio.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Batch {batch_num} failed: {e}")
                total_failed += len(batch)
                all_errors.append(f"Batch {batch_num}: {str(e)}")
                
                # Log failed operations
                for phone in batch:
                    operation = ContactOperation(
                        phone=phone,
                        success=False,
                        error_message=str(e)
                    )
                    self.operations_log.append(operation)
        
        return {
            'success': total_successful > 0,
            'stats': {
                **stats,
                'attempted': len(valid_numbers),
                'successful': total_successful,
                'failed': total_failed,
                'success_rate': (total_successful / len(valid_numbers) * 100) if valid_numbers else 0
            },
            'errors': all_errors,
            'operations': self.operations_log[-len(valid_numbers):]  # Recent operations
        }
    
    async def _process_batch(self, batch: List[PhoneNumber], name_prefix: str) -> Dict[str, Any]:
        """Process a batch of contacts."""
        # Prepare contacts with names
        contacts_with_names = []
        for i, phone in enumerate(batch):
            # Generate a name based on the phone number
            name = f"{name_prefix} {phone.formatted[-4:]}"
            contacts_with_names.append((phone, name))
        
        # Use the bulk import method
        result = await self.telegram_manager.add_contacts_bulk(batch)
        return result
    
    async def add_single_contact(self, phone_str: str, 
                               first_name: Optional[str] = None, 
                               last_name: str = "") -> ContactOperation:
        """Add a single contact."""
        # Parse the phone number
        from .phone_parser import PhoneParser
        parser = PhoneParser()
        phone = parser.parse_number(phone_str)
        
        if not phone.is_valid:
            operation = ContactOperation(
                phone=phone,
                success=False,
                error_message=phone.error_message or "Invalid phone number"
            )
            self.operations_log.append(operation)
            return operation
        
        try:
            success = await self.telegram_manager.add_single_contact(phone, first_name or f"Contact {phone.formatted[-4:]}", last_name)
            operation = ContactOperation(
                phone=phone,
                success=success,
                error_message=None if success else "Failed to add contact"
            )
            self.operations_log.append(operation)
            return operation
            
        except Exception as e:
            operation = ContactOperation(
                phone=phone,
                success=False,
                error_message=str(e)
            )
            self.operations_log.append(operation)
            return operation
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get summary of all operations performed."""
        if not self.operations_log:
            return {
                'total_operations': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0
            }
        
        total = len(self.operations_log)
        successful = sum(1 for op in self.operations_log if op.success)
        failed = total - successful
        
        return {
            'total_operations': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'latest_operations': self.operations_log[-10:]  # Last 10 operations
        }
    
    def save_operations_log(self, file_path: str):
        """Save operations log to a file."""
        import json
        
        log_data = []
        for op in self.operations_log:
            log_data.append({
                'phone_raw': op.phone.raw,
                'phone_formatted': op.phone.formatted,
                'success': op.success,
                'error_message': op.error_message,
                'timestamp': op.timestamp.isoformat() if op.timestamp else datetime.now().isoformat()
            })
        
        with open(file_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.logger.info(f"Operations log saved to {file_path}")


async def create_contact_manager(api_id: str, api_hash: str, phone_number: Optional[str] = None) -> Optional[ContactManager]:
    """Create and authenticate a contact manager."""
    
    # Try to load existing session first
    telegram_manager = TelegramContactManager.load_session_info()
    
    if not telegram_manager:
        if not api_id or not api_hash:
            return None
        telegram_manager = TelegramContactManager(api_id, api_hash)
    
    # Connect and authenticate
    try:
        await telegram_manager.connect()
        
        # If not authenticated and phone number provided, authenticate
        if not await telegram_manager.client.is_user_authorized() and phone_number:
            success = await telegram_manager.login_with_phone(phone_number)
            if not success:
                await telegram_manager.disconnect()
                return None
        
        return ContactManager(telegram_manager)
        
    except Exception as e:
        logging.error(f"Failed to create contact manager: {e}")
        return None