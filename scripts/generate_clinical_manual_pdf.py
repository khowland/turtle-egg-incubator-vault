import os
import re
from fpdf import FPDF
import markdown2
from bs4 import BeautifulSoup

def clean_text(text):
    return text.encode('ascii', 'ignore').decode('ascii')

class ClinicalManualPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toc_entries = [] # List of (level, text, page)

    def header(self):
        if self.page_no() > 2: # Skip header on cover and title pages
            self.set_font('helvetica', 'B', 8)
            self.set_text_color(180, 180, 180)
            self.cell(0, 10, 'WINC SOVEREIGN CLINICAL INCUBATOR SYSTEM | RELEASE v10.5.1', border=False, align='R', new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(220, 220, 220)
            self.line(10, 18, 200, 18)
            self.ln(5)

    def footer(self):
        if self.page_no() > 2:
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f'Institutional Archive: 2026-SEASON-VOL | Page {self.page_no()}', align='C')

    def add_toc_entry(self, level, text, page):
        self.toc_entries.append((level, text, page))

    def render_toc(self):
        self.add_page()
        self.set_font('helvetica', 'B', 20)
        self.cell(0, 20, "Table of Contents", align='L', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_font('helvetica', '', 11)
        for level, text, page in self.toc_entries:
            actual_page = page + 1
            indent = (level - 1) * 10
            self.set_x(10 + indent)
            title = text or "Section"
            if level == 1:
                self.set_font('helvetica', 'B', 11)
            else:
                self.set_font('helvetica', '', 11)
            
            w_title = self.get_string_width(title)
            w_page = self.get_string_width(str(actual_page)) + 5
            dots_count = int((190 - indent - w_title - w_page) / (self.get_string_width(".") or 1))
            leader = "." * max(0, dots_count - 2)
            self.cell(0, 7, f"{title} {leader} {actual_page}", new_x="LMARGIN", new_y="NEXT")
        
    def alert_box(self, text, type='NOTE'):
        colors = {
            'NOTE': (230, 240, 255, 0, 100, 255),
            'IMPORTANT': (255, 230, 230, 255, 0, 0),
            'CAUTION': (255, 250, 230, 255, 200, 0)
        }
        bg_r, bg_g, bg_b, b_r, b_g, b_b = colors.get(type, colors['NOTE'])
        self.set_fill_color(bg_r, bg_g, bg_b)
        self.set_draw_color(b_r, b_g, b_b)
        self.set_line_width(0.5)
        self.set_x(15)
        self.multi_cell(180, 6, f"{type}: {text}", border=1, fill=True, align='L')
        self.ln(5)
        self.set_line_width(0.2)

    def get_block_height(self, text, width=180, line_height=7):
        # Estimate height of multi_cell block
        lines = self.multi_cell(width, line_height, text, dry_run=True, output="LINES")
        return len(lines) * line_height

def process_element(pdf, element, first_img_skipped, md_path, capture_toc=False):
    text = clean_text(element.get_text().strip())
    if not text and element.name != 'hr' and not element.find('img'): return first_img_skipped

    # --- CONTINUITY CHECK ---
    # We never want to start a heading or a paragraph if it triggers a lonely orphan line
    remaining_space = 270 - pdf.get_y() # Total usable height roughly 270mm

    if element.name == 'h1':
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 22)
        pdf.cell(0, 15, text, new_x="LMARGIN", new_y="NEXT")
        if capture_toc: pdf.add_toc_entry(1, text, pdf.page_no())
        pdf.ln(5)
    elif element.name == 'h2':
        if pdf.get_y() > 140:
            pdf.add_page()
        else:
            pdf.set_draw_color(240, 240, 240)
            pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
            pdf.ln(10)
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        if capture_toc: pdf.add_toc_entry(2, text, pdf.page_no())
        pdf.ln(2)
    elif element.name == 'h3':
        if pdf.get_y() > 160:
            pdf.add_page()
        else:
            pdf.ln(5)
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
    elif element.name == 'p':
        pdf.set_font('helvetica', '', 11)
        img = element.find('img')
        if img:
            if not first_img_skipped: return True
            src = img.get('src')
            img_path = os.path.join(os.path.dirname(md_path), src.replace('/', os.sep))
            if os.path.exists(img_path):
                if pdf.get_y() > 200: pdf.add_page()
                pdf.image(img_path, w=150, x=30)
                pdf.ln(5)
        else:
            # Atomic Block Check: Dry run to prevent orphans
            est_h = pdf.get_block_height(text, width=180, line_height=7)
            if est_h > (remaining_space - 10): # 10mm buffer
                pdf.add_page()
            
            if '**NOTE**' in text or 'NOTE:' in text:
                pdf.alert_box(text.replace('**NOTE**', '').replace('NOTE:', '').replace('📘', '').strip(), 'NOTE')
            elif '**IMPORTANT**' in text or 'IMPORTANT:' in text:
                pdf.alert_box(text.replace('**IMPORTANT**', '').replace('IMPORTANT:', '').replace('🛑', '').strip(), 'IMPORTANT')
            elif '**CAUTION**' in text or 'CAUTION:' in text:
                pdf.alert_box(text.replace('**CAUTION**', '').replace('CAUTION:', '').replace('⚠️', '').strip(), 'CAUTION')
            else:
                pdf.multi_cell(0, 7, text)
                pdf.ln(3)
    elif element.name == 'li':
        pdf.set_x(20)
        pdf.set_font('helvetica', '', 11)
        est_h = pdf.get_block_height(f"- {text}", width=170, line_height=7)
        if est_h > (remaining_space - 5):
            pdf.add_page()
        pdf.multi_cell(0, 7, f"- {text}") 
        pdf.ln(1)
    elif element.name == 'hr':
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    return first_img_skipped

def generate_pdf(md_path, pdf_path):
    print(f"Institutional Compiler: Reading {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    html = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'table', 'blockquote', 'hr'])

    # PASS 1: MAP
    pdf = ClinicalManualPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page(); pdf.add_page()
    skipped = False
    for el in elements: skipped = process_element(pdf, el, skipped, md_path, capture_toc=True)

    # PASS 2: BUILD
    final_pdf = ClinicalManualPDF()
    final_pdf.toc_entries = pdf.toc_entries
    final_pdf.add_page()
    cover_path = os.path.join(os.getcwd(), "assets", "manual", "operators_manual_cover_page.png")
    if os.path.exists(cover_path): final_pdf.image(cover_path, x=0, y=0, w=210, h=297)
    final_pdf.add_page()
    final_pdf.set_font('helvetica', 'B', 28); final_pdf.ln(80)
    final_pdf.cell(0, 20, "WINC Incubator System", align='C', new_x="LMARGIN", new_y="NEXT")
    final_pdf.set_font('helvetica', '', 18)
    final_pdf.cell(0, 10, "Operator's Guide and Clinical Protocol", align='C', new_x="LMARGIN", new_y="NEXT")
    final_pdf.ln(90); final_pdf.set_font('helvetica', '', 10)
    final_pdf.cell(0, 10, "Copyright 2026 Wisconsin Incubator Network Consortium. All Rights Reserved.", align='C')
    final_pdf.render_toc()
    skipped = False
    for el in elements: skipped = process_element(final_pdf, el, skipped, md_path, capture_toc=False)

    print(f"Institutional Compiler: Saving PDF to {pdf_path}...")
    final_pdf.output(pdf_path)
    print("Institutional Manual v10.5.1 Compiled Successfully.")

if __name__ == "__main__":
    generate_pdf('./docs/user/OPERATOR_MANUAL.md', './docs/user/OPERATOR_MANUAL_v10_5_1.pdf')
