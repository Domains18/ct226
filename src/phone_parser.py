"""Phone number parser and validator for contact importer."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import phonenumbers

from .config import config


@dataclass
class PhoneNumber:
    """Represents a parsed phone number."""
    raw: str
    formatted: str
    country_code: str
    is_valid: bool
    error_message: Optional[str] = None


class PhoneParser:
    """Parser for phone numbers from text files."""
    
    def __init__(self, default_country: str = "HK"):
        """Initialize parser with default country code."""
        self.default_country = default_country
        self.validation_config = config.get_validation()
        self.formatting_config = config.get_phone_formatting()
    
    def parse_file(self, file_path: str) -> List[PhoneNumber]:
        """Parse phone numbers from a text file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        phone_numbers = []
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#') or line.startswith('//'):
                    continue
                
                # Skip lines that look like headers or labels
                if any(char.isalpha() for char in line) and not self._looks_like_phone(line):
                    continue
                
                # Try to extract phone number from line
                phone = self._extract_phone_from_line(line)
                if phone:
                    parsed = self.parse_number(phone, line_num)
                    phone_numbers.append(parsed)
        
        return phone_numbers
    
    def parse_number(self, phone_str: str, line_num: Optional[int] = None) -> PhoneNumber:
        """Parse a single phone number string."""
        original = phone_str.strip()

        # Clean the phone number
        cleaned = self._clean_phone_number(original)

        # If the number doesn't start with +, try adding it if it looks like an international number
        # (numbers starting with digits that could be country codes)
        if not cleaned.startswith('+') and len(cleaned) >= 10:
            # Try with + prefix first (for international format without +)
            try:
                test_parsed = phonenumbers.parse('+' + cleaned, None)
                if phonenumbers.is_valid_number(test_parsed):
                    cleaned = '+' + cleaned
            except:
                # If that fails, continue with original cleaned number
                pass

        try:
            # Parse with phonenumbers library
            parsed = phonenumbers.parse(cleaned, self.default_country)
            
            # Validate the number
            is_valid = phonenumbers.is_valid_number(parsed)
            
            if is_valid:
                # Format the number
                formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                country_code = f"+{parsed.country_code}"
                
                return PhoneNumber(
                    raw=original,
                    formatted=formatted,
                    country_code=country_code,
                    is_valid=True
                )
            else:
                return PhoneNumber(
                    raw=original,
                    formatted=cleaned,
                    country_code="",
                    is_valid=False,
                    error_message="Invalid phone number format"
                )
                
        except phonenumbers.NumberParseException as e:
            return PhoneNumber(
                raw=original,
                formatted=cleaned,
                country_code="",
                is_valid=False,
                error_message=str(e)
            )
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean phone number by removing unwanted characters."""
        # Remove characters specified in config
        chars_to_remove = self.formatting_config.get('remove_chars', [])
        for char in chars_to_remove:
            phone = phone.replace(char, '')

        # Auto-detect international numbers without + prefix
        # Check if it starts with a likely country code and add + if missing
        if not phone.startswith('+') and len(phone) >= 10:
            # Common country code patterns
            # Try to detect if this is an international number
            if (phone.startswith('1') and len(phone) == 11) or \
               (phone.startswith(('2', '3', '4', '5', '6', '7', '8', '9')) and len(phone) >= 11):
                # Looks like international format without +
                phone = '+' + phone

        # Handle Hong Kong numbers specifically
        if phone.startswith('82102'):
            # This appears to be a Hong Kong number format
            # Convert to standard Hong Kong format: +852 XXXX XXXX
            if len(phone) == 12:  # 821020123456 format
                phone = '+852 ' + phone[5:]  # Remove 82102 prefix and add +852

        # If no country code and auto_add_country_code is enabled
        elif self.formatting_config.get('auto_add_country_code', False):
            if not phone.startswith('+'):
                country_code = config.get_country_code(self.default_country)
                if country_code:
                    phone = country_code + phone

        return phone
    
    def _extract_phone_from_line(self, line: str) -> Optional[str]:
        """Extract phone number from a line of text."""
        # Look for sequences of digits with optional separators
        phone_pattern = r'[\d\-\(\)\.\s\+]{7,}'
        matches = re.findall(phone_pattern, line)
        
        if matches:
            # Return the longest match (most likely to be a complete phone number)
            return max(matches, key=len).strip()
        
        return None
    
    def _looks_like_phone(self, text: str) -> bool:
        """Check if text looks like it could contain a phone number."""
        # Count digits in the text
        digit_count = sum(1 for char in text if char.isdigit())
        return digit_count >= self.validation_config.get('min_length', 7)
    
    def get_stats(self, phone_numbers: List[PhoneNumber]) -> dict:
        """Get statistics about parsed phone numbers."""
        total = len(phone_numbers)
        valid = sum(1 for p in phone_numbers if p.is_valid)
        invalid = total - valid
        
        # Count by country code
        country_codes = {}
        for phone in phone_numbers:
            if phone.is_valid and phone.country_code:
                country_codes[phone.country_code] = country_codes.get(phone.country_code, 0) + 1
        
        return {
            'total': total,
            'valid': valid,
            'invalid': invalid,
            'success_rate': (valid / total * 100) if total > 0 else 0,
            'country_codes': country_codes
        }


def parse_phone_file(file_path: str, country: str = "HK") -> Tuple[List[PhoneNumber], dict]:
    """Convenience function to parse a phone file and return numbers with stats."""
    parser = PhoneParser(country)
    numbers = parser.parse_file(file_path)
    stats = parser.get_stats(numbers)
    return numbers, stats