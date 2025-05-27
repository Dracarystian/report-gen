import os
import re

def save_latex_report(content, filename_base):
    """Guarda el informe en formato LaTeX."""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

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

    def md_to_latex(text):
        text = re.sub(r'# (.*)', r'\\section{\1}', text)
        text = re.sub(r'## (.*)', r'\\subsection{\1}', text)
        text = re.sub(r'### (.*)', r'\\subsubsection{\1}', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
        return text

    lines = content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Informe"
    latex_content = md_to_latex(content)
    latex_doc = latex_template % (title, latex_content)

    output_file = f"{reports_dir}/{filename_base}.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_doc)
    return output_file