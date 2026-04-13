import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus.tableofcontents import TableOfContents
import markdown2
from bs4 import BeautifulSoup

def clean_text(text):
    return text.encode('ascii', 'ignore').decode('ascii')

class InstitutionalDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 1
        BaseDocTemplate.__init__(self, filename, **kw)
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'H1': self.notify('TOCEntry', (0, text, self.page))
            elif style == 'H2': self.notify('TOCEntry', (1, text, self.page))

class InstitutionalCompiler:
    def __init__(self, output_path):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self.elements = []
        
    def _setup_styles(self):
        self.styles.add(ParagraphStyle(name='H1', parent=self.styles['Heading1'], fontSize=24, leading=30, spaceAfter=20, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='H2', parent=self.styles['Heading2'], fontSize=18, leading=22, spaceBefore=20, spaceAfter=15, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='H3', parent=self.styles['Heading3'], fontSize=14, leading=18, spaceBefore=15, spaceAfter=10, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='InternalText', parent=self.styles['Normal'], fontSize=11, leading=14, spaceAfter=10, fontName='Helvetica'))
        self.styles.add(ParagraphStyle(name='InstitutionalBullet', parent=self.styles['Normal'], fontSize=11, leading=14, leftIndent=20, firstLineIndent=-10, spaceAfter=5, fontName='Helvetica'))
        self.styles.add(ParagraphStyle(name='CentredTitle', parent=self.styles['Normal'], fontSize=28, leading=40, alignment=TA_CENTER, fontName='Helvetica-Bold'))

    def header_footer(self, canvas, doc):
        canvas.saveState()
        if doc.page > 2:
            canvas.setFont('Helvetica-Bold', 8)
            canvas.setStrokeColor(colors.lightgrey)
            canvas.line(10*mm, 280*mm, 200*mm, 280*mm)
            canvas.setFillColor(colors.grey)
            canvas.drawRightString(200*mm, 282*mm, "WINC CLINICAL INCUBATOR SYSTEM | v10.5.1")
            canvas.setFont('Helvetica-Oblique', 8)
            canvas.drawCentredString(105*mm, 10*mm, f"Institutional Archive: 2026-SEASON-VOL | Page {doc.page}")
        canvas.restoreState()

    def add_alert_box(self, text, alert_type='NOTE'):
        color_map = {'NOTE': colors.HexColor('#E6F0FF'), 'IMPORTANT': colors.HexColor('#FFE6E6'), 'CAUTION': colors.HexColor('#FFFBE6')}
        border_map = {'NOTE': colors.HexColor('#0064FF'), 'IMPORTANT': colors.red, 'CAUTION': colors.HexColor('#FFC800')}
        data = [[Paragraph(f"<b>{alert_type}</b>: {text}", self.styles['InternalText'])]]
        t = Table(data, colWidths=[170*mm])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), color_map.get(alert_type, colors.white)), ('BOX', (0,0), (-1,-1), 1, border_map.get(alert_type, colors.black)), ('PADDING', (0,0), (-1,-1), 5*mm)]))
        return t

    def compile(self, md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        html = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])
        soup = BeautifulSoup(html, 'html.parser')
        raw_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])

        # Title and TOC remain same
        self.elements.append(Spacer(1, 80*mm))
        self.elements.append(Paragraph("WINC Incubator System", self.styles['CentredTitle']))
        self.elements.append(Paragraph("Operator's Guide and Clinical Protocol", self.styles['H2']))
        self.elements.append(Spacer(1, 80*mm)); self.elements.append(Paragraph("Release v10.5.1 | Institutional Edition", self.styles['H3']))
        self.elements.append(PageBreak())
        self.elements.append(Paragraph("Table of Contents", self.styles['H1']))
        toc = TableOfContents()
        toc.levelStyles = [ParagraphStyle(name='TOCL1', fontSize=12, leading=16, fontName='Helvetica-Bold'), ParagraphStyle(name='TOCL2', fontSize=10, leading=14, fontName='Helvetica', leftIndent=10)]
        self.elements.append(toc); self.elements.append(PageBreak())

        # --- SMART SECTION AGGREGATION ---
        is_emergency = False
        first_img_skipped = False
        first_heading_processed = False
        current_block = []
        
        def flush_block(elements_list, target_list, emergency=False):
            if elements_list:
                if emergency:
                    # Wrap the entire emergency block in a Thick Red Box
                    data = [[KeepTogether(elements_list)]]
                    t = Table(data, colWidths=[175*mm])
                    t.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 3, colors.red),
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF5F5')),
                        ('PADDING', (0,0), (-1,-1), 10*mm),
                    ]))
                    target_list.append(t)
                else:
                    total_len = sum(len(str(e)) for e in elements_list)
                    if total_len < 3000:
                        target_list.append(KeepTogether(elements_list))
                    else:
                        target_list.extend(elements_list)

        for element in raw_elements:
            text = clean_text(element.get_text().strip())
            if not text and not element.find('img'): continue
            
            p_obj = None
            if element.name in ['h1', 'h2']:
                flush_block(current_block, self.elements, emergency=is_emergency)
                current_block = []
                is_emergency = "🆘" in text
                if first_heading_processed: self.elements.append(PageBreak())
                first_heading_processed = True
                self.elements.append(Paragraph(text, self.styles['H1'] if element.name == 'h1' else self.styles['H2']))
                continue
                
            # H3 Subheadings trigger a block flush but NOT necessarily a PageBreak (unless it starts at the end)
            elif element.name == 'h3':
                flush_block(current_block, self.elements)
                current_block = [Paragraph(text, self.styles['H3'])]
                continue

            elif element.name == 'p':
                img = element.find('img')
                if img:
                    if not first_img_skipped: first_img_skipped = True; continue
                    src = img.get('src')
                    img_path = os.path.join(os.path.dirname(md_path), src.replace('/', os.sep))
                    if os.path.exists(img_path):
                        p_obj = Image(img_path, width=150*mm, height=100*mm, kind='proportional')
                else:
                    if '**NOTE**' in text or 'NOTE:' in text: p_obj = self.add_alert_box(text.replace('**NOTE**', '').replace('NOTE:', '').replace('📘', '').strip(), 'NOTE')
                    elif '**IMPORTANT**' in text or 'IMPORTANT:' in text: p_obj = self.add_alert_box(text.replace('**IMPORTANT**', '').replace('IMPORTANT:', '').replace('🛑', '').strip(), 'IMPORTANT')
                    elif '**CAUTION**' in text or 'CAUTION:' in text: p_obj = self.add_alert_box(text.replace('**CAUTION**', '').replace('CAUTION:', '').replace('⚠️', '').strip(), 'CAUTION')
                    else: p_obj = Paragraph(text, self.styles['InternalText'])
            elif element.name == 'li':
                p_obj = Paragraph(f"&bull; {text}", self.styles['InstitutionalBullet'])

            if p_obj:
                current_block.append(p_obj)
        
        flush_block(current_block, self.elements, emergency=is_emergency) # Final flush

        doc = InstitutionalDoc(self.output_path, pagesize=A4)
        cover_frame = Frame(0, 0, 210*mm, 297*mm, id='cover_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        content_frame = Frame(20*mm, 20*mm, 170*mm, 257*mm, id='content_frame')
        def draw_cover(canvas, doc):
            cover_path = os.path.join(os.getcwd(), "assets", "manual", "operators_manual_cover_page_optimized.png")
            if os.path.exists(cover_path): canvas.drawImage(cover_path, 0, 0, width=210*mm, height=297*mm)
        doc.addPageTemplates([PageTemplate(id='Cover', frames=cover_frame, onPage=draw_cover), PageTemplate(id='Later', frames=content_frame, onPage=self.header_footer)])
        doc.multiBuild([PageBreak('Later')] + self.elements)

if __name__ == "__main__":
    compiler = InstitutionalCompiler('./docs/user/OPERATOR_MANUAL_v10_5_1.pdf')
    compiler.compile('./docs/user/OPERATOR_MANUAL.md')
    print("ReportLab Adaptive Block Manual Compiled.")
