import os
import re
import markdown
from playwright.sync_api import sync_playwright

INPUT_MD = "REPORT.md"
CSS_FILE = "style.css"
OUTPUT_PDF = "report.pdf"


def main():
    with open(INPUT_MD, "r", encoding="utf-8") as f:
        md_text = f.read()

    base_dir = os.path.abspath(".")

    def replace_img(match):
        alt = match.group(1)
        rel_path = match.group(2)
        abs_path = os.path.abspath(os.path.join(base_dir, rel_path))
        return f'<img src="file://{abs_path}" alt="{alt}">'

    md_with_abs_imgs = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_img, md_text)
    body_html = markdown.markdown(
        md_with_abs_imgs,
        extensions=["tables", "fenced_code"],
    )

    with open(CSS_FILE, "r", encoding="utf-8") as f:
        css_text = f.read()

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<style>
{css_text}
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
        page.pdf(path=OUTPUT_PDF, format="A4", print_background=True)
        browser.close()

    print(f"생성 완료: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
