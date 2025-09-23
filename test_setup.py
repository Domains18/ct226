#!/usr/bin/env python3
"""Test script to verify phone number parsing."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_phone_parsing():
    """Test phone number parsing with the sample data."""
    print("🧪 Testing Phone Number Parser")
    print("="*40)
    
    try:
        from src.phone_parser import parse_phone_file

        # Test with the sample file
        file_path = "src/data/HGCS12.txt"
        
        if not Path(file_path).exists():
            print(f"❌ Test file not found: {file_path}")
            return False
        
        print(f"📄 Parsing: {file_path}")
        
        phone_numbers, stats = parse_phone_file(file_path, country="HK")
        
        print(f"\n📊 Results:")
        print(f"Total numbers: {stats['total']}")
        print(f"Valid numbers: {stats['valid']}")
        print(f"Invalid numbers: {stats['invalid']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        
        if stats['country_codes']:
            print(f"\nCountry codes:")
            for code, count in stats['country_codes'].items():
                print(f"  {code}: {count}")
        
        # Show some examples
        valid_numbers = [p for p in phone_numbers if p.is_valid]
        if valid_numbers:
            print(f"\n✅ Sample valid numbers:")
            for i, phone in enumerate(valid_numbers[:5]):
                print(f"  {phone.raw} → {phone.formatted}")
        
        invalid_numbers = [p for p in phone_numbers if not p.is_valid]
        if invalid_numbers:
            print(f"\n❌ Sample invalid numbers:")
            for i, phone in enumerate(invalid_numbers[:3]):
                print(f"  {phone.raw} - {phone.error_message}")
        
        return stats['success_rate'] > 80  # Consider success if >80% valid
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing Configuration")
    print("="*30)
    
    try:
        from src.config import config
        
        country = config.get('defaults.country_code')
        print(f"Default country: {country}")
        
        phone_config = config.get_phone_formatting()
        print(f"Phone formatting: {phone_config}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def main():
    """Run tests."""
    print("🚀 Telegram Contact Importer - Test Suite")
    print("="*50)
    
    # Test phone parsing
    parse_success = test_phone_parsing()
    
    # Test config
    config_success = test_config()
    
    print(f"\n📋 Test Results:")
    print(f"Phone parsing: {'✅ PASS' if parse_success else '❌ FAIL'}")
    print(f"Configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
    
    if parse_success and config_success:
        print(f"\n🎉 All tests passed! You can run: python main.py")
        return True
    else:
        print(f"\n❌ Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)