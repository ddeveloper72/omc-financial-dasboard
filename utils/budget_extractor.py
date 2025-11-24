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
            r'€\s*([0-9,]+\.?[0-9]*)',     # € 1,234.56
            r'([0-9,]+\.?[0-9]*)\s*EUR?',  # 1,234.56 EUR
            r'\$\s*([0-9,]+\.?[0-9]*)',     # $ 1,234.56
            r'\s([0-9,]{3,}\.?[0-9]*)',    # Standalone number with commas (4,730 or 10,414)
            r'([0-9,]+\.?[0-9]*)',          # Plain number (fallback)
        ]
        
        # Keywords that might indicate service charges
        self.charge_keywords = [
            'management fee', 'insurance', 'maintenance', 'cleaning',
            'lighting', 'lift', 'elevator', 'service charge', 'annual charge',
            'sinking fund', 'reserve fund', 'garden', 'landscaping',
            'repair', 'common area', 'utilities', 'water', 'electricity',
            'security', 'fire', 'legal', 'accounting', 'audit', 'vermin',
            'postage', 'stationery', 'bulb', 'gate', 'alarm', 'grounds',
            'salting', 'refuse', 'waste', 'parking', 'agent', 'fees',
            'accountancy', 'debt collection'
        ]
        
        # Patterns to exclude (section headers, page numbers, etc.)
        self.exclusion_patterns = [
            r'^\d+\s+\d+\s+[A-Z]',  # Section numbers like "9 1 Accounting"
            r'^\d+\.\d+\s+[A-Z]',   # Subsection like "1.1 Accounting"
            r'\bSection\s+\d+\b',   # "Section 19"
            r'\bChapter\s+\d+\b',   # "Chapter 15"
            r'\bPart\s+\d+\b',      # "Part 6"
            r'^\(\w\)\s+',          # "(a) the company"
            r'\bpolicies\b',        # Policy statements
            r'\bconvention\b',      # Accounting conventions
            r'\bin accordance with\b',  # Policy explanations
            r'\bthe company must\b',    # Requirements/obligations
            r'\bis availing\b',         # Company actions
            r'\brepresents\b.*\breceived\b',  # Income definitions
            r'\bwere levied\b',         # Past tense narratives
            # AGM Minutes specific patterns
            r'^\d+\.\s+Adopt',      # "2. Adoption of..."
            r'^\d+\.\s+Appoint',    # "3. Appoint..."
            r'^\•\s+A copy of',     # "• A copy of the Audited Accounts"
            r'\bAgenda\b',          # Agenda items
            r'\bMinutes\b',         # Minutes references
            r'\bif you have any queries\b',  # AGM boilerplate text
            r'\bApproval of the\b', # "Approval of the auditors"
            r'\bRemuneration\b',    # "Auditors Remuneration"
            r'\bfix the auditors\b', # "fix the auditors remuneration"
            # Table headers and column references
            r'\bTotal\s+20\d{2}\b',  # "Total 2024", "Total 2023"
            r'^20\d{2}$',             # Just a year on its own line
            # Column headers and document labels
            r'^\s*Unaudited\s*$',     # "Unaudited" column header
            r'^\s*Audited\s*$',       # "Audited" column header
            r'^\s*Draft\s*$',         # "Draft" label
            # Section headers without amounts (category names)
            r'^\s*Lift\s+Costs\s*$',  # "Lift Costs" section header
            r'^\s*Insurance\s*$',     # "Insurance" section header (when standalone)
        ]
    
    def _preprocess_ocr_text(self, text: str) -> str:
        """
        Preprocess OCR text to handle columnar budget format
        
        OCR often produces columnar text where charge names are in one section
        and amounts are in another section below, like:
        
        Building Insurance
        Lift Engineering Inspection insurance
        €23,000
        €1,500 €400
        
        We need to pair them up:
        Building Insurance €23,000
        Lift Engineering Inspection insurance €1,500
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Separate charge names from amount lines
        charge_lines = []
        amount_lines = []
        
        for line in lines:
            # Check if line is purely amounts (starts with currency or is just numbers)
            if re.match(r'^[€$£EUR]\s*[0-9,]+(\s+[€$£EUR]\s*[0-9,]+)*$', line):
                # Split multiple amounts on same line
                amounts = re.findall(r'[€$£EUR]\s*[0-9,]+', line)
                amount_lines.extend(amounts)
            else:
                # Check if it looks like a charge name (has keywords or reasonable length)
                line_lower = line.lower()
                has_keyword = any(keyword in line_lower for keyword in self.charge_keywords)
                # Also check it's not a section header (too short) or excluded pattern
                is_excluded = any(re.search(pattern, line, re.IGNORECASE) for pattern in self.exclusion_patterns)
                
                if (has_keyword or len(line) > 15) and not is_excluded:
                    charge_lines.append(line)
        
        # Try to pair up charges with amounts
        merged_lines = []
        for i, charge in enumerate(charge_lines):
            if i < len(amount_lines):
                merged_lines.append(f"{charge} {amount_lines[i]}")
            else:
                # No amount available, include charge anyway
                merged_lines.append(charge)
        
        return '\n'.join(merged_lines)
    
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
        
        # Preprocess text to merge multi-line charges (OCR often splits charge name and amount)
        text = self._preprocess_ocr_text(text)
        
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
        
        # Exclude lines matching exclusion patterns
        for pattern in self.exclusion_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return False
        
        # Must contain at least one keyword
        has_keyword = any(keyword in line_lower for keyword in self.charge_keywords)
        
        # Must contain a currency amount OR a number pattern that looks like an amount
        has_currency = bool(re.search(r'(EUR?|\$|€)\s*[0-9,]+', line, re.IGNORECASE))
        
        # Also accept lines with charge keywords followed by numbers (for schedules without EUR symbols)
        # Example: "Management fees    19,803    14,760"
        has_amount_pattern = bool(re.search(r'[A-Za-z]+.*\s+[0-9,]{3,}', line))
        
        # Line should be reasonably short (actual charge lines are typically concise)
        is_reasonable_length = len(line) < 200
        
        return has_keyword and (has_currency or has_amount_pattern) and is_reasonable_length
    
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
        
        # Classify charge type
        charge_type = self._classify_charge_type(charge_name, line)
        
        return {
            'charge_name': charge_name,
            'amount': float(amount),
            'currency': self._detect_currency(line),
            'year': year,
            'charge_type': charge_type,
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
                        # Exclude common year values that look like amounts
                        if amount in [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]:
                            continue
                        return amount
                except:
                    continue
        return None
    
    def _extract_charge_name(self, line: str) -> Optional[str]:
        """Extract the name/description of the charge"""
        # Try to find text before the amount
        # Remove currency symbols and numbers to isolate the description
        cleaned = re.sub(r'[EUR$€0-9,.\s]+$', '', line).strip()
        
        if len(cleaned) < 3:  # Too short to be meaningful
            return None
        
        # Exclude if it looks like a section number at the start
        if re.match(r'^\d+\s+\d+\s+', cleaned) or re.match(r'^\d+\.\d+\s+', cleaned):
            return None
        
        # Exclude if starts with (a), (b), etc.
        if re.match(r'^\([a-z]\)\s+', cleaned, re.IGNORECASE):
            return None
        
        # Clean up common separators
        cleaned = re.sub(r'[:\-\t]+', ' ', cleaned).strip()
        
        # Final check: should be a reasonable charge name
        if len(cleaned) > 150:  # Too long to be a charge name
            return None
        
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
    
    def _classify_charge_type(self, charge_name: str, full_line: str) -> str:
        """
        Classify if this is an expense, income, or balance sheet item
        
        Returns:
            'expense', 'income', or 'balance_sheet'
        """
        name_lower = charge_name.lower()
        line_lower = full_line.lower()
        
        # Balance sheet items (skip these for expense analysis)
        balance_sheet_indicators = [
            'bank balance', 'balance €', 'cash', 'debtor', 'creditor',
            'asset', 'liability', 'equity', 'retained earnings',
            'accounts receivable', 'accounts payable', 'fund balance'
        ]
        
        for indicator in balance_sheet_indicators:
            if indicator in name_lower or indicator in line_lower:
                return 'balance_sheet'
        
        # Income/Revenue items
        income_indicators = [
            'service charge', 'service charges', 'income', 'revenue',
            'charges received', 'charges receivable', 'receipts',
            'transfer from', 'contribution from'
        ]
        
        for indicator in income_indicators:
            if indicator in name_lower:
                return 'income'
        
        # Check if the line contains income context
        income_context = [
            'income represents', 'service charges received',
            'charges levied', 'charges of €'
        ]
        
        for context in income_context:
            if context in line_lower:
                return 'income'
        
        # Default to expense (management fees, insurance, maintenance, etc.)
        return 'expense'
    
    def deduplicate_charges(self, charges: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Deduplicate charges within a document by keeping the highest confidence
        entry for similar charge names in the same year.
        
        Args:
            charges: List of extracted charges
            
        Returns:
            Deduplicated list of charges
        """
        from collections import defaultdict
        
        # Group charges by normalized name and year
        groups = defaultdict(list)
        
        for charge in charges:
            # Normalize the charge name
            normalized_name = self._normalize_charge_name(charge['charge_name'])
            key = (normalized_name, charge['year'])
            groups[key].append(charge)
        
        # For each group, keep the charge with highest confidence
        deduplicated = []
        for (norm_name, year), charge_list in groups.items():
            if len(charge_list) == 1:
                deduplicated.append(charge_list[0])
            else:
                # Multiple charges with similar names - pick the best one
                best_charge = max(charge_list, key=lambda c: (
                    c.get('confidence_score', 0.5),  # Higher confidence first
                    c['amount'],                      # Higher amount (for fund contributions vs references)
                    len(c['charge_name']),           # More complete name
                    -len(c['raw_text'])              # Shorter raw text (less noise)
                ))
                deduplicated.append(best_charge)
                
                # Log what was deduplicated
                logger.info(f"Deduplicated {len(charge_list)} charges for '{norm_name}' ({year})")
                logger.info(f"  Kept: {best_charge['charge_name']} (EUR {best_charge['amount']}, confidence: {best_charge.get('confidence_score', 0.5):.2f})")
        
        return deduplicated
    
    def _normalize_charge_name(self, name: str) -> str:
        """
        Normalize a charge name for comparison purposes.
        Removes amounts, extra spaces, and standardizes common variations.
        """
        import re
        
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove currency amounts (EUR 1234, €1234, etc.)
        normalized = re.sub(r'eur?\s*[0-9,]+\.?[0-9]*', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'€\s*[0-9,]+\.?[0-9]*', '', normalized)
        normalized = re.sub(r'[0-9,]+\.?[0-9]*\s*eur?', '', normalized, flags=re.IGNORECASE)
        
        # Remove year references like "2023", "2024"
        normalized = re.sub(r'\b20\d{2}\b', '', normalized)
        
        # Remove special characters and extra spaces
        normalized = re.sub(r'[:\-€$]+', ' ', normalized)
        normalized = ' '.join(normalized.split())
        
        # Standardize common variations
        normalized = normalized.replace('sinking fund contribution', 'sinking fund')
        normalized = normalized.replace('reserve fund contribution', 'reserve fund')
        normalized = normalized.replace('common area budget', 'common area')
        
        # Remove "budget" suffix as it's often just a section reference
        normalized = re.sub(r'\s+budget\s*$', '', normalized)
        
        normalized = normalized.strip()
        
        return normalized
