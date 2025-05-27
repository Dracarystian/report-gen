import os
from fpdf import FPDF
import re

class APA_PDF(FPDF):
    def header(self):
        self.set_margins(25.4, 25.4, 25.4)
        self.set_font("Times", "B", 12)
        if hasattr(self, 'apa_title') and self.page_no() == 1:
            self.cell(0, 10, self.apa_title, ln=True, align="C")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 10)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def handle_title(pdf, line, i):
    title = line.replace("# ", "").strip()
    pdf.apa_title = title
    if i != 0:
        pdf.set_font("Times", "B", 16)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(5)
    pdf.set_font("Times", size=12)

def handle_subtitle(pdf, line, *_):
    subtitle = line.replace("## ", "").strip()
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 8, subtitle, ln=True)
    pdf.ln(2)
    pdf.set_font("Times", size=12)

def handle_subsubtitle(pdf, line, *_):
    subsubtitle = line.replace("### ", "").strip()
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 7, subsubtitle, ln=True)
    pdf.set_font("Times", size=12)

def handle_bold(pdf, line, *_):
    bold_text = line.replace("**", "")
    pdf.set_font("Times", "B", 12)
    pdf.multi_cell(0, 7, bold_text)
    pdf.set_font("Times", size=12)

def handle_list(pdf, line, *_):
    pdf.cell(5)
    pdf.multi_cell(0, 7, "- " + line[2:])

def handle_default(pdf, line, *_):
    if "**" in line:
        parts = re.split(r'(\*\*.*?\*\*)', line)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                pdf.set_font("Times", "B", 12)
                pdf.write(7, part[2:-2])
                pdf.set_font("Times", size=12)
            else:
                pdf.write(7, part)
        pdf.ln(7)
    else:
        pdf.multi_cell(0, 7, line)

def save_pdf_report(content, filename_base):
    """Guarda el informe en formato PDF siguiendo normas APA básicas."""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    pdf = APA_PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25.4)
    pdf.set_font("Times", size=12)
    pdf.apa_title = ""

    handlers = {
        "# ": handle_title,
        "## ": handle_subtitle,
        "### ": handle_subsubtitle,
        "**": handle_bold,
        "- ": handle_list
    }

    lines = content.split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue

        # Switch-like logic
        for prefix, handler in handlers.items():
            if line.startswith(prefix):
                handler(pdf, line, i)
                break
        else:
            handle_default(pdf, line, i)

    output_file = f"{reports_dir}/{filename_base}.pdf"
    pdf.output(output_file)
    return output_file