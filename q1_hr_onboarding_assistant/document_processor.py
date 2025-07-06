import os
import PyPDF2
from docx import Document
from typing import List, Dict, Any
import re
from datetime import datetime
import hashlib

class DocumentProcessor:
    def __init__(self, config):
        self.config = config
        self.upload_dir = config.UPLOAD_DIR
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
        return text
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text based on file extension"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def hr_specific_chunking(self, text: str) -> List[Dict[str, Any]]:
        """HR-specific intelligent chunking strategy"""
        chunks = []
        
        # Split by common HR document sections
        sections = re.split(r'\n(?=Section|CHAPTER|PART|\d+\.\s*[A-Z])', text, flags=re.IGNORECASE)
        
        for section_idx, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Further split by paragraphs
            paragraphs = re.split(r'\n\s*\n', section)
            
            current_chunk = ""
            chunk_metadata = {
                "section_index": section_idx,
                "section_title": self._extract_section_title(section),
                "content_type": self._classify_content(section)
            }
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # If adding this paragraph would exceed chunk size, save current chunk
                if len(current_chunk) + len(paragraph) > self.config.CHUNK_SIZE:
                    if current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "metadata": chunk_metadata.copy()
                        })
                        current_chunk = ""
                
                current_chunk += paragraph + "\n\n"
            
            # Add remaining content as final chunk
            if current_chunk.strip():
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": chunk_metadata.copy()
                })
        
        return chunks
    
    def _extract_section_title(self, section: str) -> str:
        """Extract section title from the beginning of a section"""
        lines = section.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if re.match(r'^(Section|CHAPTER|PART|\d+\.\s*[A-Z])', line, re.IGNORECASE):
                return line
        return "Untitled Section"
    
    def _classify_content(self, text: str) -> str:
        """Classify content type based on keywords"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['vacation', 'leave', 'holiday', 'time off']):
            return "leave_policy"
        elif any(word in text_lower for word in ['health', 'insurance', 'medical', 'dental', 'vision']):
            return "benefits"
        elif any(word in text_lower for word in ['conduct', 'behavior', 'ethics', 'discipline']):
            return "conduct"
        elif any(word in text_lower for word in ['salary', 'compensation', 'pay', 'bonus']):
            return "compensation"
        elif any(word in text_lower for word in ['remote', 'work from home', 'telecommute']):
            return "work_arrangement"
        else:
            return "general"
    
    def process_document(self, file_path: str, original_filename: str) -> List[Dict[str, Any]]:
        """Process a document and return chunks with metadata"""
        # Extract text
        raw_text = self.extract_text(file_path)
        cleaned_text = self.clean_text(raw_text)
        
        # Generate document hash for tracking
        doc_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
        
        # Chunk the text
        chunks = self.hr_specific_chunking(cleaned_text)
        
        # Add document-level metadata to each chunk
        for chunk in chunks:
            chunk["metadata"].update({
                "document_name": original_filename,
                "document_hash": doc_hash,
                "processed_at": datetime.now().isoformat(),
                "file_path": file_path
            })
        
        return chunks 