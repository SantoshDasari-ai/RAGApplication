import os
from dotenv import load_dotenv
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod

# Load environment variables from the .env file
load_dotenv()

# Directory containing PDF files and output directory
pdf_directory = os.getenv('PDF_DIRECTORY')
output_directory = os.getenv('CHUNKED_TEXT_DIRECTORY')

if pdf_directory is None or output_directory is None:
    raise EnvironmentError("Required environment variables PDF_DIRECTORY or CHUNKED_TEXT_DIRECTORY are not set.")

class PDFProcessor(ABC):
    @abstractmethod
    def process_pdf(self, pdf_file: str):
        pass

class MyPDFProcessor(PDFProcessor):
    def __init__(self, pdf_dir: str, out_dir: str):
        self.pdf_directory = pdf_dir
        self.output_directory = out_dir

    def extract_text_from_page(self, doc, page_num):
        page = doc.load_page(page_num)
        text_in_page = page.get_text()
        metadata = {
            'page_number': page_num + 1,
            'width': page.rect.width,
            'height': page.rect.height,
            'rotation': page.rotation
        }
        return text_in_page, metadata

    def save_text_to_file(self, text: str, metadata: dict, output_file_path: str):
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f"METADATA: {metadata}\n\n")
            output_file.write(text)
            output_file.write(f"\n\n-- End of Page {metadata['page_number']} --\n\n")

    def process_pdf(self, pdf_file: str):
        pdf_path = os.path.join(self.pdf_directory, pdf_file)
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(doc.page_count):
                text_in_page, metadata = self.extract_text_from_page(doc, page_num)
                output_file_path = os.path.join(self.output_directory, f"{pdf_file}_page_{page_num + 1}.txt")
                self.save_text_to_file(text_in_page, metadata, output_file_path)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

# Example usage
if __name__ == "__main__":
    processor = MyPDFProcessor(pdf_directory, output_directory)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(processor.process_pdf, pdf_file) for pdf_file in os.listdir(pdf_directory) if pdf_file.endswith('.pdf')]
        for future in as_completed(futures):
            future.result()
