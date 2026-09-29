#!/usr/bin/env python3
"""Baut die statische Website des SV 1919 Osterburken e.V.

    python3 build.py

Liest  src/pages/*.html   (Kopfzeilen bis '---': title, description, theme, nav, scripts, robots)
       src/partials/      (header.html, footer.html)
       src/data/*.json    (Beiträge, Sponsoren)
schreibt public/*.html und public/aktuelles/<slug>.html.

Platzhalter in Seiten: {{root}} {{icon:name}} {{motif:name}} {{news_latest:4}} {{news_all}} {{news_cat:turnen:4}}
{{news_related:stichwort}} {{art:name}} (3D-Icon) {{sponsors_maeh}} {{sponsors_all}} {{sponsor_band}} {{vorstand}}
"""
import datetime
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / 'src', ROOT / 'public'
MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
          'September', 'Oktober', 'November', 'Dezember']
CATS = {'fussball': 'Fußball', 'turnen': 'Turnen', 'fitness': 'Fitness', 'verein': 'Verein'}

# ---------- Vorstandschaft ----------
VORSTAND = [
    ('Vorstand', [
        ('Gustav Hofmann', '1. Vorstand', 'vorstand@svosterburken.de'),
        ('Tabitha Heinemann', '2. Vorstand', 'vorstand@svosterburken.de'),
        ('Natalia Siemens', 'Schatzmeisterin', None),
        ('Holger Speck', 'Schrift- und Karteiführer', 'schriftfuehrung@svosterburken.de'),
        ('Joel Heidl', 'Öffentlichkeitsreferent', 'pr@svosterburken.de'),
    ]),
    ('Abteilungen & Jugend', [
        ('Andreas Siegfried', 'Abteilungsleiter Fußball', 'fussball@svosterburken.de'),
        ('Robert Maier', 'Abteilungsleiter Fußball', 'fussball@svosterburken.de'),
        ('Stefan Elert', 'Jugendleiter Fußball (D–A)', 'jugend.fussball@svosterburken.de'),
        ('Holger Karle', 'Jugendleiter Fußball (Bambini–E)', 'jugend.fussball@svosterburken.de'),
        ('Thomas Ernst', 'Abteilungsleiter Turnen', 'turnen@svosterburken.de'),
        ('Cornelia Ernst', 'Jugendleiterin Turnen', 'turnen@svosterburken.de'),
    ]),
    ('Beisitzer', [
        ('Alex Titarenko', 'Beisitzer', None),
        ('Thomas Pysik', 'Beisitzer', None),
        ('Frank Blischke', 'Beisitzer', None),
        ('Jannik Frankenberger', 'Beisitzer', None),
    ]),
]

# ---------- Deko-Motive für die Abteilungs-Header ----------
MOTIFS = {
    'pitch': '<svg class="motif" viewBox="0 0 800 500" aria-hidden="true" preserveAspectRatio="xMaxYMid slice"><g fill="none" stroke="currentColor" stroke-width="2.5"><rect x="40" y="40" width="1100" height="420"/><line x1="400" y1="40" x2="400" y2="460"/><circle cx="400" cy="250" r="80"/><circle cx="400" cy="250" r="4" fill="currentColor"/><rect x="620" y="140" width="180" height="220"/><rect x="720" y="195" width="80" height="110"/><path d="M620 205a60 60 0 0 0 0 90"/></g></svg>',
    'arcs': '<svg class="motif" viewBox="0 0 800 500" aria-hidden="true" preserveAspectRatio="xMaxYMid slice"><g fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="720" cy="420" r="120"/><circle cx="720" cy="420" r="200"/><circle cx="720" cy="420" r="280"/><circle cx="720" cy="420" r="360"/><path d="M80 420C200 300 300 460 420 330S640 240 760 120" stroke-dasharray="6 10"/></g></svg>',
    'wave': '<svg class="motif" viewBox="0 0 800 500" aria-hidden="true" preserveAspectRatio="xMaxYMid slice"><g fill="currentColor">' + ''.join(
        f'<rect x="{430 + i * 24}" y="{250 - h}" width="10" height="{2 * h}" rx="5"/>'
        for i, h in enumerate([20, 45, 80, 130, 90, 170, 110, 60, 140, 190, 120, 70, 100, 40, 25, 55])) + '</g></svg>',
    'stripes': '<svg class="motif" viewBox="0 0 800 500" aria-hidden="true" preserveAspectRatio="xMaxYMid slice"><g fill="currentColor">' + ''.join(
        f'<rect x="{480 + i * 44}" y="0" width="22" height="500"/>' for i in range(8)) + '</g></svg>',
}


