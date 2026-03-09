from fpdf import FPDF
from fpdf.enums import XPos, YPos
import re
import os

class BookPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load bundled Unicode fonts for Uzbek support
        font_dir = os.path.join(os.path.dirname(__file__), "fonts")
        
        self.main_font = "DejaVu"
        
        try:
            # Add all four styles for full support
            self.add_font("DejaVu", "", os.path.join(font_dir, "DejaVuSans.ttf"))
            self.add_font("DejaVu", "B", os.path.join(font_dir, "DejaVuSans-Bold.ttf"))
            self.add_font("DejaVu", "I", os.path.join(font_dir, "DejaVuSans-Oblique.ttf"))
            self.add_font("DejaVu", "BI", os.path.join(font_dir, "DejaVuSans-BoldOblique.ttf"))
        except Exception as e:
            print(f"Warning: Could not load Unicode fonts: {e}. Falling back to Arial.")
            self.main_font = "Arial"

    def header(self):
        self.set_font(self.main_font, 'B', 12)
        self.cell(0, 10, 'Compiled Telegram Book', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font(self.main_font, 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

def clean_text(text):
    """
    Strict cleaning for PDF output: removes HTML, Markdown markers, and excessive noise.
    """
    if not text:
        return ""
    # 1. Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # 2. Remove Markdown bold/italic markers
    text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    # 3. Clean up smart quotes and special dashes that might cause issues in some viewers
    text = text.replace('‘', "'").replace('’', "'").replace('“', '"').replace('”', '"')
    # 4. Remove any remaining weird anchor patterns like [id]
    text = re.sub(r'\[\d+\]', '', text)
    
    return text.strip()

def generate_pdf(markdown_text, output_path):
    """
    Improved PDF generation using fpdf2 with Unicode support.
    """
    pdf = BookPDF()
    # Increase margins to prevent border overlap (L, T, R)
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font(pdf.main_font, size=11) # Slightly smaller font for better fit
    
    epw = pdf.epw
    
    lines = markdown_text.split('\n')
    for line in lines:
        raw_line = line.strip()
        if not raw_line:
            pdf.ln(4) # Reduced space for better density
            continue
            
        # 1. Main Headings
        if raw_line.startswith('# '):
            text = clean_text(raw_line[2:])
            pdf.set_font(pdf.main_font, 'B', 16)
            pdf.multi_cell(0, 10, text, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(4)
            pdf.set_font(pdf.main_font, size=11)
            
        # 2. Sub Headings
        elif raw_line.startswith('## '):
            text = clean_text(raw_line[3:])
            pdf.set_font(pdf.main_font, 'B', 14)
            pdf.multi_cell(0, 8, text, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
            pdf.set_font(pdf.main_font, size=11)
            
        elif raw_line.startswith('### '):
            text = clean_text(raw_line[4:])
            pdf.set_font(pdf.main_font, 'B', 12)
            pdf.multi_cell(0, 7, text, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
            pdf.set_font(pdf.main_font, size=11)
            
        # 3. List Items (Standardizing)
        elif raw_line.startswith(('* ', '- ', '• ')):
            text = "• " + clean_text(raw_line[2:])
            pdf.multi_cell(0, 7, text, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
        elif re.match(r'^\d+\.', raw_line):
            text = clean_text(raw_line)
            pdf.multi_cell(0, 7, text, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
        # 4. Standard Paragraphs
        else:
            text = clean_text(raw_line)
            if text:
                # Use multi_cell with width 0 (fill to right margin) and explicit resets
                pdf.multi_cell(0, 7, text, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    print(f"Saving PDF to {output_path}...")
    pdf.output(output_path)

def save_markdown(markdown_text, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)
    print(f"Saving Markdown to {output_path}...")

if __name__ == "__main__":
    test_md = "# Introduction\nThis is a test.\n## Chapter 1\nContent goes here."
    generate_pdf(test_md, "test_book.pdf")
