from fpdf import FPDF
from fpdf.enums import XPos, YPos
import re
import os

class BookPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Try to load a Unicode font
        font_dir = "/usr/share/fonts/truetype/clear-sans/"
        fonts = {
            "": "ClearSans-Regular.ttf",
            "B": "ClearSans-Bold.ttf",
            "I": "ClearSans-Italic.ttf",
            "BI": "ClearSans-BoldItalic.ttf"
        }
        
        self.main_font = "Arial" # Default fallback
        
        if os.path.exists(font_dir):
            loaded_any = False
            for style, filename in fonts.items():
                path = os.path.join(font_dir, filename)
                if os.path.exists(path):
                    self.add_font("ClearSans", style, path)
                    loaded_any = True
            
            if loaded_any:
                self.main_font = "ClearSans"

    def header(self):
        self.set_font(self.main_font, 'B', 12)
        self.cell(0, 10, 'Compiled Telegram Book', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font(self.main_font, 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

def wrap_long_words(text, max_len=50):
    """
    Splits extremely long words (like URLs) that might break PDF layout.
    """
    words = text.split(' ')
    wrapped_words = []
    for word in words:
        if len(word) > max_len:
            # Chunk the long word
            chunks = [word[i:i+max_len] for i in range(0, len(word), max_len)]
            wrapped_words.append(' '.join(chunks))
        else:
            wrapped_words.append(word)
    return ' '.join(wrapped_words)

def generate_pdf(markdown_text, output_path):
    """
    Improved PDF generation using fpdf2 with Unicode support.
    """
    pdf = BookPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font(pdf.main_font, size=12)
    
    epw = pdf.epw
    
    lines = markdown_text.split('\n')
    for line in lines:
        line = wrap_long_words(line.strip())
        if not line:
            pdf.ln(5)
            continue
            
        if line.startswith('# '):
            pdf.set_font(pdf.main_font, 'B', 18)
            pdf.multi_cell(epw, 12, line[2:], align='C')
            pdf.ln(5)
            pdf.set_font(pdf.main_font, size=12)
        elif line.startswith('## '):
            pdf.set_font(pdf.main_font, 'B', 15)
            pdf.multi_cell(epw, 10, line[3:])
            pdf.ln(2)
            pdf.set_font(pdf.main_font, size=12)
        elif line.startswith('### '):
            pdf.set_font(pdf.main_font, 'B', 13)
            pdf.multi_cell(epw, 8, line[4:])
            pdf.ln(1)
            pdf.set_font(pdf.main_font, size=12)
        else:
            pdf.multi_cell(epw, 8, line)
    
    print(f"Saving PDF to {output_path}...")
    pdf.output(output_path)

def save_markdown(markdown_text, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    print(f"Saving Markdown to {output_path}...")

if __name__ == "__main__":
    test_md = "# Introduction\nThis is a test.\n## Chapter 1\nContent goes here."
    generate_pdf(test_md, "test_book.pdf")
