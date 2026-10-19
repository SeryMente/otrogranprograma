#!/usr/bin/env python3
"""Private synthetic fixtures only; never writes sample posts to the public source."""
from pathlib import Path
import tempfile, shutil, subprocess, json, sys
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='blog-contract-') as t:
    r=Path(t); (r/'scripts').mkdir(); (r/'blog/entries').mkdir(parents=True)
    shutil.copy(HERE/'build-personal-blog.py',r/'scripts/build-personal-blog.py')
    def run(ok=True):
        p=subprocess.run([sys.executable,str(r/'scripts/build-personal-blog.py')],capture_output=True,text=True)
        assert (p.returncode==0)==ok,p.stderr
    run(); assert 'Aún no hay entradas' in (r/'blog/index.html').read_text(encoding='utf-8')
    d={'schema':1,'slug':'2026-10-18-prueba','title':'Texto <script> & seguro','date':'2026-10-18T19:00:00-06:00','body':'Primera línea <script>alert(1)</script>\n\nSegundo párrafo.','source':{'kind':'khora','sha256':'a'*64}}
    p=r/'blog/entries'/f'{d["slug"]}.json';p.write_text(json.dumps(d), encoding='utf-8');run()
    html=(r/'blog/entradas'/d['slug']/'index.html').read_text(encoding='utf-8')
    assert '<script>alert' not in html and '&lt;script&gt;alert' in html
    assert html.count('<p>Primera')==1 and 'Segundo párrafo.' in html
    assert 'La huella identifica este texto' in html
    assert json.loads((r/'blog/archivo.json').read_text(encoding='utf-8'))['entries']==[d]
    assert ET.parse(r/'blog/feed.xml').find('.//item/title').text==d['title']
    for field,value in [('slug','../../private'),('date','2026-10-18'),('body',''),('source',{'kind':'other'})]:
        bad={**d,field:value}; p.write_text(json.dumps(bad), encoding='utf-8');run(False)
    p.write_text(json.dumps(d), encoding='utf-8');run()
print('BLOG_CONTRACT_OK: empty, render, permalink, export, RSS, XSS, slug, timezone, body, provenance')
