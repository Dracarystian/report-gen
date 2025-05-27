import os
import re

def save_excel_report(content, filename_base):
    """Guarda el informe en formato Excel."""
    try:
        import pandas as pd
    except ImportError:
        print("⚠️ La biblioteca pandas no está instalada. Instálala con: pip install pandas openpyxl")
        return None

    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    # Extraer secciones del informe
    sections = re.split(r'#{1,3}\s+', content)[1:]
    section_titles = re.findall(r'#{1,3}\s+(.*)', content)

    sheets = {}
    for i, (title, section) in enumerate(zip(section_titles, sections)):
        data_dict = {}
        for line in section.split("\n"):
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().strip("-").strip()
                    value = parts[1].strip()
                    data_dict[key] = value
        if data_dict:
            sheets[f"Sección {i+1}: {title[:20]}"] = pd.DataFrame(list(data_dict.items()), columns=['Dato', 'Valor'])

    if not sheets:
        sheets["Informe Completo"] = pd.DataFrame([content], columns=["Contenido"])

    output_file = f"{reports_dir}/{filename_base}.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output_file