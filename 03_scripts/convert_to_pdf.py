import sys
import subprocess
import tempfile
import os
from pathlib import Path
import mistune

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
]

def find_edge():
    for p in EDGE_PATHS:
        if os.path.exists(p):
            return p
    return "msedge"

CSS_TEMPLATE = """
@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {
        content: counter(page);
    }
}

body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 10pt;
    margin: 0;
    padding: 0;
}

h1 {
    color: #0a2540;
    font-size: 20pt;
    font-weight: 700;
    border-bottom: 2.5px solid #0a2540;
    padding-bottom: 6px;
    margin-top: 0;
    margin-bottom: 18px;
    page-break-after: avoid;
}

h2 {
    color: #0a2540;
    font-size: 14pt;
    font-weight: 600;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 24px;
    margin-bottom: 12px;
    page-break-after: avoid;
}

h3 {
    color: #1e3a8a;
    font-size: 11.5pt;
    font-weight: 600;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
}

h4 {
    color: #334155;
    font-size: 10.5pt;
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 6px;
    page-break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 10px;
    text-align: justify;
}

ul, ol {
    margin-top: 0;
    margin-bottom: 10px;
    padding-left: 22px;
}

li {
    margin-bottom: 4px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0 18px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
}

th {
    background-color: #0a2540;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 7px 9px;
    border: 1px solid #0a2540;
}

td {
    padding: 6px 9px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f8fafc;
}

blockquote {
    border-left: 4px solid #0284c7;
    background-color: #f0f9ff;
    padding: 10px 14px;
    margin: 14px 0;
    color: #0c4a6e;
    border-radius: 0 4px 4px 0;
    page-break-inside: avoid;
}

blockquote p {
    margin-bottom: 0;
}

code {
    font-family: Consolas, 'Courier New', monospace;
    font-size: 8.5pt;
    background-color: #f1f5f9;
    padding: 2px 4px;
    border-radius: 3px;
    color: #0f172a;
}

pre {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 10px 14px;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 8pt;
    line-height: 1.45;
    page-break-inside: avoid;
}

pre code {
    background-color: transparent;
    padding: 0;
    color: #1e293b;
}

hr {
    border: 0;
    height: 1px;
    background: #cbd5e1;
    margin: 20px 0;
}

.report-header {
    text-align: right;
    font-size: 8pt;
    color: #64748b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    margin-bottom: 18px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
"""

def convert_md_to_pdf(md_file: Path, pdf_file: Path):
    print(f"Reading: {md_file}")
    content = md_file.read_text(encoding='utf-8')
    
    md_parser = mistune.create_markdown(plugins=['table', 'strikethrough'])
    html_body = md_parser(content)
    
    title = md_file.stem.replace('_', ' ').title()
    full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        {CSS_TEMPLATE}
    </style>
</head>
<body>
    <div class="report-header">Банк ВТБ (ПАО) &bull; Changellenge &gt;&gt; Cup Moscow 2026 &bull; Аналитические материалы</div>
    {html_body}
</body>
</html>
"""
    
    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    temp_html = pdf_file.with_suffix('.temp.html')
    temp_html.write_text(full_html, encoding='utf-8')
    
    edge_exe = find_edge()
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(pdf_file.resolve())}",
        f"file:///{str(temp_html.resolve()).replace(os.sep, '/')}"
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully generated: {pdf_file} ({pdf_file.stat().st_size} bytes)")
    finally:
        if temp_html.exists():
            temp_html.unlink()

def main():
    root = Path(__file__).resolve().parent.parent
    research_dir = root / "02_research"
    
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if not target.is_absolute():
            target = root / target
        pdf_target = target.with_suffix('.pdf')
        if target.exists():
            convert_md_to_pdf(target, pdf_target)
        else:
            print(f"Error: File not found: {target}")
        return

    files_to_convert = [
        (research_dir / "foreign_banks_antifraud.md", research_dir / "foreign_banks_antifraud.pdf"),
        (research_dir / "vtb_fraud_statistics.md", research_dir / "vtb_fraud_statistics.pdf"),
        (research_dir / "Правовой_анализ_161-ФЗ_ВТБ.md", research_dir / "Правовой_анализ_161-ФЗ_ВТБ.pdf"),
        (research_dir / "антифрод_модель_втб_кратко.md", research_dir / "антифрод_модель_втб_кратко.pdf"),
        (research_dir / "vtb_current_antifraud_practices.md", research_dir / "vtb_current_antifraud_practices.pdf"),
        (research_dir / "финансовая_модель_втб_защита_4_уровня.md", research_dir / "финансовая_модель_втб_защита_4_уровня.pdf")
    ]
    
    for md_path, pdf_path in files_to_convert:
        if md_path.exists():
            convert_md_to_pdf(md_path, pdf_path)
        else:
            print(f"Warning: File not found: {md_path}")

if __name__ == '__main__':
    main()
