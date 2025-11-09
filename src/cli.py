"""Interactive CLI for Telegram contact importer."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import click
    from colorama import Fore, Style
    from colorama import init as colorama_init
    from tqdm import tqdm
except ImportError:
    print("Required packages not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)

from .config import config
from .contact_manager import ContactManager, create_contact_manager
from .phone_parser import parse_phone_file
from .telegram_client import TelegramAuth, TelegramContactManager

# Initialize colorama for cross-platform colored output
colorama_init()


class ContactImporterCLI:
    """Interactive CLI for the contact importer."""
    
    def __init__(self):
        self.setup_logging()
        self.contact_manager: Optional[ContactManager] = None
        self.config_file = "telegram_config.json"
        self.session_data = self.load_session_data()
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_config = config.get_logging()
        level = getattr(logging, log_config.get('level', 'INFO'))
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('log_file', 'contact_importer.log')),
                logging.StreamHandler() if log_config.get('console_output', True) else logging.NullHandler()
            ]
        )
    
    def load_session_data(self) -> dict:
        """Load saved session data."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def save_session_data(self, data: dict):
        """Save session data."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not save session data: {e}{Style.RESET_ALL}")
    
    def print_header(self):
        """Print application header."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}  📱 Telegram Contact Importer CLI")
        print(f"{Fore.CYAN}  Bulk import phone numbers to your Telegram account")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    def print_menu(self):
        """Print main menu."""
        print(f"{Fore.GREEN}📋 Main Menu:{Style.RESET_ALL}")
        print("1. 🔐 Setup/Login to Telegram")
        print("2. 📄 Preview phone numbers from file")
        print("3. 📲 Import contacts from file")
        print("4. ➕ Add single contact")
        print("5. 📊 View import statistics")
        print("6. ⚙️  Configuration")
        print("7. 🚪 Exit")
        print()
    
    async def setup_telegram_auth(self):
        """Setup Telegram authentication."""
        print(f"{Fore.YELLOW}🔐 Telegram Authentication Setup{Style.RESET_ALL}")
        print()
        
        # Check if we have saved credentials
        if self.session_data.get('api_id') and self.session_data.get('api_hash'):
            use_saved = input(f"Use saved API credentials? (y/n): ").strip().lower()
            if use_saved == 'y':
                api_id = self.session_data['api_id']
                api_hash = self.session_data['api_hash']
            else:
                api_id, api_hash = TelegramAuth.get_api_credentials_from_user()
        else:
            api_id, api_hash = TelegramAuth.get_api_credentials_from_user()
        
        if not api_id or not api_hash:
            print(f"{Fore.RED}❌ API credentials are required!{Style.RESET_ALL}")
            return False
        
        # Get phone number
        phone_number = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
        if not phone_number:
            print(f"{Fore.RED}❌ Phone number is required!{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.YELLOW}Connecting to Telegram...{Style.RESET_ALL}")
        
        try:
            # Create contact manager with authentication
            self.contact_manager = await create_contact_manager(api_id, api_hash, phone_number)
            
            if self.contact_manager:
                print(f"{Fore.GREEN}✅ Successfully connected to Telegram!{Style.RESET_ALL}")
                
                # Save credentials for future use
                self.session_data.update({
                    'api_id': api_id,
                    'api_hash': api_hash,
                    'phone_number': phone_number
                })
                self.save_session_data(self.session_data)
                
                return True
            else:
                print(f"{Fore.RED}❌ Failed to connect to Telegram{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Authentication failed: {e}{Style.RESET_ALL}")
            return False
    
    def get_data_files(self) -> list:
        """Get all .txt files from the data directory."""
        data_dir = Path(__file__).parent.parent / "data"
        if data_dir.exists():
            return sorted([str(f) for f in data_dir.glob("*.txt")])
        return []

    def preview_phone_numbers(self):
        """Preview phone numbers from file."""
        print(f"{Fore.YELLOW}📄 Preview Phone Numbers{Style.RESET_ALL}")
        print()

        # Get available files from data directory
        data_files = self.get_data_files()

        if data_files:
            print(f"{Fore.GREEN}Available files in data directory:{Style.RESET_ALL}")
            for i, file_path in enumerate(data_files, 1):
                print(f"  {i}. {Path(file_path).name}")
            print()

            file_choice = input(f"Enter file number (1-{len(data_files)}) or custom path: ").strip()

            # Check if user entered a number
            try:
                choice_num = int(file_choice)
                if 1 <= choice_num <= len(data_files):
                    file_path = data_files[choice_num - 1]
                else:
                    print(f"{Fore.YELLOW}Invalid number, using first file{Style.RESET_ALL}")
                    file_path = data_files[0]
            except ValueError:
                # User entered a custom path
                file_path = file_choice if file_choice else data_files[0]
        else:
            # Fallback to manual entry
            default_file = "data/HGCS12.txt"
            file_path = input(f"Enter file path (default: {default_file}): ").strip()
            if not file_path:
                file_path = default_file
        
        if not os.path.exists(file_path):
            print(f"{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
            return
        
        try:
            print(f"{Fore.YELLOW}Parsing phone numbers...{Style.RESET_ALL}")
            phone_numbers, stats = parse_phone_file(file_path)
            
            # Display statistics
            print(f"\n{Fore.GREEN}📊 File Statistics:{Style.RESET_ALL}")
            print(f"Total numbers found: {stats['total']}")
            print(f"Valid numbers: {stats['valid']}")
            print(f"Invalid numbers: {stats['invalid']}")
            print(f"Success rate: {stats['success_rate']:.1f}%")
            
            if stats['country_codes']:
                print(f"\nCountry codes detected:")
                for code, count in stats['country_codes'].items():
                    print(f"  {code}: {count} numbers")
            
            # Show sample numbers
            valid_numbers = [p for p in phone_numbers if p.is_valid]
            if valid_numbers:
                print(f"\n{Fore.GREEN}✅ Sample valid numbers:{Style.RESET_ALL}")
                for i, phone in enumerate(valid_numbers[:5]):
                    print(f"  {i+1}. {phone.raw} → {phone.formatted}")
                
                if len(valid_numbers) > 5:
                    print(f"  ... and {len(valid_numbers) - 5} more")
            
            # Show invalid numbers if any
            invalid_numbers = [p for p in phone_numbers if not p.is_valid]
            if invalid_numbers:
                print(f"\n{Fore.YELLOW}⚠️  Sample invalid numbers:{Style.RESET_ALL}")
                for i, phone in enumerate(invalid_numbers[:3]):
                    print(f"  {i+1}. {phone.raw} - {phone.error_message}")
                
                if len(invalid_numbers) > 3:
                    print(f"  ... and {len(invalid_numbers) - 3} more")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Error parsing file: {e}{Style.RESET_ALL}")
    
    async def import_contacts_from_file(self, auto_file_path: Optional[str] = None):
        """Import contacts from file."""
        if not self.contact_manager:
            print(f"{Fore.RED}❌ Please setup Telegram authentication first!{Style.RESET_ALL}")
            return

        print(f"{Fore.YELLOW}📲 Import Contacts from File{Style.RESET_ALL}")
        print()

        # Use auto file path if provided
        if auto_file_path:
            file_path = auto_file_path
            print(f"{Fore.GREEN}Auto-importing from: {file_path}{Style.RESET_ALL}")
        else:
            # Get available files from data directory
            data_files = self.get_data_files()

            if data_files:
                print(f"{Fore.GREEN}Available files in data directory:{Style.RESET_ALL}")
                for i, file_path in enumerate(data_files, 1):
                    print(f"  {i}. {Path(file_path).name}")
                print()

                file_choice = input(f"Enter file number (1-{len(data_files)}) or custom path: ").strip()

                # Check if user entered a number
                try:
                    choice_num = int(file_choice)
                    if 1 <= choice_num <= len(data_files):
                        file_path = data_files[choice_num - 1]
                    else:
                        print(f"{Fore.YELLOW}Invalid number, using first file{Style.RESET_ALL}")
                        file_path = data_files[0]
                except ValueError:
                    # User entered a custom path
                    file_path = file_choice if file_choice else data_files[0]
            else:
                # Fallback to manual entry
                default_file = "data/HGCS12.txt"
                file_path = input(f"Enter file path (default: {default_file}): ").strip()
                if not file_path:
                    file_path = default_file
        
        if not os.path.exists(file_path):
            print(f"{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
            return
        
        # Get import options
        skip_existing = input("Skip existing contacts? (y/n, default: y): ").strip().lower()
        skip_existing = skip_existing != 'n'
        
        batch_size = input("Batch size (default: 50): ").strip()
        try:
            batch_size = int(batch_size) if batch_size else 50
        except ValueError:
            batch_size = 50
        
        name_prefix = input("Contact name prefix (default: 'Contact'): ").strip()
        if not name_prefix:
            name_prefix = "Contact"
        
        # Confirm import
        print(f"\n{Fore.YELLOW}Import Settings:{Style.RESET_ALL}")
        print(f"File: {file_path}")
        print(f"Skip existing: {skip_existing}")
        print(f"Batch size: {batch_size}")
        print(f"Name prefix: {name_prefix}")
        
        confirm = input(f"\nProceed with import? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Import cancelled.")
            return
        
        try:
            print(f"\n{Fore.YELLOW}Starting import...{Style.RESET_ALL}")
            
            with tqdm(desc="Importing contacts", unit="contact") as pbar:
                result = await self.contact_manager.import_from_file(
                    file_path=file_path,
                    skip_existing=skip_existing,
                    batch_size=batch_size,
                    name_prefix=name_prefix
                )
                pbar.update(result['stats'].get('attempted', 0))
            
            # Display results
            if result['success']:
                stats = result['stats']
                print(f"\n{Fore.GREEN}✅ Import completed!{Style.RESET_ALL}")
                print(f"Attempted: {stats.get('attempted', 0)}")
                print(f"Successful: {stats.get('successful', 0)}")
                print(f"Failed: {stats.get('failed', 0)}")
                print(f"Success rate: {stats.get('success_rate', 0):.1f}%")
                
                if result.get('errors'):
                    print(f"\n{Fore.YELLOW}Errors encountered:{Style.RESET_ALL}")
                    for error in result['errors'][:5]:
                        print(f"  • {error}")
                    if len(result['errors']) > 5:
                        print(f"  ... and {len(result['errors']) - 5} more")
            else:
                print(f"\n{Fore.RED}❌ Import failed: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Import error: {e}{Style.RESET_ALL}")
    
    async def add_single_contact(self):
        """Add a single contact."""
        if not self.contact_manager:
            print(f"{Fore.RED}❌ Please setup Telegram authentication first!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}➕ Add Single Contact{Style.RESET_ALL}")
        print()
        
        phone_number = input("Enter phone number: ").strip()
        if not phone_number:
            print(f"{Fore.RED}❌ Phone number is required!{Style.RESET_ALL}")
            return
        
        first_name = input("Enter first name (optional): ").strip()
        last_name = input("Enter last name (optional): ").strip()
        
        try:
            print(f"{Fore.YELLOW}Adding contact...{Style.RESET_ALL}")
            operation = await self.contact_manager.add_single_contact(
                phone_str=phone_number,
                first_name=first_name or None,
                last_name=last_name
            )
            
            if operation.success:
                print(f"{Fore.GREEN}✅ Contact added successfully!{Style.RESET_ALL}")
                print(f"Phone: {operation.phone.formatted}")
            else:
                print(f"{Fore.RED}❌ Failed to add contact: {operation.error_message}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Error adding contact: {e}{Style.RESET_ALL}")
    
    def view_statistics(self):
        """View import statistics."""
        if not self.contact_manager:
            print(f"{Fore.RED}❌ Please setup Telegram authentication first!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}📊 Import Statistics{Style.RESET_ALL}")
        print()
        
        summary = self.contact_manager.get_operation_summary()
        
        print(f"Total operations: {summary['total_operations']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        
        if summary['latest_operations']:
            print(f"\n{Fore.GREEN}Recent operations:{Style.RESET_ALL}")
            for i, op in enumerate(summary['latest_operations'][-5:], 1):
                status = "✅" if op.success else "❌"
                print(f"  {i}. {status} {op.phone.formatted} - {op.timestamp.strftime('%H:%M:%S')}")
    
    def show_configuration(self):
        """Show current configuration."""
        print(f"{Fore.YELLOW}⚙️  Configuration{Style.RESET_ALL}")
        print()
        
        print("Current settings:")
        print(f"Default country: {config.get('defaults.country_code', 'Not set')}")
        print(f"Batch size: 50 (configurable per import)")
        print(f"Skip existing: Yes (configurable per import)")
        
        print(f"\nSession files:")
        if os.path.exists(self.config_file):
            print(f"✅ Config: {self.config_file}")
        else:
            print(f"❌ Config: {self.config_file} (not found)")
        
        session_files = list(Path.cwd().glob("*.session"))
        if session_files:
            print(f"✅ Session: {session_files[0]}")
        else:
            print(f"❌ Session: No session files found")
    
    async def run(self):
        """Run the interactive CLI."""
        self.print_header()

        # Try to reconnect if we have session data
        auto_import_attempted = False
        if self.session_data.get('api_id') and self.session_data.get('api_hash'):
            try:
                print(f"{Fore.YELLOW}Attempting to reconnect...{Style.RESET_ALL}")
                self.contact_manager = await create_contact_manager(
                    self.session_data['api_id'],
                    self.session_data['api_hash']
                )
                if self.contact_manager:
                    print(f"{Fore.GREEN}✅ Reconnected to Telegram!{Style.RESET_ALL}")

                    # Check for data files and offer auto-import
                    data_files = self.get_data_files()
                    if data_files:
                        print(f"\n{Fore.CYAN}Found {len(data_files)} file(s) in data directory:{Style.RESET_ALL}")
                        for i, file_path in enumerate(data_files, 1):
                            print(f"  {i}. {Path(file_path).name}")

                        auto_import = input(f"\n{Fore.CYAN}Auto-import contacts now? (y/n): {Style.RESET_ALL}").strip().lower()
                        if auto_import == 'y':
                            auto_import_attempted = True
                            # If multiple files, ask which one
                            if len(data_files) == 1:
                                selected_file = data_files[0]
                            else:
                                file_choice = input(f"Enter file number (1-{len(data_files)}): ").strip()
                                try:
                                    choice_num = int(file_choice)
                                    if 1 <= choice_num <= len(data_files):
                                        selected_file = data_files[choice_num - 1]
                                    else:
                                        selected_file = data_files[0]
                                except ValueError:
                                    selected_file = data_files[0]

                            # Start auto-import with the selected file
                            await self.import_contacts_from_file(auto_file_path=selected_file)
                            input(f"\n{Fore.CYAN}Press Enter to continue to main menu...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️  Could not reconnect automatically{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Could not reconnect automatically: {e}{Style.RESET_ALL}")
        
        while True:
            try:
                self.print_menu()
                choice = input(f"{Fore.CYAN}Enter your choice (1-7): {Style.RESET_ALL}").strip()
                
                if choice == '1':
                    await self.setup_telegram_auth()
                elif choice == '2':
                    self.preview_phone_numbers()
                elif choice == '3':
                    await self.import_contacts_from_file()
                elif choice == '4':
                    await self.add_single_contact()
                elif choice == '5':
                    self.view_statistics()
                elif choice == '6':
                    self.show_configuration()
                elif choice == '7':
                    print(f"{Fore.GREEN}👋 Goodbye!{Style.RESET_ALL}")
                    if self.contact_manager and self.contact_manager.telegram_manager:
                        await self.contact_manager.telegram_manager.disconnect()
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please enter 1-7.{Style.RESET_ALL}")
                
                if choice != '7':
                    input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
                    print()
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
                if self.contact_manager and self.contact_manager.telegram_manager:
                    await self.contact_manager.telegram_manager.disconnect()
                break
            except Exception as e:
                print(f"\n{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")


def main():
    """Main entry point."""
    try:
        cli = ContactImporterCLI()
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()