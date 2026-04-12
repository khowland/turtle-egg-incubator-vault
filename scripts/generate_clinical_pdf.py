import os
from fpdf import FPDF
from pathlib import Path

# Paths (§v9.0.2)
ROOT_DIR = Path(__file__).parent.parent
MD_PATH = ROOT_DIR / "docs" / "user" / "OPERATOR_MANUAL.md"
OUTPUT_PATH = ROOT_DIR / "docs" / "user" / "WINC_OPERATOR_MANUAL_v10_1.pdf"

class ClinicalPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'WINC Clinical CIOS Reference Manual v10.1.0 (The Resilient Edition)', 0, 0, 'L')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_emojis(text):
    # Standard WINC cleanup for Unicode compatibility
    return text.encode('ascii', 'ignore').decode('ascii').strip()

def create_manual_pdf():
    pdf = ClinicalPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        
        # 1. Handle Page Breaks
        if '<div style="page-break-after: always;"></div>' in line:
            pdf.add_page()
            continue

        # 2. Handle Headings
        if line.startswith('# '):
            pdf.set_font('helvetica', 'B', 18)
            pdf.set_text_color(16, 185, 129) # WINC Green
            pdf.multi_cell(0, 10, clean_emojis(line[2:]))
            pdf.ln(5)
        elif line.startswith('## '):
            pdf.set_font('helvetica', 'B', 14)
            pdf.set_text_color(31, 41, 55)
            pdf.multi_cell(0, 10, clean_emojis(line[3:]))
            pdf.ln(2)
        elif line.startswith('### '):
            pdf.set_font('helvetica', 'B', 12)
            pdf.set_text_color(55, 65, 81)
            pdf.multi_cell(0, 8, clean_emojis(line[4:]))
            pdf.ln(2)
        
        # 3. Handle Images
        elif '![' in line and '](' in line:
            try:
                # Extract path
                start = line.find('](') + 2
                end = line.find(')', start)
                img_rel_path = line[start:end]
                
                # Resolve path
                clean_path = img_rel_path.replace("../../", "").replace("../", "")
                img_path = ROOT_DIR / clean_path
                
                if img_path.exists():
                    pdf.image(str(img_path), w=160)
                    pdf.ln(5)
            except:
                pass

        # 4. Handle Tables (Basic support)
        elif '|' in line and '---' not in line:
            pdf.set_font('helvetica', '', 9)
            pdf.set_text_color(0, 0, 0)
            cells = [clean_emojis(c.strip()) for c in line.split('|') if c.strip()]
            if cells:
                for c in cells:
                    pdf.cell(40, 7, c[:20], 1)
                pdf.ln()

        # 5. Handle Standard Text
        elif line and not line.startswith('---'):
            pdf.set_font('helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            # Remove MD formatting for PDF
            clean_text = line.replace('**', '').replace('__', '').replace('>', '').replace('`', '')
            pdf.multi_cell(0, 6, clean_emojis(clean_text))
            pdf.ln(1)

    pdf.output(str(OUTPUT_PATH))
    print(f"✅ Clinical PDF generated: {OUTPUT_PATH}")

if __name__ == "__main__":
    create_manual_pdf()