# Vektor-Icon-Name → farbiges Flat-Icon (public/assets/img/iconsflat/*.svg)
ART = {'link': 'handshake', 'file': 'clipboard', 'edit': 'clipboard', 'users': 'team', 'star': 'trophy',
       'phone': 'shield', 'external': 'ball', 'euro': 'heart'}


def art(name, cls='art'):
    name = ART.get(name, name)
    return f'<img class="{cls}" src="{{{{root}}}}assets/img/iconsflat/{name}.svg" alt="" width="96" height="96" loading="lazy">'


def icon(name, cls='i'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="{{{{root}}}}assets/img/icons.svg#{name}"/></svg>'


def de_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d.day}. {MONTHS[d.month - 1]} {d.year}'


def news_card(p, root):
    tags = ''.join(f'<span class="tag tag--{c}">{CATS[c]}</span>' for c in p['cats'])
    thumb = f"{root}assets/img/news/thumb/{p['slug']}.jpg" if p['image'] else f'{root}assets/img/svo-logo-512.png'
    excerpt = f"<p>{html.escape(p['excerpt'])}</p>" if p['excerpt'] else ''
    return f'''<article class="news-card" data-cats="{' '.join(p['cats'])}">
  <div class="news-card__media"><img class="bg" src="{thumb}" alt="" loading="lazy"><img class="fg" src="{thumb}" alt="" loading="lazy"></div>
  <div class="news-card__body">
    <div class="tags">{tags}</div>
    <h3><a href="{root}aktuelles/{p['slug']}.html">{html.escape(p['title'])}</a></h3>
    <time datetime="{p['date']}">{icon('calendar')}{de_date(p['date'])}</time>
    {excerpt}
    <span class="more">Weiterlesen {icon('arrow')}</span>
  </div>
</article>'''


def sponsor_grid(items, root):
    return '<ul class="logos">' + ''.join(
        f'<li><img src="{root}{s["img"]}" alt="{html.escape(s["name"])}" title="{html.escape(s["name"])}" loading="lazy" width="{s["w"]}" height="{s["h"]}"></li>'
        for s in items) + '</ul>'


def vorstand_html(root):
    out = []
    for group, people in VORSTAND:
        cards = []
        for name, role, mail in people:
            initials = ''.join(w[0] for w in name.split()[:2])
            contact = f'<a href="mailto:{mail}">{icon("mail")}{mail}</a>' if mail else ''
            cards.append(f'''<article class="person">
  <div class="person__photo" data-initials="{initials}"><img src="{root}assets/img/person-placeholder.svg" alt="" loading="lazy"><span class="person__tbd">Foto folgt</span></div>
  <h3>{name}</h3><p>{role}</p>{contact}
</article>''')
        out.append(f'<h3 class="subhead">{group}</h3><div class="people">{"".join(cards)}</div>')
    return ''.join(out)


def render(body, meta, root, ctx):
    head = (SRC / 'partials/header.html').read_text()
    foot = (SRC / 'partials/footer.html').read_text()
    nav = meta.get('nav', '')
    if nav:
        head = head.replace(f'data-nav="{nav}"', f'data-nav="{nav}" data-active')
    scripts = ''.join(f'<script src="{{{{root}}}}assets/{s.strip()}"></script>'
                      for s in meta.get('scripts', '').split(',') if s.strip())
    page = head + body + foot
    news = ctx['news']

    page = re.sub(r'\{\{art:([\w-]+)\}\}', lambda m: art(m.group(1)), page)
    page = re.sub(r'\{\{icon:([\w-]+)\}\}', lambda m: icon(m.group(1)), page)
    page = re.sub(r'\{\{motif:(\w+)\}\}', lambda m: MOTIFS[m.group(1)], page)
    page = re.sub(r'\{\{news_latest:(\d+)\}\}', lambda m: ''.join(news_card(p, root) for p in news[:int(m.group(1))]), page)
    page = re.sub(r'\{\{news_cat:(\w+):(\d+)\}\}',
                  lambda m: ''.join(news_card(p, root) for p in [p for p in news if m.group(1) in p['cats']][:int(m.group(2))]), page)
    page = re.sub(r'\{\{news_related:([\w-]+)\}\}',
                  lambda m: ''.join(news_card(p, root) for p in [p for p in news if m.group(1) in p['slug']][:4]), page)
    reps = {
        '{{news_all}}': lambda: ''.join(news_card(p, root) for p in news),
        '{{sponsors_maeh}}': lambda: sponsor_grid([s for s in ctx['sponsors'] if s.get('maeh')], root),
        '{{sponsors_all}}': lambda: sponsor_grid(ctx['sponsors'], root),
        '{{sponsor_band}}': lambda: ''.join(
            f'<img src="{root}{s["img"]}" alt="{html.escape(s["name"])}" loading="lazy">' for s in ctx['sponsors']),
        '{{vorstand}}': lambda: vorstand_html(root),
        '{{scripts}}': lambda: scripts,
    }
    for k, fn in reps.items():
        if k in page:
            page = page.replace(k, fn())
    page = page.replace('{{robots_meta}}', '<meta name="robots" content="noindex, nofollow">' if meta.get('robots') else '')
    for k in ('title', 'description', 'theme'):
        page = page.replace('{{%s}}' % k, html.escape(meta.get(k, ''), quote=True))
    page = page.replace('{{year}}', str(datetime.date.today().year))
    # Cache-Busting: Version = Hash des Dateiinhalts
    for asset in ('css/style.css', 'css/fonts.css', 'js/data.js', 'js/main.js', 'js/forms.js', 'img/person-placeholder.svg'):
        ver = hashlib.md5((OUT / 'assets' / asset).read_bytes()).hexdigest()[:8]
        page = page.replace(f'assets/{asset}"', f'assets/{asset}?v={ver}"')
    return page.replace('{{root}}', root)


