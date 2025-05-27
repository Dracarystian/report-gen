import os

def save_markdown_report(content, filename_base):
    """Guarda el informe en formato Markdown."""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    output_file = f"{reports_dir}/{filename_base}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    return output_file