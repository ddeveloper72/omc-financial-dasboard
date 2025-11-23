import logging
from pathlib import Path
from typing import Optional, Dict
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PDFParser:
    """Extract text content from PDF documents"""
    
    def __init__(self):
        self.encoding = 'utf-8'
    
    def extract_text(self, filepath: str) -> Optional[str]:
        """
        Extract all text content from a PDF file
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Extracted text as string, or None if extraction fails
        """
        try:
            reader = PdfReader(filepath)
            
            if reader.is_encrypted:
                logger.warning(f"PDF is encrypted: {filepath}")
                return None
            
            text_content = []
            
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                        logger.debug(f"Extracted text from page {page_num}")
                except Exception as e:
                    logger.error(f"Error extracting page {page_num} from {filepath}: {str(e)}")
            
            full_text = '\n'.join(text_content)
            logger.info(f"Successfully extracted {len(full_text)} characters from {Path(filepath).name}")
            
            return full_text if full_text else None
            
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return None
        except Exception as e:
            logger.error(f"Error parsing PDF {filepath}: {str(e)}")
            return None
    
    def extract_metadata(self, filepath: str) -> Dict[str, any]:
        """
        Extract PDF metadata (title, author, creation date, etc.)
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        try:
            reader = PdfReader(filepath)
            
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': reader.metadata.get('/CreationDate', ''),
                }
            
            metadata['page_count'] = len(reader.pages)
            metadata['is_encrypted'] = reader.is_encrypted
            
            logger.info(f"Extracted metadata from {Path(filepath).name}")
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {filepath}: {str(e)}")
        
        return metadata
    
    def extract_text_by_page(self, filepath: str) -> Dict[int, str]:
        """
        Extract text from PDF, organized by page number
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Dictionary mapping page numbers to text content
        """
        pages = {}
        
        try:
            reader = PdfReader(filepath)
            
            if reader.is_encrypted:
                logger.warning(f"PDF is encrypted: {filepath}")
                return pages
            
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        pages[page_num] = page_text
                except Exception as e:
                    logger.error(f"Error extracting page {page_num}: {str(e)}")
            
            logger.info(f"Extracted {len(pages)} pages from {Path(filepath).name}")
            
        except Exception as e:
            logger.error(f"Error parsing PDF {filepath}: {str(e)}")
        
        return pages
