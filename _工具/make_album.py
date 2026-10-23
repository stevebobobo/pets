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
SOUNDS = {'寶寶：': ['寶寶_平常的叫聲.mp3', '寶寶_平常的叫聲_短.mp3', '寶寶_生氣的叫聲.mp3', '寶寶_生氣的叫聲_2.mp3']}
YOUTUBE = {'大姊家': ['zqNDjk-cnGk']}        # BOSS (胖胖)
ART = os.path.join(ROOT, '_素材')             # VectorCraft drawings: header, divider, favicon


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
            if para.startswith('### '):
                paras.append(f'<h3>{inline(para[4:])}</h3>')
            elif re.match(r'\d+\. ', para):                       # numbered list (the timeline)
                items = [re.sub(r'^\d+\. ', '', x) for x in re.split(r'\n(?=\d+\. )', para)]
                paras.append('<ol class="timeline">' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ol>')
            else:
                paras.append(f'<p>{inline(para)}</p>')
        tree = f'<pre class="tree">{html.escape(code.group(1))}</pre>' if code else ''
        key = next((k for k in SECTION_PHOTOS if head.startswith(k)), None)
        pics = photos(SECTION_PHOTOS[key]) if key else ''
        for v in VIDEOS.get(key, []):                # e.g. 寶寶's video
            if os.path.exists(os.path.join(ROOT, '影片', v)):
                pics += f'<video controls preload="metadata" src="{quote("影片/" + v)}"></video>'
        clips = [c for c in SOUNDS.get(key, []) if os.path.exists(os.path.join(ROOT, '聲音', c))]
        if clips:
            pics += '<div class="voices"><p class="who">聽聽牠的聲音</p>' + ''.join(
                f'<figure><figcaption>{html.escape(c[:-4].replace("_", "・"))}</figcaption>'
                f'<audio controls preload="none" src="{quote("聲音/" + c)}"></audio></figure>' for c in clips) + '</div>'
        for y in YOUTUBE.get(key, []):
            pics += (f'<div class="yt"><iframe src="https://www.youtube-nocookie.com/embed/{y}" title="影片" loading="lazy" '
                     'referrerpolicy="strict-origin-when-cross-origin" '
                     'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
                     f'<p class="ytlink"><a href="https://youtu.be/{y}" target="_blank">在 YouTube 上看這支影片 →</a></p>')
        short = head.split('：')[0]
        nav.append(f'<a href="#{sid}">{html.escape(short)}</a>')
        body.append(f'<section id="{sid}"><img class="divider" src="_素材/art-pets_divider.svg" alt="">'
                    f'<h2>{inline(head)}</h2>{tree}<div class="prose">{"".join(paras)}</div>{pics}</section>')
    intro_html = ''.join(f'<p>{inline(x.strip())}</p>' for x in intro.split('\n\n')
                         if x.strip() and not x.strip().startswith('---') and '相簿.html' not in x)
    header_svg = open(os.path.join(ART, 'art-pets_header.svg'), encoding='utf-8').read()
    header_svg = re.sub(r'<title>.*?</title>\s*', '', header_svg[header_svg.index('<svg'):])
    header_svg = re.sub(r'\s(width|height)="\d+"', '', header_svg, count=2)
    marks = [(r'(<path d="M\d+(?:\.\d+)? \d+(?:\.\d+)? C[^"]*" fill="#c9b48f")', 'twinkle'),   # stars
             (r'(<path d="M468 52[^"]*")', 'halo'), (r'(<path id="cat_big_tail")', 'tail'),
             (r'(<path d="M238 115[^"]*")', 'tail2'), (r'(<path id="piglet")', 'pig'),
             (r'(<path d="M485 147[^"]*")', 'pig'), (r'(<path d="M441 158[^"]*")', 'pig')]
    for pat, cls in marks:
        header_svg = re.sub(pat, lambda m: m.group(1) + f' class="{cls}"', header_svg).replace('<svg ', '<svg class="hero" role="img" aria-label="巷子的牆上，兩隻貓看著月亮，地上一隻小豬" ', 1)
    page = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noimageindex">
<title>{html.escape(title)}</title>
<link rel="icon" href="_素材/art-pets_favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,400;1,500&family=Noto+Serif+TC:wght@400;600&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#f3ece0; --card:#fbf7f0; --ink:#3d3129; --soft:#7d6b5a; --line:#e0d3bf; --accent:#8f5f3e; --gold:#b9a17c; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#1f1a16; --card:#2a231e; --ink:#ece2d3; --soft:#b3a28d; --line:#3b322a; --accent:#d9a67c; --gold:#a88f6a; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; color:var(--ink); font:17px/2 "Noto Serif TC","PMingLiU",serif;
  background:var(--bg) radial-gradient(ellipse at 50% -10%, rgba(255,250,240,.7), transparent 60%) no-repeat; }}
