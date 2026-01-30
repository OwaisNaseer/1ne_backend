"""
OCR provider implementations.
"""
import os
import shutil
import platform
from typing import List, Optional
from pathlib import Path

from app.core.logging import get_logger
from app.domains.content_ingestion.providers.base import OCRProvider, PageText
from app.domains.content_ingestion.providers.ocr_preflight import OcrPreflight

logger = get_logger(__name__)


class TesseractOCRProvider(OCRProvider):
    """Tesseract OCR provider (free, MVP)."""
    
    provider_name = "tesseract"
    
    def __init__(self):
        """Initialize Tesseract OCR provider with binary discovery."""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            self.pytesseract = pytesseract
            self.convert_from_path = convert_from_path
            
            # Discover Tesseract binary
            self._setup_tesseract_binary()
            
            # Discover Poppler path
            self.poppler_path = self._find_poppler_path()
        except ImportError as e:
            logger.warning(f"Tesseract dependencies not installed: {e}")
            self.pytesseract = None
            self.convert_from_path = None
            self.poppler_path = None
    
    def _setup_tesseract_binary(self):
        """Setup Tesseract binary path using discovery logic."""
        if self.pytesseract is None:
            return
        
        # Check explicit env var first
        tesseract_cmd = os.getenv("TESSERACT_CMD")
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            self.pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            logger.info(f"Using Tesseract from TESSERACT_CMD: {tesseract_cmd}")
            return
        
        # Check PATH
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            self.pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"Using Tesseract from PATH: {tesseract_path}")
            return
        
        # Windows-specific default locations
        if platform.system() == "Windows":
            default_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in default_paths:
                if os.path.exists(path):
                    self.pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Using Tesseract from default Windows location: {path}")
                    return
        
        # If not found, pytesseract will try default behavior
        logger.warning("Tesseract binary not found via discovery, pytesseract will use default")
    
    def _find_poppler_path(self) -> Optional[str]:
        """Find Poppler directory path."""
        # Check explicit env var first
        poppler_path = os.getenv("POPPLER_PATH")
        if poppler_path:
            poppler_dir = Path(poppler_path)
            if poppler_dir.is_dir():
                pdftoppm = poppler_dir / ("pdftoppm.exe" if platform.system() == "Windows" else "pdftoppm")
                if pdftoppm.exists():
                    logger.info(f"Using Poppler from POPPLER_PATH: {poppler_path}")
                    return str(poppler_dir)
        
        # Check PATH
        pdftoppm_path = shutil.which("pdftoppm")
        if pdftoppm_path:
            poppler_dir = str(Path(pdftoppm_path).parent)
            logger.info(f"Using Poppler from PATH: {poppler_dir}")
            return poppler_dir
        
        return None
    
    def validate_config(self) -> bool:
        """Check if Tesseract is available using preflight checks."""
        if self.pytesseract is None:
            return False
        
        try:
            # Use preflight check for robust validation
            preflight_result = OcrPreflight.check()
            if not preflight_result["tesseract_found"]:
                return False
            
            # Also verify pytesseract can access it
            self.pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract validation failed: {e}")
            return False
    
    async def run_ocr(
        self,
        pdf_path: str,
        language: str = "eng",
        **kwargs
    ) -> List[PageText]:
        """
        Run OCR on PDF using Tesseract.
        
        Args:
            pdf_path: Path to PDF file
            language: Language code (default: "eng")
            
        Returns:
            List of PageText objects
        """
        if not self.validate_config():
            raise RuntimeError("Tesseract OCR not properly configured")
        
        # Ensure PDF path is absolute
        pdf_path_abs = str(Path(pdf_path).resolve())
        if not os.path.exists(pdf_path_abs):
            raise FileNotFoundError(f"PDF file not found: {pdf_path_abs}")
        
        first_page = kwargs.get("first_page")
        last_page = kwargs.get("last_page")
        dpi = int(kwargs.get("dpi") or 300)
        thread_count = kwargs.get("thread_count")

        range_msg = ""
        if first_page is not None or last_page is not None:
            range_msg = f" pages={first_page or '?'}..{last_page or '?'}"

        logger.info(f"Running Tesseract OCR on {pdf_path_abs}{range_msg} (language: {language}, dpi: {dpi})")
        
        pages_text = []
        
        try:
            # Convert PDF to images (use poppler_path if available)
            convert_kwargs = {"dpi": dpi}
            # Support converting only a page range to reduce memory usage
            if first_page is not None:
                convert_kwargs["first_page"] = int(first_page)
            if last_page is not None:
                convert_kwargs["last_page"] = int(last_page)
            # Allow pdf2image to use multiple threads when supported
            if thread_count is not None:
                try:
                    convert_kwargs["thread_count"] = int(thread_count)
                except Exception:
                    pass
            if self.poppler_path:
                # Ensure poppler_path is absolute
                poppler_path_abs = str(Path(self.poppler_path).resolve())
                convert_kwargs["poppler_path"] = poppler_path_abs
                logger.info(f"Using Poppler path: {poppler_path_abs}")
                # Prepend Poppler bin directory to PATH for DLL resolution on Windows
                # Prepend (not append) ensures DLLs are found before system paths
                if platform.system() == "Windows":
                    current_path = os.environ.get("PATH", "")
                    if poppler_path_abs not in current_path:
                        os.environ["PATH"] = f"{poppler_path_abs};{current_path}"
                        logger.debug(f"Prepended Poppler to PATH: {poppler_path_abs}")
            images = self.convert_from_path(pdf_path_abs, **convert_kwargs)
            
            # If we converted a specific range, page numbers should match the PDF page numbers
            base_page_no = int(first_page) if first_page is not None else 1
            for idx, image in enumerate(images, start=0):
                page_num = base_page_no + idx
                try:
                    # Run OCR on image
                    text = self.pytesseract.image_to_string(image, lang=language)
                    char_count = len(text.strip())
                    
                    # Get confidence (average)
                    try:
                        data = self.pytesseract.image_to_data(image, lang=language, output_type=self.pytesseract.Output.DICT)
                        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                        avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else None
                    except Exception:
                        avg_confidence = None
                    
                    pages_text.append(PageText(
                        page_no=page_num,
                        text=text,
                        char_count=char_count,
                        ocr_confidence=avg_confidence,
                        ocr_engine="tesseract"
                    ))
                    
                    logger.debug(f"OCR completed for page {page_num}: {char_count} chars")
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num}: {e}")
                    # Add empty page on error
                    pages_text.append(PageText(
                        page_no=page_num,
                        text="",
                        char_count=0,
                        ocr_engine="tesseract"
                    ))
            
            logger.info(f"OCR completed: {len(pages_text)} pages processed")
            return pages_text
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tesseract OCR failed: {error_msg}")
            # Provide more context for pdf2image errors
            if "pdf2image" in error_msg.lower() or "pdfinfo" in error_msg.lower() or "page count" in error_msg.lower():
                if self.poppler_path:
                    poppler_path_abs = str(Path(self.poppler_path).resolve())
                    pdfinfo_exe = Path(poppler_path_abs) / ("pdfinfo.exe" if platform.system() == "Windows" else "pdfinfo")
                    if pdfinfo_exe.exists():
                        error_msg += f" (Poppler found at {poppler_path_abs}, pdfinfo.exe exists but may have DLL dependency issues)"
                    else:
                        error_msg += f" (Poppler path {poppler_path_abs} exists but pdfinfo.exe not found)"
                else:
                    error_msg += " (Poppler path not configured)"
            raise RuntimeError(f"OCR processing failed: {error_msg}")


