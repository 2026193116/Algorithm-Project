import os
import re
import markdown
from playwright.sync_api import sync_playwright

INPUT_MD = "REPORT.md"
CSS_FILE = "style.css"
OUTPUT_PDF = "report.pdf"
SVG_WIDTH = "85%"  # SVG 가로 크기 조절 (예: "70%", "85%", "500px")


def find_svg_file(rel_path: str, base_dir: str) -> str | None:
    # 1) 현재 폴더 기준 상대 경로 확인
    cand1 = os.path.abspath(os.path.join(base_dir, rel_path))
    if os.path.exists(cand1):
        return cand1

    # 2) 파일명만으로 현재 폴더 및 상위/하위 폴더에서 검색
    fname = os.path.basename(rel_path)
    search_roots = [base_dir, os.path.abspath(os.path.join(base_dir, ".."))]
    for root_dir in search_roots:
        for dirpath, _, filenames in os.walk(root_dir):
            if fname in filenames:
                return os.path.join(dirpath, fname)
    return None


def main():
    base_dir = os.path.abspath(".")
    with open(INPUT_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    # 수식 보호 (Markdown 변환 시 _ 나 \ 가 망가지지 않도록 임시 치환)
    math_blocks = []

    def save_block_math(m):
        math_blocks.append(f'<div class="math-block">$${m.group(1)}$$</div>')
        return f"\x00MATHBLOCK{len(math_blocks)-1}\x00"

    def save_inline_math(m):
        math_blocks.append(f'<span class="math-inline">${m.group(1)}$</span>')
        return f"\x00MATHINLINE{len(math_blocks)-1}\x00"

    md_text = re.sub(r"\$\$([\s\S]+?)\$\$", save_block_math, md_text)
    md_text = re.sub(r"(?<!\$)\$(?!\$)([^\n$]+?)(?<!\$)\$(?!\$)", save_inline_math, md_text)

    # SVG 이미지를 찾아 <svg> 코드로 직접 삽입
    svg_holders = []

    def embed_svg(match):
        alt = match.group(1)
        rel_path = match.group(2)
        svg_path = find_svg_file(rel_path, base_dir)
        if svg_path and svg_path.lower().endswith(".svg"):
            with open(svg_path, "r", encoding="utf-8") as sf:
                svg_content = sf.read()
            # XML 선언 제거
            svg_content = re.sub(r"<\?xml[^>]*\?>", "", svg_content).strip()
            html_snippet = (
                f'<figure class="svg-figure" style="width: {SVG_WIDTH};">'
                f"{svg_content}"
                f"<figcaption>{alt}</figcaption>"
                f"</figure>"
            )
        else:
            print(f"[경고] 파일을 찾지 못함: {rel_path}")
            html_snippet = f'<p style="color:red;">[이미지 누락: {rel_path}]</p>'

        svg_holders.append(html_snippet)
        return f"\x00SVGHOLDER{len(svg_holders)-1}\x00"

    md_text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", embed_svg, md_text)

    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code"],
    )

    for i, item in enumerate(svg_holders):
        body_html = body_html.replace(f"\x00SVGHOLDER{i}\x00", item)
    for i, item in enumerate(math_blocks):
        body_html = body_html.replace(f"\x00MATHBLOCK{i}\x00", item)
        body_html = body_html.replace(f"\x00MATHINLINE{i}\x00", item)

    with open(CSS_FILE, "r", encoding="utf-8") as f:
        css_text = f.read()

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<script>
window.MathJax = {{
  tex: {{ inlineMath: [['$', '$']], displayMath: [['$$', '$$']] }},
  svg: {{ fontCache: 'global' }}
}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
{css_text}
.svg-figure {{
  margin: 16px auto;
  text-align: center;
  break-inside: avoid;
}}
.svg-figure svg {{
  width: 100% !important;
  height: auto !important;
  display: block;
}}
.svg-figure figcaption {{
  font-size: 0.85em;
  color: #57606a;
  margin-top: 6px;
}}
.math-block {{
  margin: 12px 0;
  text-align: center;
  break-inside: avoid;
}}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(full_html, wait_until="networkidle")
        page.evaluate("() => window.MathJax && MathJax.typesetPromise ? MathJax.typesetPromise() : Promise.resolve()")
        page.pdf(path=OUTPUT_PDF, format="A4", print_background=True)
        browser.close()

    print(f"생성 완료: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
