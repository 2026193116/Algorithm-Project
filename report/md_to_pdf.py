import os
import re
import markdown
from playwright.sync_api import sync_playwright

INPUT_MD = "REPORT.md"
OUTPUT_PDF = "report.pdf"

# ================= [여기서 크기 조절] =================
SVG_WIDTH = "42%"       # 기존 85%의 절반 수준 (원하는 비율로 조절)
BODY_FONT_PT = 9.5      # 기존 10.5pt에서 1pt 축소
H1_FONT_PT = 18.0       # 기존 19pt에서 1pt 축소
H2_FONT_PT = 13.5       # 기존 14.5pt에서 1pt 축소
H3_FONT_PT = 11.0       # 기존 12pt에서 1pt 축소
TABLE_FONT_PT = 8.0     # 기존 9pt에서 1pt 축소
CAPTION_FONT_PT = 7.5   # 캡션 글씨 크기
PAGE_MARGIN = "15mm"
# ======================================================


def find_svg_file(rel_path: str, base_dir: str):
    cand1 = os.path.abspath(os.path.join(base_dir, rel_path))
    if os.path.exists(cand1):
        return cand1

    fname = os.path.basename(rel_path)
    search_roots = [base_dir, os.path.abspath(os.path.join(base_dir, ".."))]
    for root_dir in search_roots:
        for dirpath, _, filenames in os.walk(root_dir):
            if fname in filenames:
                return os.path.join(dirpath, fname)
    return None


def clean_svg_dimensions(svg_text: str) -> str:
    svg_text = re.sub(r"<\?xml[^>]*\?>", "", svg_text).strip()

    def strip_wh(m):
        tag = m.group(0)
        # viewBox가 있을 때만 고정 width/height를 제거해 CSS width가 정확히 적용되게 함
        if "viewBox=" in tag:
            tag = re.sub(r'\s+(width|height)="[^"]*"', "", tag)
        return tag

    return re.sub(r"<svg\b[^>]*>", strip_wh, svg_text, count=1)


def main():
    base_dir = os.path.abspath(".")
    with open(INPUT_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    math_blocks = []

    def save_block_math(m):
        math_blocks.append(f'<div class="math-block">$${m.group(1)}$$</div>')
        return f"\x00MATHBLOCK{len(math_blocks)-1}\x00"

    def save_inline_math(m):
        math_blocks.append(f'<span class="math-inline">${m.group(1)}$</span>')
        return f"\x00MATHINLINE{len(math_blocks)-1}\x00"

    md_text = re.sub(r"\$\$([\s\S]+?)\$\$", save_block_math, md_text)
    md_text = re.sub(r"(?<!\$)\$(?!\$)([^\n$]+?)(?<!\$)\$(?!\$)", save_inline_math, md_text)

    svg_holders = []

    def embed_svg(match):
        alt = match.group(1)
        rel_path = match.group(2)
        svg_path = find_svg_file(rel_path, base_dir)
        if svg_path and svg_path.lower().endswith(".svg"):
            with open(svg_path, "r", encoding="utf-8") as sf:
                svg_content = clean_svg_dimensions(sf.read())
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
@page {{
  size: A4;
  margin: {PAGE_MARGIN};
}}
body {{
  font-family: "Noto Sans CJK KR", "Noto Sans KR", sans-serif;
  font-size: {BODY_FONT_PT}pt;
  line-height: 1.55;
  color: #1e242b;
}}
h1 {{ font-size: {H1_FONT_PT}pt; }}
h2 {{ font-size: {H2_FONT_PT}pt; }}
h3 {{ font-size: {H3_FONT_PT}pt; }}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: {TABLE_FONT_PT}pt;
  break-inside: avoid;
}}
th, td {{
  border: 1px solid #cbd5e1;
  padding: 5px 7px;
}}
.svg-figure {{
  margin: 12px auto;
  text-align: center;
  break-inside: avoid;
}}
.svg-figure svg {{
  width: 100% !important;
  height: auto !important;
  display: block;
}}
.svg-figure figcaption {{
  font-size: {CAPTION_FONT_PT}pt;
  color: #57606a;
  margin-top: 4px;
}}
.math-block {{
  margin: 10px 0;
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
