r"""Build 相簿.html from 故事.md and the 照片 folders.

Usage:  py _工具\make_album.py      (run again after adding photos or editing 故事.md)

Each "## " section of 故事.md becomes a chapter; SECTION_PHOTOS says which photo
folders belong to it. Photos are linked, not copied, so the page must stay next to 照片\.
"""
import html
from urllib.parse import quote
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = os.path.join(ROOT, '照片')
IMG = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

SECTION_PHOTOS = {
    '第一代': ['喵喵', '小貓'], '雙雄時代': ['偉偉', '娃娃', 'Midnight'], '寶寶：': ['寶寶'],
    '寶寶和乖乖': ['乖乖'], '波士頓和黑帝斯': ['波士頓', '黑帝斯', '波士頓或黑帝斯'],
    '大姊家': ['卡蜜兒', '胖胖', '酷蒂'],
}
VIDEOS = {'寶寶：': ['寶寶.mp4']}


def inline(t):
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)


def photos(folders):
    out = []
    for f in folders:
        d = os.path.join(PHOTOS, f)
        if not os.path.isdir(d):
            continue
        files = sorted(x for x in os.listdir(d) if x.lower().endswith(IMG))
        if not files:
            continue
        label = f'<p class="who">{html.escape(f)}（{len(files)} 張）</p>' if len(folders) > 1 else ''
        items = ''.join(f'<a href="{quote(f'照片/{f}/{x}')}" target="_blank">'
                        f'<img loading="lazy" src="{quote(f'照片/{f}/{x}')}" alt=""></a>' for x in files)
        out.append(f'{label}<div class="grid">{items}</div>')
    return ''.join(out)


def main():
    md = open(os.path.join(ROOT, '故事.md'), encoding='utf-8').read()
    title = re.search(r'^# (.+)$', md, re.M).group(1)
    parts = re.split(r'^## ', md, flags=re.M)
    intro = parts[0].split('\n', 1)[1]
    body, nav = [], []
    for i, p in enumerate(parts[1:]):
        head, text = p.split('\n', 1)
        text = text.split('\n---')[0]
        sid = f's{i}'
        paras, code = [], re.search(r'```\n(.*?)```', text, re.S)
        text_wo = re.sub(r'```.*?```', '', text, flags=re.S)
        for para in [x.strip() for x in text_wo.split('\n\n') if x.strip()]:
            paras.append(f'<h3>{inline(para[4:])}</h3>' if para.startswith('### ') else f'<p>{inline(para)}</p>')
        tree = f'<pre class="tree">{html.escape(code.group(1))}</pre>' if code else ''
        key = next((k for k in SECTION_PHOTOS if head.startswith(k)), None)
        pics = photos(SECTION_PHOTOS[key]) if key else ''
        for v in VIDEOS.get(key, []):                # e.g. 寶寶's video
            if os.path.exists(os.path.join(ROOT, '影片', v)):
                pics += f'<video controls preload="metadata" src="{quote("影片/" + v)}"></video>'
        short = head.split('：')[0]
        nav.append(f'<a href="#{sid}">{html.escape(short)}</a>')
        body.append(f'<section id="{sid}"><h2>{inline(head)}</h2>{tree}{"".join(paras)}{pics}</section>')
    intro_html = ''.join(f'<p>{inline(x.strip())}</p>' for x in intro.split('\n\n')
                         if x.strip() and not x.strip().startswith('---') and '相簿.html' not in x)
    page = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noimageindex">
<title>{html.escape(title)}</title>
<style>
:root {{ --bg:#f6f1e7; --ink:#2b2622; --soft:#7a6f63; --line:#ded4c4; --accent:#b5652b; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#1d1a17; --ink:#ece4d8; --soft:#a89c8d; --line:#3a332c; --accent:#e0965c; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:17px/1.9 "Noto Serif TC","PMingLiU",serif; }}
header {{ max-width:860px; margin:0 auto; padding:64px 20px 24px; border-bottom:1px solid var(--line); }}
h1 {{ font-size:44px; line-height:1.2; margin:0 0 18px; letter-spacing:.04em; }}
nav {{ position:sticky; top:0; background:var(--bg); border-bottom:1px solid var(--line); z-index:2; }}
nav div {{ max-width:860px; margin:0 auto; padding:10px 20px; display:flex; gap:16px; overflow-x:auto; white-space:nowrap;
  font:14px/1.6 "Microsoft JhengHei",sans-serif; }}
nav a {{ color:var(--soft); text-decoration:none; }} nav a:hover {{ color:var(--accent); }}
main {{ max-width:860px; margin:0 auto; padding:0 20px 80px; }}
section {{ padding:40px 0 16px; border-bottom:1px solid var(--line); }}
h2 {{ font-size:28px; margin:0 0 14px; color:var(--accent); }}
h3 {{ font-size:21px; margin:28px 0 10px; }}
p {{ margin:0 0 14px; }}
.who {{ font:14px "Microsoft JhengHei",sans-serif; color:var(--soft); margin:18px 0 6px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:10px; margin:12px 0 18px; }}
.grid img {{ width:100%; aspect-ratio:1; object-fit:cover; border-radius:4px; display:block; background:var(--line); }}
video {{ width:100%; max-width:640px; display:block; margin:8px 0 18px; border-radius:4px; }}
.tree {{ font:15px/1.7 "Microsoft JhengHei",monospace; background:rgba(0,0,0,.04); padding:16px; border-radius:6px; overflow-x:auto; }}
code {{ font-size:14px; color:var(--soft); }}
footer {{ text-align:center; color:var(--soft); font-size:14px; padding:20px; }}
</style></head><body>
<header><h1>{html.escape(title)}</h1>{intro_html}</header>
<nav><div>{"".join(nav)}</div></nav>
<main>{"".join(body)}</main>
<footer>點照片可以看大圖。新增照片或修改故事.md 後，執行 _工具\\make_album.py 重新產生這一頁。</footer>
</body></html>'''
    for name in ('相簿.html', 'index.html'):          # index.html is what GitHub Pages serves
        open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(page)
    print('ok', len(nav), 'sections')


if __name__ == '__main__':
    main()
