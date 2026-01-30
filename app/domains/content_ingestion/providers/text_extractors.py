"""
Text extractor implementations.
"""
import os
from typing import List
from pathlib import Path

from app.core.logging import get_logger
from app.domains.content_ingestion.providers.base import TextExtractor, PageText

logger = get_logger(__name__)


class PDFTextExtractor(TextExtractor):
    """PDF text extractor using pdfplumber."""
    
    provider_name = "pdfplumber"
    
    def __init__(self):
        """Initialize PDF text extractor."""
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
        except ImportError as e:
            logger.warning(f"pdfplumber not installed: {e}")
            self.pdfplumber = None
    
    def validate_config(self) -> bool:
        """Check if pdfplumber is available."""
        return self.pdfplumber is not None
    
    async def extract_text(
        self,
        file_path: str,
        **kwargs
    ) -> List[PageText]:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of PageText objects
        """
        if not self.validate_config():
            raise RuntimeError("pdfplumber not properly configured")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        logger.info(f"Extracting text from PDF: {file_path}")
        
        pages_text = []
        
        try:
            with self.pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text() or ""
                        char_count = len(text.strip())
                        
                        pages_text.append(PageText(
                            page_no=page_num,
                            text=text,
                            char_count=char_count
                        ))
                        
                        logger.debug(f"Extracted text from page {page_num}: {char_count} chars")
                        
                    except Exception as e:
                        logger.error(f"Error extracting text from page {page_num}: {e}")
                        pages_text.append(PageText(
                            page_no=page_num,
                            text="",
                            char_count=0
                        ))
            
            logger.info(f"Text extraction completed: {len(pages_text)} pages processed")
            return pages_text
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            raise RuntimeError(f"Text extraction failed: {str(e)}")


class DOCXTextExtractor(TextExtractor):
    """DOCX text extractor using python-docx."""
    
    provider_name = "python-docx"
    
    def __init__(self):
        """Initialize DOCX text extractor."""
        try:
            from docx import Document
            self.Document = Document
        except ImportError as e:
            logger.warning(f"python-docx not installed: {e}")
            self.Document = None
    
    def validate_config(self) -> bool:
        """Check if python-docx is available."""
        return self.Document is not None
    
    async def extract_text(
        self,
        file_path: str,
        **kwargs
    ) -> List[PageText]:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            List of PageText objects (DOCX doesn't have pages, so we create one page)
        """
        if not self.validate_config():
            raise RuntimeError("python-docx not properly configured")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DOCX file not found: {file_path}")
        
        logger.info(f"Extracting text from DOCX: {file_path}")
        
        try:
            doc = self.Document(file_path)
            
            # Combine all paragraphs into one text
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_parts.append(cell.text)
            
            full_text = "\n\n".join(text_parts)
            char_count = len(full_text.strip())
            
            # DOCX doesn't have pages, so we create one page
            pages_text = [PageText(
                page_no=1,
                text=full_text,
                char_count=char_count
            )]
            
            logger.info(f"DOCX text extraction completed: {char_count} chars")
            return pages_text
            
        except Exception as e:
            logger.error(f"DOCX text extraction failed: {e}")
            raise RuntimeError(f"Text extraction failed: {str(e)}")
