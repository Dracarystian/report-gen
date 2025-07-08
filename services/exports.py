import os
import re
from datetime import datetime

def save_report(content, report_type, format="md"):
    """Guarda el informe generado en un archivo Markdown."""
    # Crear directorio de informes si no existe
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Crear nombre de archivo con fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{reports_dir}/{report_type}_report_{timestamp}.{format}"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename

def convert_report(content, output_format, filename_base):
    """Convierte el informe al formato seleccionado."""
    # Diccionario de funciones de conversión por formato
    format_handlers = {
        "md": save_markdown_report,
        "pdf": save_pdf_report,
        "excel": save_excel_report,
        "latex": save_latex_report
    }
    
    # Seleccionar el manejador correcto (o usar markdown por defecto)
    handler = format_handlers.get(output_format, format_handlers["md"])
    
    # Ejecutar el manejador seleccionado
    return handler(content, filename_base)

def save_markdown_report(content, filename_base):
    """Guarda el informe en formato Markdown."""
    return save_report(content, filename_base, "md")

def save_pdf_report(content, filename_base):
    """Guarda el informe en formato PDF."""
    try:
        from fpdf import FPDF
    except ImportError:
        print("⚠️ La biblioteca fpdf no está instalada. Instálala con: pip install fpdf")
        return save_markdown_report(content, filename_base)
        
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    pdf = FPDF()
    pdf.add_page()
    
    # Extraer título
    lines = content.split("\n")
    title = lines[0].replace("#", "").strip() if lines else "Informe"
    
    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    
    # Procesar el contenido
    pdf.set_font("Arial", size=12)
    for line in lines[1:]:
        if not line.strip():
            pdf.ln(5)
        elif line.startswith("##"):
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, line.replace("#", "").strip(), ln=True)
            pdf.set_font("Arial", size=12)
        elif line.startswith("#"):
            pdf.set_font("Arial", "B", 15)
            pdf.cell(0, 10, line.replace("#", "").strip(), ln=True)
            pdf.set_font("Arial", size=12)
        else:
            pdf.multi_cell(0, 5, line.strip())
    
    output_file = f"{reports_dir}/{filename_base}.pdf"
    pdf.output(output_file)
    return output_file

def save_excel_report(content, filename_base):
    """Guarda el informe en formato Excel."""
    try:
        import pandas as pd
    except ImportError:
        print("⚠️ La biblioteca pandas no está instalada. Instálala con: pip install pandas openpyxl")
        return save_markdown_report(content, filename_base)
        
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Extraer secciones del informe
    sections = re.split(r'#{1,3}\s+', content)[1:]
    section_titles = re.findall(r'#{1,3}\s+(.*)', content)
    
    # Preparar hojas para Excel
    sheets = {}
    
    # Intentar extraer tablas y estadísticas
    for i, (title, section) in enumerate(zip(section_titles, sections)):
        # Buscar datos tipo clave-valor
        data_dict = {}
        for line in section.split("\n"):
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().strip("-").strip()
                    value = parts[1].strip()
                    data_dict[key] = value
        
        if data_dict:
            sheets[f"Sección {i+1}: {title[:20]}"] = pd.DataFrame(list(data_dict.items()),
                                                             columns=['Dato', 'Valor'])
    
    # Si no encontramos datos estructurados, crear una hoja simple con todo el contenido
    if not sheets:
        sheets["Informe Completo"] = pd.DataFrame([content], columns=["Contenido"])
    
    # Guardar en Excel
    output_file = f"{reports_dir}/{filename_base}.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output_file


