"""Build static HTML pages from content/*.md.

Usage: python build.py
Outputs: index.html, buoi-01.html .. buoi-08.html, ket-luan.html
"""
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
COURSE = "Cẩm nang xây dựng kênh YouTube tạo ra doanh thu cho doanh nghiệp"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&'
         'family=Lora:wght@500;600&display=swap&subset=vietnamese" rel="stylesheet">')
CALLOUTS = {"Ghi nhớ": "ghi-nho", "Lưu ý": "luu-y", "Ví dụ": "vi-du"}


def read(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    return meta, body


def slugify(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    table = str.maketrans("àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ",
                          "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd")
    s = s.translate(table)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def render(body):
    md = markdown.Markdown(extensions=["tables", "sane_lists"])
    out = md.convert(body)
    # headings: add ids, collect toc
    toc = []

    def h2(m):
        inner = m.group(1)
        sid = slugify(inner)
        toc.append((sid, re.sub(r"<[^>]+>", "", inner)))
        return f'<h2 id="{sid}">{inner}</h2>'
    out = re.sub(r"<h2>(.*?)</h2>", h2, out)
    out = re.sub(r"<h3>(.*?)</h3>", lambda m: f'<h3 id="{slugify(m.group(1))}">{m.group(1)}</h3>', out)
    # tables scroll wrapper
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

    # callouts
    def bq(m):
        inner = m.group(1)
        for label, cls in CALLOUTS.items():
            pat = rf"^\s*<p><strong>{label}</strong>\s*(<br\s*/?>)?\s*"
            if re.match(pat, inner):
                inner = re.sub(pat, f'<p><span class="callout-label">{label}</span>', inner, 1)
                return f'<blockquote class="callout-{cls}">{inner}</blockquote>'
        return f"<blockquote>{inner}</blockquote>"
    out = re.sub(r"<blockquote>(.*?)</blockquote>", bq, out, flags=re.S)
    return out, toc


def sections(html_body):
    """Split rendered html by h2 so special sections get custom markup."""
    parts = re.split(r'(?=<h2 id=")', html_body)
    return parts


def figure(key, caption):
    if not caption or not (ROOT / "assets" / "img" / f"{key}.webp").exists():
        return ""
    c = html.escape(caption)
    return (f'<figure class="illus"><img src="assets/img/{key}.webp" alt="{c}" width="1600" height="900" '
            f'loading="lazy" decoding="async"><figcaption>{c}</figcaption></figure>')


def enhance(html_body, page_key, caption=""):
    out = []
    for part in sections(html_body):
        title = re.search(r'<h2 id="[^"]*">(.*?)</h2>', part)
        t = title.group(1) if title else ""
        if t == "Mục tiêu buổi học":
            part = part.replace("<ul>", '<ul class="goals">', 1)
        elif t == "Tóm tắt 30 giây":
            part = part.replace("<blockquote>", '<blockquote class="callout-tom-tat">', 1)
            part += figure(page_key, caption)
        elif t == "Checklist áp dụng":
            idx = [0]

            def cb(m):
                idx[0] += 1
                return (f'<li><label><input type="checkbox" data-key="{page_key}-{idx[0]}">'
                        f'<span>{m.group(1)}</span></label></li>')
            part = re.sub(r"<li>\[ \]\s*(.*?)</li>", cb, part, flags=re.S)
            part = part.replace("<ul>", '<ul class="checklist">', 1)
            part += '<p class="progress-note">Tiến độ được lưu trên trình duyệt của bạn.</p>'
        elif t == "Câu hỏi tự kiểm tra":
            def qa(m):
                li = m.group(1)
                g = re.split(r"(?:<br\s*/?>|\n|<p>)\s*Gợi ý:\s*", li, maxsplit=1)
                if len(g) == 2:
                    q = re.sub(r"</?p>", "", g[0]).strip()
                    a = re.sub(r"</?p>", "", g[1]).strip()
                    return f"<li><p>{q}</p><details><summary>Xem gợi ý</summary><p>{a}</p></details></li>"
                return f"<li>{li}</li>"
            part = re.sub(r"<li>(.*?)</li>", qa, part, flags=re.S)
            part = part.replace("<ol>", '<ol class="quiz">', 1)
        out.append(part)
    return "".join(out)


def chapters_bar(current, lessons):
    items = []
    keys = ["index"] + [l["key"] for l in lessons] + ["ket-luan"]
    labels = ["Trang chủ"] + [f'Buổi {l["so"]}: {l["tieu_de"]}' for l in lessons] + ["Kết luận"]
    pos = keys.index(current)
    for i, (k, lab) in enumerate(zip(keys, labels)):
        cls = "current" if i == pos else ("done" if i < pos else "")
        items.append(f'<a href="{k}.html" class="{cls}" aria-label="{html.escape(lab)}"'
                     f'{" aria-current=page" if i == pos else ""}><span>{html.escape(lab)}</span></a>')
    return '<nav class="chapters" aria-label="Các buổi học">' + "".join(items) + "</nav>"


def page(title, desc, current, lessons, main_html, toc=None):
    toc_html = ""
    if toc:
        toc_html = ('<aside class="toc" aria-label="Mục lục"><h2>Trong buổi này</h2><ol>'
                    + "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in toc)
                    + "</ol></aside>")
    body = (f'<div class="layout">{toc_html}<main>{main_html}</main></div>' if toc
            else main_html)
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
{FONTS}
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top"><div class="top-inner">
<a class="brand" href="index.html"><span class="play" aria-hidden="true"></span>{COURSE}</a>
{chapters_bar(current, lessons)}
</div></header>
{body}
<footer>{COURSE}</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""


def main():
    lessons = []
    for f in sorted(CONTENT.glob("buoi-*.md")):
        meta, body = read(f)
        lessons.append({"key": f.stem, "so": int(meta.get("so", f.stem[-2:])), "tieu_de": meta["tieu_de"],
                        "mo_ta": meta.get("mo_ta", ""), "hinh": meta.get("hinh", ""), "body": body})
    lessons.sort(key=lambda l: l["so"])

    for i, l in enumerate(lessons):
        content, toc = render(l["body"])
        content = enhance(content, l["key"], l["hinh"])
        prev = lessons[i - 1] if i > 0 else None
        nxt = lessons[i + 1] if i + 1 < len(lessons) else None
        pager = '<nav class="pager" aria-label="Chuyển buổi">'
        pager += (f'<a class="prev" href="{prev["key"]}.html"><small>Buổi trước</small>Buổi {prev["so"]}: {html.escape(prev["tieu_de"])}</a>'
                  if prev else '<a class="prev" href="index.html"><small>Quay lại</small>Trang chủ</a>')
        pager += (f'<a class="next" href="{nxt["key"]}.html"><small>Buổi tiếp theo</small>Buổi {nxt["so"]}: {html.escape(nxt["tieu_de"])}</a>'
                  if nxt else '<a class="next" href="ket-luan.html"><small>Tiếp theo</small>Kết luận</a>')
        pager += "</nav>"
        head = (f'<div class="lesson-head"><p class="kicker"><span class="num">{l["so"]:02d}</span>Buổi {l["so"]} trên 8</p>'
                f'<h1>{html.escape(l["tieu_de"])}</h1><p class="lede">{html.escape(l["mo_ta"])}</p></div>')
        (ROOT / f'{l["key"]}.html').write_text(
            page(f'Buổi {l["so"]}: {l["tieu_de"]} | {COURSE}', l["mo_ta"], l["key"], lessons,
                 head + content + pager, toc), encoding="utf-8")

    # ket luan
    meta, body = read(CONTENT / "ket-luan.md")
    content, toc = render(body)
    last = lessons[-1]
    pager = (f'<nav class="pager"><a class="prev" href="{last["key"]}.html"><small>Buổi trước</small>Buổi {last["so"]}: '
             f'{html.escape(last["tieu_de"])}</a><a class="next" href="index.html"><small>Quay về</small>Trang chủ</a></nav>')
    head = f'<div class="lesson-head"><p class="kicker">Tổng kết</p><h1>{html.escape(meta["tieu_de"])}</h1><p class="lede">{html.escape(meta["mo_ta"])}</p></div>'
    (ROOT / "ket-luan.html").write_text(page(f'{meta["tieu_de"]} | {COURSE}', meta["mo_ta"], "ket-luan", lessons,
                                             head + content + pager, toc), encoding="utf-8")

    # trang chu
    meta, body = read(CONTENT / "trang-chu.md")
    content, _ = render(body)
    cards = "".join(
        f'<li><a href="{l["key"]}.html"><span class="n">{l["so"]:02d}</span><div><h3>{html.escape(l["tieu_de"])}</h3>'
        f'<p>{html.escape(l["mo_ta"])}</p></div></a></li>' for l in lessons)
    cards += ('<li class="end"><a href="ket-luan.html"><span class="n">+</span><div><h3>Kết luận</h3>'
              '<p>Một nguyên tắc làm việc hằng tuần gói lại cả 8 buổi.</p></div></a></li>')
    hero = (f'<section class="hero"><p class="kicker">Giáo trình 8 buổi</p><h1>{html.escape(meta["tieu_de"])}</h1>'
            f'<p class="lede">{html.escape(meta["mo_ta"])}</p>'
            '<ul class="meta"><li>8 buổi học</li><li>Bài tập thực hành mỗi buổi</li><li>Checklist áp dụng</li>'
            '<li>Câu hỏi tự kiểm tra</li></ul>'
            + figure("trang-chu", meta.get("hinh", "")).replace(' loading="lazy"', ' fetchpriority="high"')
            + '</section>')
    home = (f'<div class="home"><div class="home-text">{content}</div>'
            f'<h2 id="lo-trinh">Lộ trình 8 buổi</h2><ol class="course-map">{cards}</ol></div>')
    (ROOT / "index.html").write_text(page(meta["tieu_de"], meta["mo_ta"], "index", lessons, hero + home), encoding="utf-8")
    print("built", len(lessons), "lessons")


if __name__ == "__main__":
    main()
