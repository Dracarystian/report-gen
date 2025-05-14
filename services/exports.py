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
    """Guarda el informe en formato LaTeX."""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Plantilla LaTeX básica
    latex_template = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{booktabs}

\title{%s}
\author{Report Generator AI}
\date{\today}

\begin{document}

\maketitle
\tableofcontents

%s

\end{document}
"""
    
    # Convertir Markdown a LaTeX básico
    def md_to_latex(text):
        # Reemplazar encabezados
        text = re.sub(r'# (.*)', r'\\section{\1}', text)
        text = re.sub(r'## (.*)', r'\\subsection{\1}', text)
        text = re.sub(r'### (.*)', r'\\subsubsection{\1}', text)
        
        # Reemplazar énfasis
        text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
        
        return text
    
    # Extraer título
    lines = content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Informe"
    
    # Convertir contenido
    latex_content = md_to_latex(content)
    
    # Generar documento completo
    latex_doc = latex_template % (title, latex_content)
    
    # Guardar archivo
    output_file = f"{reports_dir}/{filename_base}.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_doc)
    
    return output_file