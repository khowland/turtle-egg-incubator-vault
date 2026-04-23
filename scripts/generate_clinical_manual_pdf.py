
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
        self.styles.add(ParagraphStyle(name='H1', parent=self.styles['Heading1'], fontSize=24, leading=30, spaceAfter=20, fontName='Helvetica-Bold', keepWithNext=True))
        self.styles.add(ParagraphStyle(name='H2', parent=self.styles['Heading2'], fontSize=18, leading=22, spaceBefore=25, spaceAfter=15, fontName='Helvetica-Bold', keepWithNext=True))
        self.styles.add(ParagraphStyle(name='H3', parent=self.styles['Heading3'], fontSize=14, leading=18, spaceBefore=15, spaceAfter=8, fontName='Helvetica-Bold', keepWithNext=True))
        self.styles.add(ParagraphStyle(name='InternalText', parent=self.styles['Normal'], fontSize=11, leading=16, spaceAfter=12, fontName='Helvetica'))
        self.styles.add(ParagraphStyle(name='FigureCaption', parent=self.styles['Normal'], fontSize=9, leading=12, alignment=TA_CENTER, fontName='Helvetica-Oblique', spaceBefore=4, spaceAfter=18, textColor=colors.grey))
        self.styles.add(ParagraphStyle(name='InstitutionalBullet', parent=self.styles['Normal'], fontSize=11, leading=16, leftIndent=20, firstLineIndent=-10, spaceAfter=8, fontName='Helvetica'))
        self.styles.add(ParagraphStyle(name='CentredTitle', parent=self.styles['Normal'], fontSize=28, leading=40, alignment=TA_CENTER, fontName='Helvetica-Bold'))

    def header_footer(self, canvas, doc):
        canvas.saveState()
        if doc.page > 2:
            canvas.setFont('Helvetica-Bold', 8)
            canvas.setStrokeColor(colors.lightgrey)
            canvas.line(10*mm, 280*mm, 200*mm, 280*mm)
            canvas.setFillColor(colors.grey)
            canvas.drawRightString(200*mm, 282*mm, "WINC CLINICAL INCUBATOR SYSTEM | v10.6.0")
            canvas.setFont('Helvetica-Oblique', 8)
            canvas.drawCentredString(105*mm, 10*mm, f"Institutional Archive: 2026-SEASON-VOL | Page {doc.page} | Kevin Howland")
        canvas.restoreState()

    def add_alert_box(self, text, alert_type='NOTE'):
        color_map = {'NOTE': colors.HexColor('#E6F0FF'), 'IMPORTANT': colors.HexColor('#FFE6E6'), 'CAUTION': colors.HexColor('#FFFBE6')}
        border_map = {'NOTE': colors.HexColor('#0064FF'), 'IMPORTANT': colors.red, 'CAUTION': colors.HexColor('#FFC800')}
        data = [[Paragraph(f"<b>{alert_type}</b>: {text}", self.styles['InternalText'])]]
        t = Table(data, colWidths=[170*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), color_map.get(alert_type, colors.white)),
            ('BOX', (0,0), (-1,-1), 1, border_map.get(alert_type, colors.black)),
            ('TOPPADDING', (0,0), (-1,-1), 4*mm),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4*mm),
            ('LEFTPADDING', (0,0), (-1,-1), 5*mm),
            ('RIGHTPADDING', (0,0), (-1,-1), 5*mm),
        ]))
        return t

    def compile(self, md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        html = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Front Matter: Title and TOC
        self.elements.append(Spacer(1, 80*mm))
        self.elements.append(Paragraph("WINC Incubator System", self.styles['CentredTitle']))
        self.elements.append(Paragraph("Operator's Guide and Clinical Protocol", self.styles['H2']))
        self.elements.append(Spacer(1, 80*mm))
        self.elements.append(Paragraph("Release v10.6.0 | Institutional Edition", self.styles['H3']))
        self.elements.append(PageBreak())
        
        self.elements.append(Paragraph("Table of Contents", self.styles['H1']))
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(name='TOCL1', fontSize=12, leading=16, fontName='Helvetica-Bold', spaceBefore=10),
            ParagraphStyle(name='TOCL2', fontSize=10, leading=14, fontName='Helvetica', leftIndent=10)
        ]
        self.elements.append(toc)
        # Content-driven page breaks within the loop will handle the rest

        # 2. Advanced Section Assembly Logic
        # Goal: Prevent Orphans (Headings separated from content)
        # Goal: Glue Figures to Captions
        
        raw_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'table', 'hr'])
        
        idx = 0
        self.first_img_skipped = False
        last_was_pagebreak = False
        
        while idx < len(raw_elements):
            element = raw_elements[idx]
            tag = element.name
            text = clean_text(element.get_text().strip())
            
            # --- HEADING LOGIC (ORPHAN CONTROL) ---
            if tag in ['h1', 'h2', 'h3']:
                # Bond the heading to the next 2 paragraphs/items to prevent the heading being at the bottom of a page
                cluster = []
                # Handle H1/H2 Page Breaks
                if tag in ['h1', 'h2']:
                    if idx > 0 and not last_was_pagebreak:
                        self.elements.append(PageBreak())
                        last_was_pagebreak = True
                
                # Add the heading itself
                style = self.styles['H1'] if tag == 'h1' else (self.styles['H2'] if tag == 'h2' else self.styles['H3'])
                cluster.append(Paragraph(text, style))
                
                # Look ahead and "glue" the next 2 major items if they exist
                lookahead_limit = 2
                internal_idx = idx + 1
                while lookahead_limit > 0 and internal_idx < len(raw_elements):
                    next_el = raw_elements[internal_idx]
                    if next_el.name in ['h1', 'h2', 'h3'] or next_el.name == 'hr': break # Don't glue to next heading/break
                    
                    # Process and add to cluster
                    p_obj = self._process_element(next_el, md_path)
                    if p_obj:
                        cluster.append(p_obj)
                        lookahead_limit -= 1
                    internal_idx += 1
                
                self.elements.append(KeepTogether(cluster))
                idx = internal_idx
                last_was_pagebreak = False
                continue

            # --- MANUAL PAGE BREAK (HR) ---
            elif tag == 'hr':
                if idx > 0 and not last_was_pagebreak:
                    self.elements.append(PageBreak())
                    last_was_pagebreak = True
                idx += 1
                continue

            # --- STANDALONE PARAGRAPH / FIGURE LOGIC ---
            else:
                p_obj = self._process_element(element, md_path)
                if p_obj:
                    last_was_pagebreak = False
                    # Check if this is an image. If so, look ahead for a caption.
                    if isinstance(p_obj, Image) and idx + 1 < len(raw_elements):
                        next_el = raw_elements[idx+1]
                        next_text = clean_text(next_el.get_text().strip())
                        # If next element is italics (likely a caption), glue them together
                        if (next_el.name == 'p' and next_el.find('em')) or (next_text.startswith('Figure')):
                            caption_para = Paragraph(next_text, self.styles['FigureCaption'])
                            self.elements.append(KeepTogether([p_obj, caption_para]))
                            idx += 2 # Skip the caption in the next iteration
                            continue
                    
                    self.elements.append(p_obj)
                idx += 1

        # Final Render
        doc = InstitutionalDoc(self.output_path, pagesize=A4, title="WINC Operator Manual", author="Kevin Howland")
        cover_frame = Frame(0, 0, 210*mm, 297*mm, id='cover_frame', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        content_frame = Frame(20*mm, 20*mm, 170*mm, 257*mm, id='content_frame')
        
        def draw_cover(canvas, doc):
            # Full-page cover background image
            cover_path = os.path.join(os.getcwd(), "assets", "manual", "operators_manual_cover_page.png")
            if os.path.exists(cover_path):
                canvas.drawImage(cover_path, 0, 0, width=210*mm, height=297*mm, preserveAspectRatio=False, mask='auto')
            # WINC Logo — superimposed top-left corner of cover page
            # Logo: assets/winc-logo2.jpg 360x91px RGBA, displayed at 50mm wide
            # CR-20260423: Added to match sidebar and HTML cover page branding
            logo_path = os.path.join(os.getcwd(), "assets", "winc-logo2.jpg")
            if os.path.exists(logo_path):
                logo_w = 50*mm
                logo_h = logo_w * (91 / 360)  # preserve aspect ratio
                canvas.drawImage(logo_path, 15*mm, 297*mm - 15*mm - logo_h,
                                 width=logo_w, height=logo_h, mask='auto')
        doc.addPageTemplates([
            PageTemplate(id='Cover', frames=cover_frame, onPage=draw_cover), 
            PageTemplate(id='Later', frames=content_frame, onPage=self.header_footer)
        ])
        doc.multiBuild([PageBreak('Later')] + self.elements)

    def _process_element(self, element, md_path):
        """Helper to convert BS4 element to ReportLab flowable."""
        # Extract text and icons separately
        img_tag = element.find('img')
        # Remove the img tag from the element so we can get just the remaining text
        if img_tag:
            img_src = img_tag.get('src')
            img_tag.decompose()
        else:
            img_src = None
            
        text = clean_text(element.get_text().strip())
        
        # --- IMAGE + TEXT BUNDLING LOGIC ---
        if img_src:
            img_path = os.path.join(os.path.dirname(md_path), img_src.replace('/', os.sep))
            is_icon = 'egg_s' in img_src or 'icon' in img_src.lower()
            
            # Skip cover image in content stream
            if not self.first_img_skipped:
                self.first_img_skipped = True
                return None

            img_flowable = None
            if os.path.exists(img_path):
                try:
                    from PIL import Image as PILImage
                    with PILImage.open(img_path) as pimg:
                        w, h = pimg.size
                        aspect = h / float(w)
                        target_w = 8*mm if is_icon else 160*mm
                        target_h = target_w * aspect
                        if not is_icon and target_h > 150*mm:
                            target_h = 150*mm
                            target_w = target_h / aspect
                        img_flowable = Image(img_path, width=target_w, height=target_h)
                except Exception as e:
                    print(f"ERROR: Image processing failed: {e}")
            
            if not img_flowable:
                img_flowable = Paragraph("⚠️", self.styles['InternalText'])

            # If it's an icon-bullet (inside <li> or has text), use a 2-column Table
            if is_icon and (element.name == 'li' or text):
                data = [[img_flowable, Paragraph(text, self.styles['InstitutionalBullet' if element.name=='li' else 'InternalText'])]]
                t = Table(data, colWidths=[12*mm, 158*mm])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2*mm),
                ]))
                return t
            
            # Otherwise, just return the standalone image (like a Figure)
            return img_flowable

        # --- PLAIN TEXT LOGIC ---
        if element.name == 'p':
            if any(alert in text for alert in ['**NOTE**', 'NOTE:', '📘']): 
                return self.add_alert_box(text.replace('**NOTE**', '').replace('NOTE:', '').replace('📘', '').strip(), 'NOTE')
            if any(alert in text for alert in ['**IMPORTANT**', 'IMPORTANT:', '🛑']): 
                return self.add_alert_box(text.replace('**IMPORTANT**', '').replace('IMPORTANT:', '').replace('🛑', '').strip(), 'IMPORTANT')
            if any(alert in text for alert in ['**CAUTION**', 'CAUTION:', '⚠️']): 
                return self.add_alert_box(text.replace('**CAUTION**', '').replace('CAUTION:', '').replace('⚠️', '').strip(), 'CAUTION')
            return Paragraph(text, self.styles['InternalText'])
            
        elif element.name == 'li':
            return Paragraph(f"&bull; {text}", self.styles['InstitutionalBullet'])
        
        elif element.name == 'table':
            # Basic Table Logic
            rows = element.find_all('tr')
            table_data = []
            for row in rows:
                cols = row.find_all(['td', 'th'])
                table_data.append([Paragraph(clean_text(c.get_text()), self.styles['InternalText']) for c in cols])
            if table_data:
                t = Table(table_data, colWidths=[175*mm / len(table_data[0])] * len(table_data[0]))
                t.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('TOPPADDING', (0,0), (-1,-1), 2*mm),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2*mm),
                ]))
                return t
        return None

if __name__ == "__main__":
    compiler = InstitutionalCompiler('./docs/user/OPERATOR_MANUAL_v10_6_0.pdf')
    compiler.compile('./docs/user/OPERATOR_MANUAL.md')
    print("ReportLab Adaptive Block Manual Compiled.")
