import os
import re
from fpdf import FPDF
import markdown2
from bs4 import BeautifulSoup

def clean_text(text):
    # Remove emojis and other non-latin1 characters for basic FPDF support
    return text.encode('ascii', 'ignore').decode('ascii')

class ClinicalManualPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'WINC Sovereign Clinical Incubator System | Operator Manual v10.5.1', border=False, align='L', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def generate_pdf(md_path, pdf_path):
    print(f"Reading {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert MD to HTML for easier parsing
    html = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])
    soup = BeautifulSoup(html, 'html.parser')

    pdf = ClinicalManualPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. Page 1: Artistic Cover Page
    pdf.add_page()
    cover_path = os.path.join(os.getcwd(), "assets", "manual", "operators_manual_cover_page.png")
    if os.path.exists(cover_path):
        pdf.image(cover_path, x=0, y=0, w=210, h=297) # Full page bleed
    else:
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(0, 10, "[Cover Image Placeholder]", align='C')

    # 2. Page 2: Technical Title Page
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 24)
    pdf.ln(80)
    pdf.cell(0, 20, "WINC Incubator System", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 16)
    pdf.cell(0, 10, "Operator's Guide and Clinical Protocol", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font('helvetica', 'I', 12)
    pdf.cell(0, 10, "Release v10.5.1 | Institutional Edition", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.add_page()
    
    # Content
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'table', 'blockquote', 'hr']):
        text = clean_text(element.get_text())
        if element.name == 'h1':
            pdf.ln(10)
            pdf.set_font('helvetica', 'B', 18)
            pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
        elif element.name == 'h2':
            pdf.ln(5)
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        elif element.name == 'h3':
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        elif element.name == 'p':
            pdf.set_font('helvetica', '', 11)
            # Handle images in p tags
            img = element.find('img')
            if img:
                src = img.get('src')
                # Resolve relative path
                img_path = os.path.join(os.path.dirname(md_path), src.replace('/', os.sep))
                if os.path.exists(img_path):
                    try:
                        pdf.image(img_path, w=170)
                        pdf.ln(5)
                    except:
                        pdf.set_text_color(200, 0, 0)
                        pdf.cell(0, 10, f"[Image Error: {src}]", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_text_color(0, 0, 0)
                else:
                    pdf.set_text_color(200, 0, 0)
                    pdf.cell(0, 10, f"[Missing Image: {src}]", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(0, 0, 0)
            else:
                pdf.multi_cell(0, 6, text)
                pdf.ln(3)
        elif element.name == 'li':
            pdf.set_x(20)
            pdf.set_font('helvetica', '', 11)
            pdf.multi_cell(0, 6, f"- {text}") 
            pdf.ln(2)
        elif element.name == 'blockquote':
            pdf.set_font('helvetica', 'I', 10)
            pdf.set_text_color(100, 100, 100)
            pdf.set_x(25)
            pdf.multi_cell(0, 5, text.strip())
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
        elif element.name == 'hr':
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

    print(f"Saving PDF to {pdf_path}...")
    pdf.output(pdf_path)
    print("PDF Generated Successfully.")

if __name__ == "__main__":
    base_dir = '.'
    md = os.path.join(base_dir, 'docs', 'user', 'OPERATOR_MANUAL.md')
    pdf_out = os.path.join(base_dir, 'docs', 'user', 'OPERATOR_MANUAL_v10_5_1.pdf')
    generate_pdf(md, pdf_out)
