#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Ethical & Duty Guide website at docs/how/.

Run from repository root:
    python3 src/gen_how_html.py

Inputs:
  - data/how_duties.txt (provided curated duties dataset)
  - output/quran_*.txt  (all available verse translation files)

Outputs:
  - docs/how/index.html
  - docs/how/sd/translations.json
  - docs/how/sd/t/*.json
"""

import json
import os
import re
from glob import glob

DATA_FILE = 'data/how_duties.txt'
OUT_DIR = 'docs/how'
SD_DIR = os.path.join(OUT_DIR, 'sd')
SD_T_DIR = os.path.join(SD_DIR, 't')


def read_duties(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip() for ln in f]

    categories = []
    cur = None
    intro_done = False

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if not intro_done and line.lower().startswith('here is a comprehensive list'):
            intro_done = True
            continue

        # Category header
        if not raw.startswith(' ') and not re.match(r'^\d+\.\s+', line):
            cur = {'name': line, 'items': []}
            categories.append(cur)
            continue

        if cur is None:
            continue

        if re.match(r'^\d+\.\s+', line):
            txt = re.sub(r'^\d+\.\s*', '', line).strip()
            cur['items'].append({'text': txt, 'sub': []})
        elif line.startswith('·'):
            txt = line.lstrip('·').strip()
            if cur['items']:
                cur['items'][-1]['sub'].append(txt)

    return categories


def extract_refs(text):
    refs = []
    for m in re.finditer(r'\(([^)]*)\)', text):
        block = m.group(1)
        last_sura = None
        for tok in [t.strip() for t in block.split(',') if t.strip()]:
            m_full = re.match(r'^(\d+):(\d+)(?:-(\d+))?$', tok)
            if m_full:
                s = int(m_full.group(1))
                a1 = int(m_full.group(2))
                a2 = int(m_full.group(3)) if m_full.group(3) else a1
                if a2 < a1:
                    a1, a2 = a2, a1
                for a in range(a1, a2 + 1):
                    refs.append((s, a))
                last_sura = s
                continue
            m_short = re.match(r'^(\d+)(?:-(\d+))?$', tok)
            if m_short and last_sura is not None:
                a1 = int(m_short.group(1))
                a2 = int(m_short.group(2)) if m_short.group(2) else a1
                if a2 < a1:
                    a1, a2 = a2, a1
                for a in range(a1, a2 + 1):
                    refs.append((last_sura, a))
    return refs


def collect_all_refs(categories):
    all_refs = set()
    for cat in categories:
        for it in cat['items']:
            for r in extract_refs(it['text']):
                all_refs.add(r)
            for sub in it['sub']:
                for r in extract_refs(sub):
                    all_refs.add(r)
    return all_refs


def pretty_name(path):
    base = os.path.basename(path)
    name = base.replace('quran_', '').replace('.txt', '')
    return name, name.replace('_', ' ').title()


def load_translation_subset(path, refs_needed):
    out = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.match(r'^\[(\d+):(\d+)\]\s*(.*)$', line.rstrip('\n'))
            if not m:
                continue
            key = (int(m.group(1)), int(m.group(2)))
            if key in refs_needed:
                out[key] = m.group(3)
    return out


def build_ref_store(refs_needed):
    files = sorted(glob('output/quran_*.txt'))
    # Exclude non-translation base sources
    excluded = {
        'output/quran_arabic.txt',
        'output/quran_translit_unicode.txt',
    }
    files = [p for p in files if p not in excluded]

    translations = []
    per_t = {}
    for p in files:
        key, label = pretty_name(p)
        translations.append({'key': key, 'label': label})
        per_t[key] = load_translation_subset(p, refs_needed)

    per_translation_refs = {}
    for t in translations:
        key = t['key']
        mp = {}
        for (s, a), txt in per_t[key].items():
            mp[f'{s}:{a}'] = txt
        per_translation_refs[key] = mp

    return {'translations': translations, 'per_translation_refs': per_translation_refs}


def ref_links_html(refs):
    if not refs:
        return ''
    seen = set()
    parts = []
    for s, a in refs:
        k = (s, a)
        if k in seen:
            continue
        seen.add(k)
        href = f'../{s:03d}.html#ayah-{a}'
        parts.append(f"<a href='{href}' target='_blank' rel='noopener'>{s}:{a}</a>")
    return ' '.join(parts)


def item_html(item, idx):
    refs = extract_refs(item['text'])
    sub_rows = []
    for s in item['sub']:
        srefs = extract_refs(s)
        sub_rows.append(
            "<li><span class='sub-text'>%s</span>%s<div class='refs'>%s</div><div class='tv' data-refs='%s'></div></li>"
            % (
                s,
                " <span class='sub-ref-count'>(%d refs)</span>" % len(set(srefs)) if srefs else '',
                ref_links_html(srefs),
                ','.join([f'{r[0]}:{r[1]}' for r in srefs]),
            )
        )

    return (
        "<article class='duty-card' data-search='%s'>"
        "<h3>%s</h3>"
        "%s"
        "<div class='refs'>%s</div>"
        "<div class='tv' data-refs='%s'></div>"
        "%s"
        "</article>"
        % (
            (item['text'] + ' ' + ' '.join(item['sub'])).replace("'", '&#39;').lower(),
            item['text'],
            "<div class='ref-count'>%d references</div>" % len(set(refs)) if refs else '',
            ref_links_html(refs),
            ','.join([f'{r[0]}:{r[1]}' for r in refs]),
            ('<ul class="sub-list">' + ''.join(sub_rows) + '</ul>') if sub_rows else '',
        )
    )


def generate(categories, ref_store):
    os.makedirs(SD_T_DIR, exist_ok=True)
    stale_refs = os.path.join(SD_DIR, 'refs.json')
    if os.path.exists(stale_refs):
        os.remove(stale_refs)
    with open(os.path.join(SD_DIR, 'translations.json'), 'w', encoding='utf-8') as f:
        json.dump({'translations': ref_store['translations']}, f, ensure_ascii=False, separators=(',', ':'))
    for t in ref_store['translations']:
        key = t['key']
        with open(os.path.join(SD_T_DIR, key + '.json'), 'w', encoding='utf-8') as f:
            json.dump(ref_store['per_translation_refs'].get(key, {}), f, ensure_ascii=False, separators=(',', ':'))

    nav = []
    sections = []
    for i, cat in enumerate(categories, 1):
        cid = f'cat-{i}'
        nav.append(f"<a href='#{cid}'>{cat['name']}</a>")
        cards = ''.join(item_html(it, i) for it in cat['items'])
        sections.append(
            "<section id='%s' class='cat'><h2>%s</h2><div class='cards'>%s</div></section>"
            % (cid, cat['name'], cards)
        )

    tr_opts = ''.join(
        ["<option value='%s'>%s</option>" % (t['key'], t['label']) for t in ref_store['translations']]
    )
    filter_opts = ["<option value='all'>All Categories</option>"]
    for i, cat in enumerate(categories, 1):
        filter_opts.append("<option value='cat-%d'>%s</option>" % (i, cat['name']))

    html = """<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1.0'>
<title>Ethical & Duty Guide</title>
<style>
*,*::before,*::after{box-sizing:border-box}
body{margin:0;font-family:system-ui,Arial,Helvetica,sans-serif;background:#fff;color:#111;line-height:1.55}
header{background:#1a3a5c;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:20;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
header a{color:#ffd54f;text-decoration:none;font-weight:700}
header a:hover{text-decoration:underline}
.header-search{margin-left:auto}
main{max-width:1200px;margin:0 auto;padding:16px}
h1{margin:0 0 10px;font-size:1.45em}
.layout{display:grid;grid-template-columns:280px 1fr;gap:16px}
.side{position:sticky;top:74px;align-self:start;background:#f0f4f8;border:1px solid #ccd6e0;border-radius:8px;padding:12px}
.side .filter{width:100%;padding:8px;border:1px solid #ccd6e0;border-radius:6px;margin-bottom:8px;background:#fff}
.side nav{display:flex;flex-direction:column;gap:6px;max-height:65vh;overflow:auto}
.side nav a{color:#1a3a5c;text-decoration:none;background:#fff;border:1px solid #ccd6e0;padding:7px 8px;border-radius:6px;font-size:.9em}
.side nav a:hover{background:#dde8f2}
.ctrl{display:flex;gap:8px;align-items:center;margin:8px 0 6px;flex-wrap:wrap}
.ctrl select{padding:6px 8px;border-radius:6px;border:1px solid #ccd6e0;background:#fff}
.note{font-size:.86em;color:#666}
.cat{margin-bottom:26px}
.cat h2{margin:0 0 10px;color:#1a3a5c}
.cards{display:grid;grid-template-columns:1fr;gap:10px}
.duty-card{border:1px solid #ccd6e0;border-radius:8px;padding:10px 12px;background:#fff}
.duty-card h3{margin:0 0 5px;font-size:1.02em}
.ref-count{font-size:.82em;color:#666;margin-bottom:5px}
.refs{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.refs a{font-size:.8em;text-decoration:none;background:#f0f4f8;border:1px solid #ccd6e0;border-radius:999px;padding:2px 8px;color:#1a3a5c}
.refs a:hover{background:#dde8f2}
.sub-list{margin:6px 0 0 18px;padding:0}
.sub-list li{margin:6px 0}
.sub-ref-count{font-size:.8em;color:#666}
.tv{font-size:.9em;color:#2d2d2d;margin-top:4px}
.tv ul{margin:4px 0 0 18px;padding:0}
.tv li{margin:3px 0}
.tv .ref{font-weight:700;color:#1a3a5c}
footer{text-align:center;padding:14px 20px;font-size:.82em;color:#666;border-top:1px solid #e0e0e0;margin-top:28px}
footer a{color:#1a3a5c;text-decoration:none;font-weight:600}
footer a:hover{text-decoration:underline}
@media(max-width:940px){.layout{grid-template-columns:1fr}.side{position:static}}
@media(prefers-color-scheme:dark){
 body{background:#121212;color:#e8e8e8}header{background:#0d2136}
 .side{background:#1e2a3a;border-color:#334}.side .filter,.ctrl select{background:#1a1a1a;border-color:#334;color:#e8e8e8}
 .ctrl button{background:#0d2136!important;border-color:#334!important;color:#90caf9!important}
 .ctrl button:hover{background:#1a3a5c!important}
 .side nav a{background:#1a1a1a;border-color:#334;color:#90caf9}.side nav a:hover{background:#263650}
 .cat h2{color:#90caf9}.duty-card{background:#1a1a1a;border-color:#333}.note,.ref-count,.sub-ref-count{color:#aaa}
 .refs a{background:#1e2a3a;border-color:#334;color:#90caf9}.refs a:hover{background:#263650}
 .tv .ref{color:#90caf9}footer{color:#aaa;border-top-color:#333}footer a{color:#90caf9}
}
</style>
</head>
<body>
<header>
  <a href='../index.html'>&#8962; Index</a>
  <a href='../hadith/index.html'>&#128209; Hadith</a>
  <a class='header-search' href='../config.html' title='Settings'>&#9881;</a>
  <a class='header-search' href='../search.html'>&#128269; Search</a>
</header>
<main>
  <h1>Comprehensive Ethical & Duty Guide</h1>
  <div class='layout'>
    <aside class='side'>
      <label for='fcat' style='font-size:.9em;color:#1a3a5c'>Filter:</label>
      <select id='fcat' class='filter'>__FILTER_OPTS__</select>
      <div class='ctrl'><label for='t'>Translation:</label><select id='t'>__TR_OPTS__</select></div>
      <div class='ctrl'><button id='how-dl' onclick='downloadHowZip()' style='padding:6px 10px;border:1px solid #ccd6e0;border-radius:6px;background:#1a3a5c;color:#fff;cursor:pointer'>&#128229; Download Offline ZIP</button></div>
      <div class='note'>All available translations loaded from <code>output/quran_*.txt</code>. Verse chips open the main reader.</div>
      <nav>__NAV__</nav>
    </aside>
    <div id='content'>__SECTIONS__</div>
  </div>
</main>
<footer><a href='../../index.html'>&#8962; Qur'an Index</a> &nbsp;|&nbsp; <a href='https://github.com/druvx13/Quran-data' rel='noopener noreferrer'>GitHub</a></footer>
<script>
(function(){
  var fcat=document.getElementById('fcat');
  var t=document.getElementById('t');
  var TRANS_CACHE={};

  function refsFrom(el){
    var raw=(el.getAttribute('data-refs')||'').trim();
    if(!raw)return [];
    return raw.split(',').filter(Boolean);
  }
  function renderBox(box){
    if(!box)return;
    var refs=refsFrom(box);
    var key=t.value;
    if(!refs.length){box.innerHTML='';return;}
    var map=TRANS_CACHE[key]||{};
    var out=['<ul>'];
    refs.forEach(function(r){
      var txt=map[r]||'—';
      out.push('<li><span class="ref">['+r+']</span> '+escapeHtml(txt)+'</li>');
    });
    out.push('</ul>');
    box.innerHTML=out.join('');
  }
  function renderAll(){
    document.querySelectorAll('.tv').forEach(renderBox);
  }
  function applyFilter(){
    var v=(fcat&&fcat.value)||'all';
    document.querySelectorAll('.cat').forEach(function(sec){
      sec.style.display=(v==='all'||sec.id===v)?'':'none';
    });
  }
  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g,function(ch){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch];
    });
  }
  if(fcat)fcat.addEventListener('change',applyFilter);
  function loadTranslationAndRender(key){
    if(TRANS_CACHE[key]){renderAll();return;}
    fetch('sd/t/'+key+'.json').then(function(r){return r.json();}).then(function(data){
      TRANS_CACHE[key]=data||{};
      renderAll();
    }).catch(function(){TRANS_CACHE[key]={};renderAll();});
  }
  t.addEventListener('change',function(){
    try{localStorage.setItem('how-trans',t.value);}catch(_){}
    loadTranslationAndRender(t.value);
  });
  try{var sf=localStorage.getItem('how-filter-cat');if(sf&&fcat)fcat.value=sf;}catch(_){}
  if(fcat)fcat.addEventListener('change',function(){try{localStorage.setItem('how-filter-cat',fcat.value);}catch(_){}}); 
  applyFilter();
  try{var sv=localStorage.getItem('how-trans');if(sv)t.value=sv;}catch(_){}
  loadTranslationAndRender(t.value);
})();
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script>
async function downloadHowZip(){
  var btn=document.getElementById('how-dl');
  if(!btn||!window.JSZip)return;
  var old=btn.textContent;
  btn.disabled=true;
  btn.textContent='Preparing ZIP…';
  try{
    var zip=new JSZip();
    var files=['index.html','sd/translations.json'];
    var tr=await fetch('sd/translations.json').then(function(r){return r.json();});
    (tr.translations||[]).forEach(function(t){files.push('sd/t/'+t.key+'.json');});
    for(var i=0;i<files.length;i++){
      btn.textContent='Adding '+(i+1)+'/'+files.length+'…';
      var p=files[i];
      var txt=await fetch(p).then(function(r){return r.text();});
      zip.file('how/'+p,txt);
    }
    var blob=await zip.generateAsync({type:'blob'});
    var a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='quran-how-offline.zip';
    document.body.appendChild(a);a.click();a.remove();
    setTimeout(function(){URL.revokeObjectURL(a.href);},1000);
  }catch(e){
    alert('Failed to build ZIP: '+(e&&e.message?e.message:e));
  }finally{
    btn.disabled=false;
    btn.textContent=old;
  }
}
</script>
</body>
</html>
"""
    html = html.replace('__TR_OPTS__', tr_opts).replace('__FILTER_OPTS__', ''.join(filter_opts)).replace('__NAV__', ''.join(nav)).replace('__SECTIONS__', ''.join(sections))

    with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cats = read_duties(DATA_FILE)
    refs_needed = collect_all_refs(cats)
    ref_store = build_ref_store(refs_needed)
    generate(cats, ref_store)
    print('Written: docs/how/index.html')
    print('Written: docs/how/sd/translations.json')
    print('Written: docs/how/sd/t/*.json')
    print('Categories:', len(cats))
    print('Unique references:', len(refs_needed))
    print('Translations:', len(ref_store['translations']))


if __name__ == '__main__':
    main()
