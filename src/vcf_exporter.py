"""Export phone numbers to VCF (vCard) format for importing to phone contacts."""

import logging
from pathlib import Path
from typing import List
import vobject

from .phone_parser import PhoneNumber


class VCFExporter:
    """Export phone numbers to VCF format."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def export_to_vcf(self, phone_numbers: List[PhoneNumber], output_file: str = "contacts.vcf", name_prefix: str = "Contact") -> bool:
        """
        Export phone numbers to VCF file.

        Args:
            phone_numbers: List of PhoneNumber objects to export
            output_file: Output VCF file path
            name_prefix: Prefix for contact names

        Returns:
            True if successful, False otherwise
        """
        try:
            # Filter valid phone numbers
            valid_numbers = [p for p in phone_numbers if p.is_valid]

            if not valid_numbers:
                self.logger.error("No valid phone numbers to export")
                return False

            # Create VCF file
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, phone in enumerate(valid_numbers, 1):
                    # Create vCard object
                    vcard = vobject.vCard()

                    # Add name
                    vcard.add('fn')
                    vcard.fn.value = f"{name_prefix} {phone.formatted[-4:]}"

                    vcard.add('n')
                    vcard.n.value = vobject.vcard.Name(
                        family=f"{phone.formatted[-4:]}",
                        given=name_prefix
                    )

                    # Add phone number
                    vcard.add('tel')
                    vcard.tel.value = phone.formatted
                    vcard.tel.type_param = 'CELL'

                    # Write to file
                    f.write(vcard.serialize())

            self.logger.info(f"Exported {len(valid_numbers)} contacts to {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting to VCF: {e}")
            return False

    def export_from_file(self, input_file: str, output_file: str = "contacts.vcf", name_prefix: str = "Contact") -> dict:
        """
        Export phone numbers from text file to VCF.

        Args:
            input_file: Input text file with phone numbers
            output_file: Output VCF file path
            name_prefix: Prefix for contact names

        Returns:
            Dictionary with export statistics
        """
        from .phone_parser import parse_phone_file

        try:
            # Parse phone numbers
            phone_numbers, stats = parse_phone_file(input_file)

            # Export to VCF
            success = self.export_to_vcf(phone_numbers, output_file, name_prefix)

            return {
                'success': success,
                'total': stats['total'],
                'valid': stats['valid'],
                'invalid': stats['invalid'],
                'output_file': output_file
            }

        except Exception as e:
            self.logger.error(f"Error exporting from file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
