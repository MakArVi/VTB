import re
import os
import sys

def clean_latex_string(s: str) -> str:
    # Repeatedly handle nested \text{} and \mathbf{}
    for _ in range(3):
        s = re.sub(r'\\text\{([^}]+)\}', r'\1', s)
        s = re.sub(r'\\mathbf\{([^}]+)\}', r'**\1**', s)
        s = re.sub(r'\\mathit\{([^}]+)\}', r'*\1*', s)
        s = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1 / \2)', s)
    
    # Mathematical symbols
    s = s.replace(r'\times', '×')
    s = s.replace(r'\approx', '≈')
    s = s.replace(r'\implies', '→')
    s = s.replace(r'\le', '≤')
    s = s.replace(r'\ge', '≥')
    s = s.replace(r'\Delta', 'Δ')
    s = s.replace(r'\,', ' ')
    s = s.replace(r'\%', '%')
    s = s.replace(r'\ ', ' ')
    
    # Subscripts and powers
    s = re.sub(r'_\{([^}]+)\}', r'_\1', s)
    s = re.sub(r'\^\{([^}]+)\}', r'^\1', s)
    s = s.replace('^2', '²').replace('^3', '³')
    s = s.replace(r'\sum_{t=1}^{12}', 'Σ(t=1..12)')
    s = s.replace(r'\sum_{t=1}^3', 'Σ(t=1..3)')
    
    # Clean leftover LaTeX escapes
    s = s.replace(r'\{', '{').replace(r'\}', '}')
    s = s.replace(r'\$', '$')
    
    # Remove math mode delimiters
    s = s.replace('$$', '')
    
    # Inline single dollar signs (ensure not actual currency like $50M)
    # If $ appears around math like $500 000 \times ...$
    # Replace $...$ with the inner text
    s = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', r'\1', s)
    
    # Cleanup extra spaces
    s = re.sub(r' +', ' ', s)
    return s.strip()

def process_file(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. First process display math blocks: $$ ... $$
    def replace_block_math(match):
        raw = match.group(1)
        cleaned = clean_latex_string(raw)
        return f"\n> **Расчет:** {cleaned}\n"

    content = re.sub(r'\$\$\s*(.+?)\s*\$\$', replace_block_math, content, flags=re.DOTALL)

    # 2. Process inline math: $ ... $
    def replace_inline_math(match):
        raw = match.group(1)
        # Avoid replacing actual currency like $1.5M or $50
        if re.match(r'^\d+(\.\d+)?[kKM]?$', raw):
            return f"${raw}"
        cleaned = clean_latex_string(raw)
        return cleaned

    content = re.sub(r'(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)', replace_inline_math, content)

    # 3. Clean any remaining standalone LaTeX commands
    content = content.replace(r'\times', '×')
    content = content.replace(r'\approx', '≈')
    content = content.replace(r'\implies', '→')
    content = content.replace(r'\le', '≤')
    content = content.replace(r'\ge', '≥')
    content = content.replace(r'\%', '%')
    content = re.sub(r'\\text\{([^}]+)\}', r'\1', content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")
    else:
        print(f"No changes needed: {filepath}")

def main():
    targets = [
        "02_research/04_financial_model/финансовая_модель_втб_защита_4_уровня.md",
        "02_research/03_solution_and_tech/единое_комплексное_решение_втб_защита.md",
        "02_research/03_solution_and_tech/экономика_внедрения_втб_защита.md",
        "02_research/03_solution_and_tech/детализация_уровней_втб_защита_матрица.md",
        "02_research/03_solution_and_tech/технические_заметки_втб_защита.md",
        "02_research/01_as_is_vtb/vtb_fraud_statistics.md",
        "01_presentation/Презентация_ВТБ_Защита_Уровни_Безопасности.md"
    ]
    for t in targets:
        if os.path.exists(t):
            process_file(t)

if __name__ == '__main__':
    main()
