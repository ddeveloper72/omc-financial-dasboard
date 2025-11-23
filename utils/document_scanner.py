import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DocumentScanner:
    """Scan directories for AGM documents (PDFs and other formats)"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.supported_extensions = ['.pdf', '.PDF']
        
    def scan_directory(self) -> List[Dict[str, any]]:
        """
        Recursively scan directory for supported document files
        
        Returns:
            List of dictionaries containing file metadata
        """
        documents = []
        
        if not self.base_path.exists():
            logger.error(f"Directory does not exist: {self.base_path}")
            return documents
            
        if not os.access(self.base_path, os.R_OK):
            logger.error(f"No read permission for directory: {self.base_path}")
            return documents
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                for filename in files:
                    if any(filename.endswith(ext) for ext in self.supported_extensions):
                        filepath = Path(root) / filename
                        
                        try:
                            file_info = self._get_file_info(filepath)
                            documents.append(file_info)
                            logger.info(f"Found document: {filename}")
                        except Exception as e:
                            logger.error(f"Error processing {filename}: {str(e)}")
                            
        except PermissionError as e:
            logger.error(f"Permission denied while scanning: {str(e)}")
        except Exception as e:
            logger.error(f"Error during directory scan: {str(e)}")
            
        logger.info(f"Found {len(documents)} documents")
        return documents
    
    def _get_file_info(self, filepath: Path) -> Dict[str, any]:
        """Extract file metadata"""
        stat_info = filepath.stat()
        
        # Extract year from path
        extracted_year = self.extract_year_from_path(str(filepath))
        
        # Classify document type from filename
        doc_type = self._classify_document_type(filepath.name)
        
        return {
            'filename': filepath.name,
            'filepath': str(filepath),
            'file_size': stat_info.st_size,
            'modified_date': datetime.fromtimestamp(stat_info.st_mtime),
            'extension': filepath.suffix.lower(),
            'year': extracted_year,
            'document_type': doc_type
        }
    
    def extract_year_from_path(self, filepath: str) -> Optional[int]:
        """
        Try to extract year from file path or filename
        
        Args:
            filepath: Full path to document
            
        Returns:
            Year as integer or None
        """
        path_parts = Path(filepath).parts
        filename = Path(filepath).stem
        
        # Check path components and filename for 4-digit year
        for part in list(path_parts) + [filename]:
            # Look for 4-digit year (2000-2099)
            import re
            year_match = re.search(r'(20\d{2})', part)
            if year_match:
                return int(year_match.group(1))
        
        return None
    
    def _classify_document_type(self, filename: str) -> str:
        """
        Classify document type based on filename
        
        Returns:
            Document type: 'Audited Accounts', 'Proposed Budget', 'AGM Minutes', 'Other'
        """
        filename_lower = filename.lower()
        
        # Check for audited accounts / financial statements
        if any(term in filename_lower for term in [
            'audited account', 'financial statement', 'accounts 20',
            'audit', 'statement'
        ]):
            return 'Audited Accounts'
        
        # Check for proposed/draft budgets
        if any(term in filename_lower for term in [
            'budget', 'draft budget', 'proposed budget', 'apportionment'
        ]):
            return 'Proposed Budget'
        
        # Check for AGM/EGM minutes or notices
        if any(term in filename_lower for term in [
            'agm minutes', 'egm minutes', 'meeting minutes', 'agm notice'
        ]):
            return 'AGM Minutes'
        
        return 'Other'
    
    def filter_by_year(self, documents: List[Dict], year: int) -> List[Dict]:
        """Filter documents by year"""
        filtered = []
        for doc in documents:
            extracted_year = self.extract_year_from_path(doc['filepath'])
            if extracted_year == year:
                filtered.append(doc)
        return filtered
    
    def get_years_available(self, documents: List[Dict]) -> List[int]:
        """Extract all available years from document paths"""
        years = set()
        for doc in documents:
            year = self.extract_year_from_path(doc['filepath'])
            if year:
                years.add(year)
        return sorted(list(years))