@media (prefers-color-scheme: dark) {{
  body {{ background:var(--bg) radial-gradient(ellipse 55% 75% at 50% 0%, rgba(255,246,230,.55), rgba(255,240,215,.12) 55%, transparent 80%) no-repeat; }}
  header h1 {{ color:#fbf3e6; text-shadow:0 1px 14px rgba(20,14,8,.55); }}
  header p {{ color:#f3e8d6; text-shadow:0 1px 10px rgba(20,14,8,.8), 0 0 2px rgba(20,14,8,.6); }}
  .kicker {{ color:#f0c49a; text-shadow:0 1px 8px rgba(20,14,8,.7); }}
  main p, .prose, .timeline li {{ text-shadow:0 1px 8px rgba(20,14,8,.55); }}
}}
header {{ max-width:760px; margin:0 auto; padding:40px 20px 28px; text-align:center; }}
.hero {{ width:100%; max-width:600px; height:auto; display:block; margin:0 auto 18px; }}
.kicker {{ font:italic 500 19px "Cormorant Garamond",Georgia,serif; color:var(--accent); letter-spacing:.08em; margin:0; }}
h1 {{ font-size:42px; font-weight:600; line-height:1.3; margin:6px 0 22px; letter-spacing:.12em; }}
header p {{ color:var(--soft); max-width:600px; margin:0 auto 12px; }}
nav {{ position:sticky; top:0; background:color-mix(in srgb, var(--bg) 92%, transparent); backdrop-filter:blur(6px);
  border-top:1px solid var(--line); border-bottom:1px solid var(--line); z-index:2; }}
nav div {{ max-width:860px; margin:0 auto; padding:10px 20px; display:flex; gap:22px; overflow-x:auto; white-space:nowrap;
  font-size:14px; justify-content:center; }}
nav a {{ color:var(--soft); text-decoration:none; }} nav a:hover {{ color:var(--accent); }}
main {{ max-width:860px; margin:0 auto; padding:0 20px 60px; }}
section {{ padding:56px 0 12px; }}
.divider {{ display:block; width:160px; margin:0 auto 18px; opacity:.9; }}
h2 {{ text-align:center; font-size:27px; font-weight:600; letter-spacing:.08em; margin:0 0 26px; color:var(--ink); }}
h3 {{ font-size:19px; font-weight:600; color:var(--accent); margin:34px 0 8px; letter-spacing:.05em; }}
h3::before {{ content:"— "; color:var(--gold); }}
.prose {{ max-width:660px; margin:0 auto; }}
p {{ margin:0 0 16px; }}
.who {{ max-width:660px; margin:30px auto 4px; font:italic 500 18px "Cormorant Garamond","Noto Serif TC",serif; color:var(--soft); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(170px,1fr)); gap:26px 20px; margin:16px 0 22px; padding:6px; }}
.grid a {{ display:block; background:var(--card); padding:8px 8px 26px; box-shadow:0 1px 2px rgba(60,40,20,.12), 0 6px 18px rgba(60,40,20,.10);
  transform:rotate(-1.2deg); transition:transform .3s ease, box-shadow .3s ease; }}
.grid a:nth-child(2n) {{ transform:rotate(1deg); }}
.grid a:nth-child(3n) {{ transform:rotate(-.4deg); }}
.grid a:hover {{ transform:rotate(0) scale(1.03); box-shadow:0 2px 4px rgba(60,40,20,.15), 0 12px 28px rgba(60,40,20,.16); }}
.grid img {{ width:100%; aspect-ratio:1; object-fit:cover; display:block; background:var(--line); filter:sepia(.12) saturate(.95); }}
video, .yt {{ width:100%; max-width:640px; display:block; margin:18px auto 22px; background:var(--card); padding:8px;
  box-shadow:0 6px 18px rgba(60,40,20,.12); }}
.yt {{ aspect-ratio:16/9; }} .yt iframe {{ width:100%; height:100%; border:0; display:block; }}
.tree {{ max-width:560px; margin:0 auto 26px; font:15px/1.8 "Noto Serif TC","Microsoft JhengHei",monospace; background:var(--card);
  padding:20px 22px; border:1px solid var(--line); overflow-x:auto; }}
.timeline {{ list-style:none; padding:0; margin:0 0 16px; counter-reset:t; }}
.timeline li {{ position:relative; padding:0 0 14px 44px; counter-increment:t; }}
.timeline li::before {{ content:counter(t); position:absolute; left:0; top:2px; width:28px; height:28px; border:1px solid var(--gold);
  border-radius:50%; text-align:center; font:italic 500 17px/26px "Cormorant Garamond",serif; color:var(--accent); }}
.voices {{ max-width:660px; margin:0 auto 20px; }} .voices figure {{ margin:8px 0; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }}
.voices figcaption {{ min-width:9em; color:var(--soft); font-size:15px; }} .voices audio {{ height:36px; flex:1; min-width:220px; }}
.ytlink {{ text-align:center; font-size:14px; margin:-10px 0 20px; }} .ytlink a {{ color:var(--soft); }}
code {{ font-size:14px; color:var(--soft); }}
footer {{ text-align:center; color:var(--soft); font:italic 500 17px "Cormorant Garamond","Noto Serif TC",serif; padding:30px 20px 50px; }}
footer img {{ width:28px; display:block; margin:0 auto 10px; opacity:.8; }}
/* gentle motion: stars twinkle, the moon breathes, tails sway, the piglet trots; things fade in */
.hero .twinkle {{ animation:twinkle 3.2s ease-in-out infinite; }}
.hero .twinkle:nth-of-type(2n) {{ animation-delay:1.1s; }} .hero .twinkle:nth-of-type(3n) {{ animation-delay:2s; }}
.hero .halo {{ transform-box:fill-box; transform-origin:center; animation:halo 5s ease-in-out infinite; }}
.hero .tail {{ transform-box:fill-box; transform-origin:0% 0%; animation:sway 3.6s ease-in-out infinite; }}
.hero .tail2 {{ transform-box:fill-box; transform-origin:100% 0%; animation:sway 4.4s ease-in-out infinite reverse; }}
.hero .pig {{ animation:trot 7s ease-in-out infinite; }}
@keyframes twinkle {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.15; }} }}
@keyframes halo {{ 0%,100% {{ transform:scale(1); opacity:.35; }} 50% {{ transform:scale(1.15); opacity:.6; }} }}
@keyframes sway {{ 0%,100% {{ transform:rotate(0); }} 50% {{ transform:rotate(7deg); }} }}
@keyframes trot {{ 0%,100% {{ transform:translate(0,0); }} 20% {{ transform:translate(-6px,-1.5px); }} 25% {{ transform:translate(-8px,0); }}
  45% {{ transform:translate(-8px,0); }} 70% {{ transform:translate(0,-1.5px); }} 75% {{ transform:translate(0,0); }} }}
header > * {{ animation:rise 1.2s ease both; }} header > :nth-child(2) {{ animation-delay:.3s; }}
header > :nth-child(3) {{ animation-delay:.5s; }} header > :nth-child(n+4) {{ animation-delay:.8s; }}
@keyframes rise {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:none; }} }}
.reveal {{ opacity:0; transform:translateY(18px); transition:opacity 1s ease, transform 1s ease; }}
.reveal.on {{ opacity:1; transform:none; }}
@media (prefers-reduced-motion: reduce) {{ *, *::before {{ animation:none !important; transition:none !important; }} .reveal {{ opacity:1; transform:none; }} }}
@media (max-width:480px) {{
  body {{ font-size:16px; }}
  h1 {{ font-size:32px; letter-spacing:.08em; }}
  h2 {{ font-size:23px; }}
  nav div {{ justify-content:flex-start; gap:18px; }}
  .grid {{ grid-template-columns:repeat(2,1fr); gap:18px 14px; }}
  .grid a {{ padding:6px 6px 18px; }}
}}
</style></head><body>
<header>{header_svg}<p class="kicker">In loving memory</p><h1>{html.escape(title)}</h1>{intro_html}</header>
<nav><div>{"".join(nav)}</div></nav>
<main>{"".join(body)}</main>
<footer><img src="_素材/art-pets_favicon.svg" alt="">謝謝你們，曾經陪著我們。</footer>
<script>
// fade each photo, video and heading in as it scrolls into view
const els = document.querySelectorAll('main h2, main .grid, main video, main .yt, main .tree');
if ('IntersectionObserver' in window) {{
  const io = new IntersectionObserver(es => es.forEach(e => {{ if (e.isIntersecting) {{ e.target.classList.add('on'); io.unobserve(e.target); }} }}), {{ rootMargin: '0px 0px -8% 0px' }});
  els.forEach(el => {{ el.classList.add('reveal'); io.observe(el); }});
}}
</script>
</body></html>'''
    for name in ('相簿.html', 'index.html'):          # index.html is what GitHub Pages serves
        open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(page)
    print('ok', len(nav), 'sections')


if __name__ == '__main__':
    main()
