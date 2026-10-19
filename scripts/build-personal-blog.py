#!/usr/bin/env python3
"""Deterministic public blog builder. No network, credentials or private Khora reads."""
from pathlib import Path
from html import escape as e
from datetime import datetime
import json, re, hashlib, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
BLOG=ROOT/'blog'
BASE='https://serymente.github.io/otrogranprograma/blog/'
def shell(title,body,depth='',description='Bitácora personal de Víctor Hugo Torres: vida, trabajo y proyectos.',canonical=''):
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · Víctor Hugo Torres</title><meta name="description" content="{e(description,quote=True)}"><meta name="author" content="Víctor Hugo Torres"><meta name="color-scheme" content="light dark"><link rel="stylesheet" href="{depth}blog.css?v=1"><link rel="alternate" type="application/rss+xml" title="Bitácora" href="{depth}feed.xml">{f'<link rel="canonical" href="{e(canonical,quote=True)}">' if canonical else ''}</head><body><a class="skip" href="#contenido">Saltar al contenido</a><header><a class="brand" href="{depth or './'}">Víctor Hugo Torres<span>Bitácora personal</span></a><nav aria-label="Principal"><a href="{depth or './'}">Entradas</a><a href="{depth}escribir/">Escribir</a><a href="{depth}laboratorio/">Laboratorio</a></nav></header><main id="contenido">{body}</main><footer><span>Un archivo propio, una entrada a la vez.</span><nav aria-label="Enlaces del archivo"><a href="{depth}feed.xml">RSS</a><a href="{depth}archivo.json" download>Descargar archivo</a><a href="{depth}../">Otro Gran Programa</a></nav></footer></body></html>'''
def validate(d):
    assert isinstance(d,dict), 'Entrada debe ser objeto'
    assert set(d)<= {'schema','slug','title','date','body','source'}, 'Campos no reconocidos'
    assert d.get('schema')==1, 'schema debe ser 1'
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',d['slug']) and len(d['slug'])<=100, 'slug inválido'
    assert isinstance(d['title'],str) and 1<=len(d['title'].strip())<=160, 'Título inválido'
    assert isinstance(d['body'],str) and 1<=len(d['body'].strip())<=200000, 'Cuerpo inválido'
    dt=datetime.fromisoformat(d['date'])
    assert dt.tzinfo is not None, 'Fecha requiere zona horaria'
    if 'source' in d:
        assert isinstance(d['source'],dict) and set(d['source'])<= {'kind','sha256'}, 'Procedencia inválida'
        assert d['source'].get('kind') in ('manual','khora'), 'Origen inválido'
        h=d['source'].get('sha256')
        assert h is None or re.fullmatch('[a-f0-9]{64}',h), 'Huella inválida'
    return dt

def build():
    entries=[]; seen=set()
    for p in sorted((BLOG/'entries').glob('*.json')):
        d=json.loads(p.read_text(encoding='utf-8')); validate(d)
        assert p.stem==d['slug'], 'Nombre de archivo distinto del slug'
        assert d['slug'] not in seen, 'Slug duplicado'
        seen.add(d['slug']); entries.append(d)
    entries.sort(key=lambda d: datetime.fromisoformat(d['date']),reverse=True)
    cards=[]
    for d in entries:
        dt=datetime.fromisoformat(d['date']); date=dt.strftime('%d/%m/%Y')
        text=d['body']; summary=' '.join(text.split())[:220]
        words=len(text.split()); minutes=max(1,round(words/200))
        cards.append(f'<article class="entry" data-search="{e((d["title"]+" "+text).lower(),quote=True)}"><p class="meta"><time datetime="{e(d["date"],quote=True)}">{date}</time> · {minutes} min de lectura</p><h2><a href="entradas/{e(d["slug"])}/">{e(d["title"])}</a></h2><p>{e(summary)}{ "…" if len(text)>220 else ""}</p></article>')
        paras=''.join('<p>'+e(p).replace('\n','<br>')+'</p>' for p in re.split(r'\n\s*\n',text.strip()))
        digest=hashlib.sha256(text.encode()).hexdigest()
        origin='Khora · selección revisada por el autor' if d.get('source',{}).get('kind')=='khora' else 'Escritura del autor'
        body=f'<a class="back" href="../../">← Todas las entradas</a><article class="reading"><p class="eyebrow">BITÁCORA PERSONAL</p><h1>{e(d["title"])}</h1><p class="meta">Víctor Hugo Torres · <time datetime="{e(d["date"],quote=True)}">{date}</time> · {minutes} min de lectura</p><div class="prose">{paras}</div><details><summary>Procedencia y archivo</summary><p>{origin}. La huella identifica este texto; no certifica por sí sola los hechos narrados.</p><p class="hash">SHA-256 del texto publicado: {digest}</p><p><a href="https://github.com/SeryMente/otrogranprograma/commits/main/blog/entries/{e(d["slug"])}.json">Historial de esta entrada</a> · <a download href="../../entries/{e(d["slug"])}.json">Original portable</a></p></details></article>'
        out=BLOG/'entradas'/d['slug']; out.mkdir(parents=True,exist_ok=True)
        (out/'index.html').write_text(shell(d['title'],body,'../../',summary,BASE+'entradas/'+d['slug']+'/'), encoding='utf-8')
    empty='<section class="empty"><h2>El archivo comienza aquí.</h2><p>Aún no hay entradas publicadas. Cada entrada aparecerá aquí después de que su autor la revise y confirme su publicación.</p><a class="button" href="escribir/">Preparar la primera entrada</a></section>'
    intro='<section class="intro"><p class="eyebrow">VIDA · TRABAJO · PROYECTOS</p><h1>Bitácora personal.</h1><p class="dek">Un espacio de Víctor Hugo Torres para dejar constancia de su día a día, con voz propia y un archivo bajo su control.</p></section>'
    search='<div class="archive-bar"><h2>Entradas</h2><label>Buscar <input id="buscar" type="search" placeholder="Buscar en el archivo" autocomplete="off"></label></div><p id="sin-resultados" hidden>No hay entradas que coincidan.</p>' if entries else ''
    script='<script src="archive.js" defer></script>' if entries else ''
    (BLOG/'index.html').write_text(shell('Bitácora personal',intro+search+(''.join(cards) or empty)+script,canonical=BASE), encoding='utf-8')
    (BLOG/'archivo.json').write_text(json.dumps({'schema':1,'author':'Víctor Hugo Torres','entries':entries},ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    rss=ET.Element('rss',version='2.0'); ch=ET.SubElement(rss,'channel')
    for k,v in [('title','Bitácora · Víctor Hugo Torres'),('link',BASE),('description','Vida, trabajo y proyectos. Archivo personal.')]: ET.SubElement(ch,k).text=v
    from email.utils import format_datetime
    for d in entries:
        item=ET.SubElement(ch,'item')
        for k,v in [('title',d['title']),('link',BASE+'entradas/'+d['slug']+'/'),('guid',BASE+'entradas/'+d['slug']+'/'),('pubDate',format_datetime(datetime.fromisoformat(d['date']))),('description',d['body'])]: ET.SubElement(item,k).text=v
    ET.ElementTree(rss).write(BLOG/'feed.xml',encoding='utf-8',xml_declaration=True)
    print(f'BLOG_BUILD_OK entries={len(entries)}')
if __name__=='__main__': build()