class EasyOCRProvider(OCRProvider):
    """EasyOCR provider (free, no binary installation needed)."""
    
    provider_name = "easyocr"
    
    def __init__(self):
        """Initialize EasyOCR provider."""
        try:
            import easyocr
            from pdf2image import convert_from_path
            self.easyocr_reader = None  # Lazy initialization
            self.convert_from_path = convert_from_path
            self._initialized = False
            self._import_error = None
        except (ImportError, OSError) as e:
            logger.warning(f"EasyOCR dependencies not available: {e}")
            logger.warning("Install with: pip install easyocr pdf2image")
            logger.warning("On Windows, also install: Microsoft Visual C++ Redistributable")
            self.easyocr_reader = None
            self.convert_from_path = None
            self._initialized = False
            self._import_error = str(e)
    
    def _init_reader(self, languages: List[str] = None):
        """Initialize EasyOCR reader (lazy loading)."""
        if self._initialized:
            return
        
        if self.easyocr_reader is None:
            try:
                import easyocr
                # EasyOCR supports 80+ languages, default to English
                lang_list = languages or ['en']
                logger.info(f"Initializing EasyOCR reader with languages: {lang_list}")
                self.easyocr_reader = easyocr.Reader(lang_list, gpu=False)  # Use CPU for compatibility
                self._initialized = True
                logger.info("EasyOCR reader initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR reader: {e}")
                raise RuntimeError(f"EasyOCR initialization failed: {str(e)}")
    
    def validate_config(self) -> bool:
        """Check if EasyOCR is available."""
        if hasattr(self, '_import_error') and self._import_error:
            return False
        if self.easyocr_reader is None:
            try:
                import easyocr
                from pdf2image import convert_from_path
                return True
            except (ImportError, OSError):
                return False
        return self._initialized
    
    async def run_ocr(
        self,
        pdf_path: str,
        language: str = "eng",
        **kwargs
    ) -> List[PageText]:
        """
        Run OCR on PDF using EasyOCR.
        
        Args:
            pdf_path: Path to PDF file
            language: Language code (default: "eng" -> "en" for EasyOCR)
            
        Returns:
            List of PageText objects
        """
        if not self.validate_config():
            raise RuntimeError("EasyOCR not properly configured. Install with: pip install easyocr pdf2image")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Map language codes: eng -> en, etc.
        lang_map = {"eng": "en", "en": "en", "ur": "ur", "ar": "ar"}
        easyocr_lang = lang_map.get(language.lower(), "en")
        
        logger.info(f"Running EasyOCR on {pdf_path} (language: {easyocr_lang})")
        
        # Initialize reader if not already done
        self._init_reader([easyocr_lang])
        
        pages_text = []
        
        try:
            # Convert PDF to images
            images = self.convert_from_path(pdf_path, dpi=300)
            
            for page_num, image in enumerate(images, start=1):
                try:
                    # Run OCR on image
                    results = self.easyocr_reader.readtext(image)
                    
                    # Combine all detected text
                    text_lines = [result[1] for result in results]  # result[1] is the text
                    text = "\n".join(text_lines)
                    char_count = len(text.strip())
                    
                    # Calculate average confidence
                    confidences = [result[2] for result in results]  # result[2] is confidence
                    avg_confidence = sum(confidences) / len(confidences) if confidences else None
                    
                    pages_text.append(PageText(
                        page_no=page_num,
                        text=text,
                        char_count=char_count,
                        ocr_confidence=avg_confidence,
                        ocr_engine="easyocr"
                    ))
                    
                    logger.debug(f"EasyOCR completed for page {page_num}: {char_count} chars")
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num} with EasyOCR: {e}")
                    # Add empty page on error
                    pages_text.append(PageText(
                        page_no=page_num,
                        text="",
                        char_count=0,
                        ocr_engine="easyocr"
                    ))
            
            logger.info(f"EasyOCR completed: {len(pages_text)} pages processed")
            return pages_text
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            raise RuntimeError(f"OCR processing failed: {str(e)}")


class MathpixOCRProvider(OCRProvider):
    """Mathpix OCR provider (paid, future-ready stub)."""
    
    provider_name = "mathpix"
    
    def __init__(self):
        """Initialize Mathpix OCR provider (stub for MVP)."""
        self.app_id = os.getenv("MATHPIX_APP_ID")
        self.app_key = os.getenv("MATHPIX_APP_KEY")
    
    def validate_config(self) -> bool:
        """Check if Mathpix is configured (stub - always False for MVP)."""
        # In MVP, Mathpix is not used
        return False
    
    async def run_ocr(
        self,
        pdf_path: str,
        language: str = "eng",
        **kwargs
    ) -> List[PageText]:
        """
        Run OCR on PDF using Mathpix (stub - not implemented in MVP).
        
        This is a placeholder for future Mathpix integration.
        """
        raise NotImplementedError(
            "Mathpix OCR is not implemented in MVP. "
            "Set OCR_ENGINE=tesseract for free OCR, or implement Mathpix integration."
        )
