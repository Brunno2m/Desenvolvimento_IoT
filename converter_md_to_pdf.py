#!/usr/bin/env python3
"""
Conversor de Markdown para PDF
Converte todos os arquivos de documentação para PDF
"""

import os
import subprocess
import sys
from pathlib import Path

# Lista de arquivos a converter
MARKDOWN_FILES = [
    "INDEX_AVALIACAO.md",
    "RESUMO_EXECUTIVO.md",
    "AVALIACAO_FRONTEND_DJANGO.md",
    "MELHORIAS_FRONTEND_DJANGO.md",
    "ARQUITETURA_TECNICA.md",
    "STATUS_BOARD.md",
]

def convert_md_to_pdf(md_file):
    """Converte arquivo markdown para PDF usando weasyprint + markdown2"""
    
    pdf_file = md_file.replace(".md", ".pdf")
    
    print(f"📝 Convertendo: {md_file} → {pdf_file}")
    
    try:
        # Opção 1: Tentar com markdown2pdf (mais simples)
        cmd = [
            "python3", "-c",
            f"""
import markdown
import weasyprint
from pathlib import Path

# Ler arquivo markdown
with open('{md_file}', 'r', encoding='utf-8') as f:
    md_content = f.read()

# Converter markdown para HTML
html_content = markdown.markdown(
    md_content,
    extensions=['extra', 'codehilite', 'toc']
)

# Envolver em HTML básico
html_page = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 2cm;
            background-color: white;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 28px;
            page-break-after: avoid;
        }}
        h2 {{
            border-left: 4px solid #3498db;
            padding-left: 10px;
            font-size: 22px;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 18px;
            page-break-after: avoid;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            border-left: 3px solid #3498db;
            padding: 10px;
            overflow-x: auto;
            border-radius: 5px;
        }}
        blockquote {{
            border-left: 4px solid #bdc3c7;
            padding-left: 15px;
            color: #666;
            margin: 20px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        table, th, td {{
            border: 1px solid #bdc3c7;
        }}
        th {{
            background-color: #ecf0f1;
            padding: 10px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 8px 10px;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 5px 0;
        }}
        .toc {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        @media print {{
            body {{
                margin: 0;
                padding: 1cm;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            table {{
                page-break-inside: avoid;
            }}
            code {{
                word-break: break-all;
            }}
        }}
    </style>
</head>
<body>
    {{html_content}}
</body>
</html>'''

# Converter HTML para PDF
weasyprint.HTML(string=html_page).write_pdf('{pdf_file}')
print(f'✅ Convertido com sucesso: {pdf_file}')
"""
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao converter {md_file}: {e}")
        return False


def main():
    """Função principal"""
    
    print("=" * 70)
    print("📄 CONVERSOR DE MARKDOWN PARA PDF")
    print("=" * 70)
    print()
    
    # Verificar diretório
    base_dir = Path("/workspaces/Desenvolvimento_IoT")
    os.chdir(base_dir)
    
    # Instalar markdown se não estiver
    try:
        import markdown
    except ImportError:
        print("📥 Instalando markdown...")
        subprocess.run([sys.executable, "-m", "pip", "install", "markdown"], 
                      capture_output=True, check=True)
    
    success_count = 0
    failed_count = 0
    
    for md_file in MARKDOWN_FILES:
        if Path(md_file).exists():
            if convert_md_to_pdf(md_file):
                success_count += 1
            else:
                failed_count += 1
        else:
            print(f"⚠️  Arquivo não encontrado: {md_file}")
            failed_count += 1
    
    print()
    print("=" * 70)
    print(f"✅ Conversão concluída!")
    print(f"   Sucesso: {success_count}/{len(MARKDOWN_FILES)}")
    if failed_count > 0:
        print(f"   Falhas: {failed_count}/{len(MARKDOWN_FILES)}")
    print("=" * 70)
    print()
    
    # Listar PDFs gerados
    print("📋 Arquivos PDF gerados:")
    for md_file in MARKDOWN_FILES:
        pdf_file = md_file.replace(".md", ".pdf")
        if Path(pdf_file).exists():
            size = Path(pdf_file).stat().st_size / 1024  # KB
            print(f"   ✅ {pdf_file} ({size:.1f} KB)")
        else:
            print(f"   ❌ {pdf_file} (não encontrado)")


if __name__ == "__main__":
    main()
