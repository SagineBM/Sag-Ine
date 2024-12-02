import docx
import pandas as pd
import PyPDF2
from io import StringIO
import os

class FileHandler:
    @staticmethod
    def read_file(file_path: str) -> tuple[str, str]:
        """Returns tuple of (file_content, file_type)"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.txt':
            return FileHandler._read_txt(file_path), 'text'
        elif ext == '.docx':
            return FileHandler._read_docx(file_path), 'docx'
        elif ext == '.pdf':
            return FileHandler._read_pdf(file_path), 'pdf'
        elif ext in ['.csv', '.xlsx', '.xls']:
            return FileHandler._read_spreadsheet(file_path), 'spreadsheet'
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def _read_txt(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def _read_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def _read_pdf(file_path: str) -> str:
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)

    @staticmethod
    def _read_spreadsheet(file_path: str) -> str:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # Convert DataFrame to string representation
        buffer = StringIO()
        df.to_string(buffer)
        return buffer.getvalue()

    @staticmethod
    def get_supported_extensions() -> list:
        return ['.txt', '.docx', '.pdf', '.csv', '.xlsx', '.xls']
