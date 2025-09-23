#!/usr/bin/env python3
"""
Telegram Contact Importer
Interactive CLI for bulk importing phone numbers to your Telegram account.

Usage:
    python main.py              # Run interactive CLI
    python main.py --help       # Show help
    python main.py --file path  # Quick import from file
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.cli import ContactImporterCLI
    from src.cli import main as cli_main
    from src.config import config
    from src.phone_parser import parse_phone_file
    from src.utils import setup_logging
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def quick_preview(file_path: str):
    """Quick preview of phone numbers in a file."""
    print(f"📄 Quick Preview: {file_path}")
    print("=" * 50)
    
    try:
        phone_numbers, stats = parse_phone_file(file_path)
        
        print(f"Total numbers found: {stats['total']}")
        print(f"Valid numbers: {stats['valid']}")
        print(f"Invalid numbers: {stats['invalid']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        
        if stats['country_codes']:
            print("\nCountry codes detected:")
            for code, count in stats['country_codes'].items():
                print(f"  {code}: {count} numbers")
        
        # Show sample numbers
        valid_numbers = [p for p in phone_numbers if p.is_valid]
        if valid_numbers:
            print(f"\n✅ Sample valid numbers:")
            for i, phone in enumerate(valid_numbers[:5]):
                print(f"  {i+1}. {phone.raw} → {phone.formatted}")
            
            if len(valid_numbers) > 5:
                print(f"  ... and {len(valid_numbers) - 5} more")
        
        # Show invalid numbers if any
        invalid_numbers = [p for p in phone_numbers if not p.is_valid]
        if invalid_numbers:
            print(f"\n⚠️  Sample invalid numbers:")
            for i, phone in enumerate(invalid_numbers[:3]):
                print(f"  {i+1}. {phone.raw} - {phone.error_message}")
            
            if len(invalid_numbers) > 3:
                print(f"  ... and {len(invalid_numbers) - 3} more")
    
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        return False
    
    return True


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║             📱 Telegram Contact Importer CLI                ║
║                                                              ║
║  Bulk import phone numbers to your Telegram account         ║
║  • Interactive CLI with progress tracking                   ║
║  • Batch processing with error handling                     ║
║  • Phone number validation and formatting                   ║
║  • Skip existing contacts automatically                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_requirements():
    """Print setup requirements."""
    print("📋 Setup Requirements:")
    print("1. Telegram API credentials (api_id and api_hash)")
    print("   - Get them from: https://my.telegram.org/apps")
    print("2. Your phone number registered with Telegram")
    print("3. Text file with phone numbers (one per line)")
    print()
    print("📁 Sample file format:")
    print("   821020131384")
    print("   821020102136")
    print("   +852 1234 5678")
    print("   ...")
    print()


def validate_file(file_path: str) -> bool:
    """Validate that file exists and is readable."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    if not path.is_file():
        print(f"❌ Path is not a file: {file_path}")
        return False
    
    try:
        with open(path, 'r') as f:
            first_line = f.readline().strip()
            if not first_line:
                print(f"⚠️  File appears to be empty: {file_path}")
                return False
    except Exception as e:
        print(f"❌ Cannot read file: {e}")
        return False
    
    return True


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Telegram Contact Importer - Bulk import phone numbers to Telegram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run interactive CLI
  python main.py --preview data.txt       # Preview numbers in file
  python main.py --file data.txt          # Quick import from file
  python main.py --config                 # Show configuration
  
For first-time setup, run without arguments to use the interactive CLI.
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Phone numbers file to import'
    )
    
    parser.add_argument(
        '--preview', '-p',
        type=str,
        help='Preview phone numbers in file without importing'
    )
    
    parser.add_argument(
        '--config', '-c',
        action='store_true',
        help='Show current configuration'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Reduce output (quiet mode)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Specify log file path'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "ERROR" if args.quiet else "INFO"
    setup_logging(level=log_level, log_file=args.log_file, console=not args.quiet)
    
    # Handle different command modes
    if args.config:
        print_banner()
        print("⚙️  Current Configuration:")
        print("-" * 30)
        print(f"Default country: {config.get('defaults.country_code', 'Not set')}")
        print(f"Phone formatting: {config.get_phone_formatting()}")
        print(f"Validation settings: {config.get_validation()}")
        print(f"Logging: {config.get_logging()}")
        
        # Check for session files
        session_files = list(Path.cwd().glob("*.session"))
        config_files = list(Path.cwd().glob("telegram_*.json"))
        
        print(f"\n📁 Session Files:")
        if session_files:
            for f in session_files:
                print(f"  ✅ {f}")
        else:
            print(f"  ❌ No session files found")
        
        if config_files:
            for f in config_files:
                print(f"  ✅ {f}")
        
        return
    
    if args.preview:
        if not validate_file(args.preview):
            sys.exit(1)
        
        print_banner()
        success = quick_preview(args.preview)
        sys.exit(0 if success else 1)
    
    if args.file:
        if not validate_file(args.file):
            sys.exit(1)
        
        print_banner()
        print(f"🚀 Quick Import Mode")
        print(f"File: {args.file}")
        print()
        print("Note: This will start the interactive CLI with the file pre-selected.")
        print("You'll need to authenticate with Telegram first.")
        print()
        
        # Set the file for the CLI to use
        import os
        os.environ['CONTACT_IMPORTER_FILE'] = args.file
    
    # Default: Run interactive CLI
    if not args.quiet:
        print_banner()
        if not (args.file or args.preview or args.config):
            print_requirements()
    
    try:
        # Run the interactive CLI
        cli_main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()