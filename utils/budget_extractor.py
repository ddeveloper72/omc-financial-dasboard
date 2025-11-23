import re
import logging
from typing import List, Dict, Optional, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class BudgetExtractor:
    """Extract service charge information from document text"""
    
    def __init__(self):
        # Common patterns for currency amounts
        self.amount_patterns = [
            r'EUR?\s*([0-9,]+\.?[0-9]*)',  # EUR 1,234.56 or E 1234.56
            r'([0-9,]+\.?[0-9]*)\s*EUR?',  # 1,234.56 EUR
            r'\$\s*([0-9,]+\.?[0-9]*)',     # $ 1,234.56
            r'([0-9,]+\.?[0-9]*)',          # Plain number
        ]
        
        # Keywords that might indicate service charges
        self.charge_keywords = [
            'management fee', 'insurance', 'maintenance', 'cleaning',
            'lighting', 'lift', 'elevator', 'service charge', 'annual charge',
            'sinking fund', 'reserve fund', 'garden', 'landscaping',
            'repair', 'common area', 'utilities', 'water', 'electricity',
            'security', 'fire', 'legal', 'accounting', 'audit'
        ]
    
    def extract_charges(self, text: str, year: Optional[int] = None) -> List[Dict[str, any]]:
        """
        Extract service charges from document text
        
        Args:
            text: Extracted document text
            year: Document year (if known)
            
        Returns:
            List of extracted charges with metadata
        """
        charges = []
        
        if not text:
            logger.warning("No text provided for charge extraction")
            return charges
        
        # Split into lines for line-by-line analysis
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            
            if not line:
                continue
            
            # Check if line contains potential charge information
            if self._is_potential_charge_line(line):
                charge_info = self._extract_charge_from_line(line, line_num, year)
                if charge_info:
                    charges.append(charge_info)
        
        logger.info(f"Extracted {len(charges)} potential charges")
        return charges
    
    def _is_potential_charge_line(self, line: str) -> bool:
        """Check if line likely contains charge information"""
        line_lower = line.lower()
        
        # Must contain at least one keyword
        has_keyword = any(keyword in line_lower for keyword in self.charge_keywords)
        
        # Must contain a number (potential amount)
        has_number = bool(re.search(r'\d+', line))
        
        return has_keyword and has_number
    
    def _extract_charge_from_line(self, line: str, line_num: int, year: Optional[int]) -> Optional[Dict[str, any]]:
        """
        Extract charge details from a single line
        
        Returns:
            Dictionary with charge information or None
        """
        # Extract amount
        amount = self._extract_amount(line)
        if amount is None:
            return None
        
        # Extract charge name (everything before the amount, typically)
        charge_name = self._extract_charge_name(line)
        if not charge_name:
            return None
        
        return {
            'charge_name': charge_name,
            'amount': float(amount),
            'currency': self._detect_currency(line),
            'year': year,
            'raw_text': line,
            'line_number': line_num,
            'confidence_score': self._calculate_confidence(line)
        }
    
    def _extract_amount(self, text: str) -> Optional[Decimal]:
        """Extract monetary amount from text"""
        for pattern in self.amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1) if match.lastindex else match.group(0)
                # Remove commas and convert to Decimal
                amount_str = amount_str.replace(',', '')
                try:
                    amount = Decimal(amount_str)
                    # Sanity check: amounts should be positive and reasonable
                    if 0 < amount < 1000000:
                        return amount
                except:
                    continue
        return None
    
    def _extract_charge_name(self, line: str) -> Optional[str]:
        """Extract the name/description of the charge"""
        # Try to find text before the amount
        # Remove currency symbols and numbers to isolate the description
        cleaned = re.sub(r'[EUR$0-9,.\s]+$', '', line).strip()
        
        if len(cleaned) < 3:  # Too short to be meaningful
            return None
        
        # Clean up common separators
        cleaned = re.sub(r'[:\-\t]+', ' ', cleaned).strip()
        
        return cleaned if cleaned else None
    
    def _detect_currency(self, text: str) -> str:
        """Detect currency from text"""
        text_upper = text.upper()
        
        if 'EUR' in text_upper or 'E' in text_upper:
            return 'EUR'
        elif '$' in text or 'USD' in text_upper:
            return 'USD'
        elif 'GBP' in text_upper or chr(163) in text:  # Pound symbol
            return 'GBP'
        
        # Default to EUR for Irish property
        return 'EUR'
    
    def _calculate_confidence(self, line: str) -> float:
        """
        Calculate confidence score for extraction (0.0 to 1.0)
        
        Higher confidence for:
        - Clear currency symbols
        - Well-formatted amounts
        - Recognizable keywords
        """
        confidence = 0.5  # Base confidence
        
        # Boost for currency symbol
        if re.search(r'EUR?|\$|GBP', line, re.IGNORECASE):
            confidence += 0.2
        
        # Boost for recognizable keywords
        line_lower = line.lower()
        keyword_count = sum(1 for keyword in self.charge_keywords if keyword in line_lower)
        confidence += min(0.2, keyword_count * 0.1)
        
        # Boost for well-formatted numbers
        if re.search(r'\d{1,3}(,\d{3})*(\.\d{2})?', line):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def group_by_category(self, charges: List[Dict[str, any]]) -> Dict[str, List[Dict]]:
        """Group charges by detected category"""
        categories = {}
        
        for charge in charges:
            category = self._detect_category(charge['charge_name'])
            if category not in categories:
                categories[category] = []
            categories[category].append(charge)
        
        return categories
    
    def _detect_category(self, charge_name: str) -> str:
        """Detect category from charge name"""
        charge_lower = charge_name.lower()
        
        if any(word in charge_lower for word in ['management', 'admin', 'managing']):
            return 'Management'
        elif any(word in charge_lower for word in ['insurance']):
            return 'Insurance'
        elif any(word in charge_lower for word in ['maintenance', 'repair', 'upkeep']):
            return 'Maintenance'
        elif any(word in charge_lower for word in ['clean', 'cleaning']):
            return 'Cleaning'
        elif any(word in charge_lower for word in ['light', 'lighting', 'electric']):
            return 'Utilities'
        elif any(word in charge_lower for word in ['lift', 'elevator']):
            return 'Lift/Elevator'
        elif any(word in charge_lower for word in ['garden', 'landscape', 'grounds']):
            return 'Grounds'
        elif any(word in charge_lower for word in ['security', 'alarm']):
            return 'Security'
        elif any(word in charge_lower for word in ['sinking', 'reserve', 'fund']):
            return 'Reserve Fund'
        else:
            return 'Other'
