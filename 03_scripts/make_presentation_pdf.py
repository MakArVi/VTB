import mistune
import subprocess
import os
from pathlib import Path

def generate_pdf():
    root = Path(__file__).resolve().parent.parent
    md_path = root / '01_presentation' / 'Презентация_ВТБ_Защита_Уровни_Безопасности.md'
    pdf_path = root / '01_presentation' / 'Презентация_ВТБ_Защита_Уровни_Безопасности.pdf'

    content = md_path.read_text(encoding='utf-8')
    md_parser = mistune.create_markdown(plugins=['table', 'strikethrough'])
    html_body = md_parser(content)

    css = """
    @page {
        size: A4 landscape;
        margin: 12mm 15mm 12mm 15mm;
        @bottom-right {
            content: counter(page);
        }
    }

    body {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        color: #1e293b;
        line-height: 1.45;
        font-size: 10pt;
        margin: 0;
        padding: 0;
    }

    h1 {
        display: none;
    }

    h2 {
        color: #0a2540;
        font-size: 16pt;
        font-weight: 700;
        border-bottom: 2.5px solid #0091ff;
        padding-bottom: 5px;
        margin-top: 0;
        margin-bottom: 10px;
        page-break-before: always;
    }

    h2:first-of-type {
        page-break-before: avoid;
    }

    h3 {
        color: #0f172a;
        font-size: 11pt;
        font-weight: 600;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    blockquote {
        border-left: 4.5px solid #0091ff;
        background: #f0f7ff;
        padding: 8px 14px;
        margin: 8px 0 12px 0;
        color: #0c4a6e;
        border-radius: 0 4px 4px 0;
        font-size: 10.5pt;
    }

    blockquote h3 {
        color: #0369a1;
        margin: 0;
        font-size: 10.5pt;
        line-height: 1.4;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 9pt;
    }

    th {
        background-color: #0a2540;
        color: #ffffff;
        font-weight: 600;
        text-align: left;
        padding: 7px 10px;
        border: 1px solid #0a2540;
    }

    td {
        padding: 6px 10px;
        border: 1px solid #cbd5e1;
        vertical-align: top;
    }

    tr:nth-child(even) {
        background-color: #f8fafc;
    }

    pre {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 8px 12px;
        border-radius: 6px;
        font-family: Consolas, monospace;
        font-size: 8.5pt;
        line-height: 1.35;
        margin: 8px 0;
    }

    ul, ol {
        margin-top: 4px;
        margin-bottom: 8px;
        padding-left: 20px;
    }

    li {
        margin-bottom: 3px;
    }

    .report-header {
        display: flex;
        justify-content: space-between;
        font-size: 8pt;
        color: #64748b;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 4px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    """

    full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Презентация решения: ВТБ Защита</title>
    <style>{css}</style>
</head>
<body>
    <div class="report-header">
        <span>БАНК ВТБ (ПАО) &bull; CHANGELLENGE &gt;&gt; CUP MOSCOW 2026</span>
        <span>РЕШЕНИЕ: «ДЕНЬГИ ПОД ЗАЩИТОЙ»</span>
    </div>
    {html_body}
</body>
</html>"""

    temp_html = pdf_path.with_suffix('.temp.html')
    temp_html.write_text(full_html, encoding='utf-8')

    edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    cmd = [
        edge_exe,
        '--headless=new',
        '--disable-gpu',
        '--no-pdf-header-footer',
        f'--print-to-pdf={str(pdf_path.resolve())}',
        f'file:///{str(temp_html.resolve()).replace(os.sep, "/")}'
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully created: {pdf_path.resolve()} ({pdf_path.stat().st_size} bytes)")
    finally:
        if temp_html.exists():
            temp_html.unlink()

if __name__ == '__main__':
    generate_pdf()