def save_latex_report(content, filename_base):
    """Guarda el informe en formato Presentación LaTeX (beamer)."""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    latex_template = r"""
\documentclass{beamer}
\usetheme{Madrid}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\title{%s}
\author{Report Generator AI}
\date{\today}

\begin{document}

\frame{\titlepage}

%s

\end{document}
"""

    def escape_latex(text):
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
        }
        for key, val in replacements.items():
            text = text.replace(key, val)
        return text

    def md_table_to_latex(table_lines):
        headers = [escape_latex(h.strip()) for h in table_lines[0].split("|") if h.strip()]
        rows = [l for l in table_lines[1:] if l.strip()]
        latex = ["\\begin{tabular}{%s}" % ("l" * len(headers))]
        latex.append("\\toprule")
        latex.append(" & ".join(headers) + " \\\\")
        latex.append("\\midrule")
        for row in rows:
            cols = [escape_latex(c.strip()) for c in row.split("|") if c.strip()]
            latex.append(" & ".join(cols) + " \\\\")
        latex.append("\\bottomrule")
        latex.append("\\end{tabular}")
        return "\n".join(latex)

    def handle_slide_title(slide_content, line):
        return escape_latex(line[2:].strip()), []

    def handle_subtitle(slide_content, line):
        slide_content.append("\\textbf{%s}\\\\[1ex]" % escape_latex(line[3:].strip()))
        return None, slide_content

    def handle_subsubtitle(slide_content, line):
        slide_content.append("\\textbf{\\small %s}\\\\[0.5ex]" % escape_latex(line[4:].strip()))
        return None, slide_content

    def handle_list(slide_content, line, lines_iter):
        slide_content.append("\\begin{itemize}")
        slide_content.append("\\item %s" % apply_formatting(line[2:].strip()))
        for next_line in lines_iter:
            if next_line.strip().startswith("- "):
                slide_content.append("\\item %s" % apply_formatting(next_line.strip()[2:]))
            else:
                lines_iter.pushback(next_line)
                break
        slide_content.append("\\end{itemize}")
        return None, slide_content

    def handle_table(slide_content, line, table_lines, lines_iter):
        table_lines.append(line)
        for next_line in lines_iter:
            if "|" in next_line and "---" not in next_line:
                table_lines.append(next_line)
            else:
                lines_iter.pushback(next_line)
                break
        slide_content.append(md_table_to_latex(table_lines))
        table_lines.clear()
        return None, slide_content

    def apply_formatting(text):
        text = escape_latex(text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
        return text

    def handle_bold_italic(slide_content, line):
        slide_content.append(apply_formatting(line) + "\\\\")
        return None, slide_content

    class PushbackIterator:
        def __init__(self, iterable):
            self.iterable = iter(iterable)
            self.buffer = []

        def __iter__(self):
            return self

        def __next__(self):
            if self.buffer:
                return self.buffer.pop()
            return next(self.iterable)

        def pushback(self, value):
            self.buffer.append(value)

    def md_to_beamer_slides(text):
        slides = []
        lines = text.split('\n')
        slide_content = []
        slide_title = None
        table_lines = []

        handlers = [
            (lambda l: l.startswith("# "), handle_slide_title),
            (lambda l: l.startswith("## "), handle_subtitle),
            (lambda l: l.startswith("### "), handle_subsubtitle),
            (lambda l: l.startswith("- "), handle_list),
            (lambda l: "|" in l and "---" not in l, handle_table),
            (lambda l: True, handle_bold_italic)
        ]

        def flush_slide():
            nonlocal slide_title, slide_content
            if slide_title or slide_content:
                slides.append("\\begin{frame}{%s}\n%s\n\\end{frame}" % (
                    slide_title if slide_title else "",
                    "\n".join(slide_content)
                ))
                slide_title = None
                slide_content = []

        lines_iter = PushbackIterator(lines)
        for line in lines_iter:
            line = line.strip()
            if not line:
                continue
            for cond, handler in handlers:
                if cond(line):
                    if handler == handle_slide_title:
                        flush_slide()
                        slide_title, slide_content = handler(slide_content, line)
                    elif handler == handle_list:
                        _, slide_content = handler(slide_content, line, lines_iter)
                    elif handler == handle_table:
                        _, slide_content = handler(slide_content, line, table_lines, lines_iter)
                    else:
                        _, slide_content = handler(slide_content, line)
                    break

        flush_slide()
        return "\n".join(slides)

    # Extraer título
    lines = content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Presentación"

    # Convertir contenido a slides beamer
    latex_content = md_to_beamer_slides(content)

    # Generar documento completo
    latex_doc = latex_template % (escape_latex(title), latex_content)

    # Guardar archivo
    output_file = f"{reports_dir}/{filename_base}.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_doc)

    return output_file