def parse(path):
    raw = path.read_text()
    head, body = raw.split('\n---\n', 1)
    meta = dict(line.split(':', 1) for line in head.strip().splitlines())
    return {k.strip(): v.strip() for k, v in meta.items()}, body


def article(p, i, news):
    prev_p = news[i + 1] if i + 1 < len(news) else None
    next_p = news[i - 1] if i > 0 else None
    tags = ''.join(f'<a class="tag tag--{c}" href="../aktuelles.html#{c}">{CATS[c]}</a>' for c in p['cats'])
    img = ''
    if p['image']:
        img = f'''<figure class="article__media"><img class="bg" src="{{{{root}}}}{p['image']}" alt=""><img class="fg" src="{{{{root}}}}{p['image']}" alt="{html.escape(p['title'])}"></figure>'''
    pager = '<nav class="pager" aria-label="Weitere Beiträge">'
    pager += (f'<a class="pager__prev" href="{prev_p["slug"]}.html">{icon("arrow-left")}<span><small>Älter</small>{html.escape(prev_p["title"])}</span></a>' if prev_p else '<span></span>')
    pager += (f'<a class="pager__next" href="{next_p["slug"]}.html"><span><small>Neuer</small>{html.escape(next_p["title"])}</span>{icon("arrow")}</a>' if next_p else '<span></span>')
    pager += '</nav>'
    theme = next((c for c in p['cats'] if c != 'verein'), 'verein')
    body = f'''
<section class="article-hero">
  <div class="wrap wrap--narrow">
    <a class="back" href="../aktuelles.html">{icon('arrow-left')}Alle Beiträge</a>
    <div class="tags">{tags}</div>
    <h1 class="display">{html.escape(p['title'])}</h1>
    <time datetime="{p['date']}">{icon('calendar')}{de_date(p['date'])}</time>
  </div>
</section>
<section class="section section--tight">
  <div class="wrap wrap--narrow">
    {img}
    <div class="prose">{p['body']}</div>
    {pager}
  </div>
</section>'''
    meta = {'title': f"{p['title']} – SV 1919 Osterburken e.V.",
            'description': p['excerpt'] or p['title'], 'theme': theme, 'nav': 'aktuelles'}
    return body, meta


def main():
    news = json.loads((SRC / 'data/news.json').read_text())
    news.sort(key=lambda p: p['date'], reverse=True)
    ctx = {'news': news, 'sponsors': json.loads((SRC / 'data/sponsors.json').read_text())}
    count = 0
    for path in sorted((SRC / 'pages').glob('*.html')):
        meta, body = parse(path)
        (OUT / path.name).write_text(render(body, meta, '', ctx))
        count += 1
    (OUT / 'aktuelles').mkdir(exist_ok=True)
    for i, p in enumerate(news):
        body, meta = article(p, i, news)
        (OUT / 'aktuelles' / f"{p['slug']}.html").write_text(render(body, meta, '../', ctx))
        count += 1
    print(f'{count} Seiten gebaut → {OUT}')


if __name__ == '__main__':
    main()
