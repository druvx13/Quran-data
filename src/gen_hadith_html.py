#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a complete Hadith website at docs/hadith/.

Run from the repository root:
    python3 src/gen_hadith_html.py

Downloads/caches Arabic & Hindi editions, then generates:
  docs/hadith/index.html          — collection cards
  docs/hadith/search.html         — full-text search
  docs/hadith/{small}.html        — nawawi, qudsi, dehlawi (all hadiths)
  docs/hadith/{large}/index.html  — book list for bukhari, muslim, etc.
  docs/hadith/{large}/book-N.html — per-book hadith pages
  docs/hadith/sd/                 — search data JSON files
"""

import json
import os
import zipfile
import urllib.request
from collections import defaultdict, OrderedDict

HADITH_BASE_URL = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/'
DATA_DIR = 'data/hadith'
OUT_DIR = 'docs/hadith'

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def fetch_edition(edition_id):
    """Download and cache a hadith edition JSON. Returns the parsed dict."""
    cache_path = os.path.join(DATA_DIR, edition_id + '.json.zip')
    if os.path.exists(cache_path):
        with zipfile.ZipFile(cache_path, 'r') as zf:
            with zf.open(edition_id + '.json') as jf:
                return json.load(jf)
    url = HADITH_BASE_URL + edition_id + '.min.json'
    print('Downloading %s ...' % url)
    raw = urllib.request.urlopen(url, timeout=90).read()
    data = json.loads(raw)
    with zipfile.ZipFile(cache_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(edition_id + '.json', json.dumps(data, ensure_ascii=False))
    return data


# ---------------------------------------------------------------------------
# Collection definitions
# ---------------------------------------------------------------------------

LARGE_COLLECTIONS = [
    ('bukhari',  'Sahih al-Bukhari'),
    ('muslim',   'Sahih Muslim'),
    ('abudawud', 'Sunan Abu Dawud'),
    ('tirmidhi', 'Jami\u02bc at-Tirmidhi'),
    ('ibnmajah', 'Sunan Ibn Majah'),
    ('nasai',    'Sunan an-Nasa\u02bci'),
    ('malik',    'Muwatta Malik'),
]

SMALL_COLLECTIONS = [
    ('nawawi',  'Forty Hadith of an-Nawawi'),
    ('qudsi',   'Forty Hadith Qudsi'),
    ('dehlawi', 'Forty Hadith of Shah Waliullah Dehlawi'),
]

ALL_COLLECTIONS = LARGE_COLLECTIONS + SMALL_COLLECTIONS
LARGE_IDS = {c[0] for c in LARGE_COLLECTIONS}

# ---------------------------------------------------------------------------
# CSS (copied verbatim from gendocshtml.py + hadith-specific additions)
# ---------------------------------------------------------------------------

CSS = """\
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;font-family:system-ui,Arial,Helvetica,sans-serif;
  font-size:16px;background:#fff;color:#111;line-height:1.6}
header{background:#1a3a5c;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
header a{color:#ffd54f;text-decoration:none;font-weight:bold;font-size:1.1em}
header a:hover{text-decoration:underline}
.header-search{margin-left:auto}
main{padding:16px;max-width:900px;margin:0 auto}
h1{font-size:1.4em;margin:0 0 12px}
h2{font-size:1.2em;color:#1a3a5c;margin:20px 0 8px}
.surah-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px;margin-top:16px}
.surah-grid a{display:block;padding:10px 12px;background:#f0f4f8;border:1px solid #ccd6e0;
  border-radius:6px;text-decoration:none;color:#1a3a5c;font-size:.95em}
.surah-grid a:hover{background:#dde8f2}
.sg-meta{display:flex;align-items:center;gap:6px;margin-top:4px;font-size:.78em;color:#555}
.notice{background:#fff8e1;border-left:4px solid #ffd54f;padding:12px 16px;margin-bottom:20px;font-size:.95em}
.notice summary{cursor:pointer}
.table-wrap{overflow-x:auto;width:100%}
table{width:100%;border-collapse:collapse;margin-bottom:24px}
th{background:#1a3a5c;color:#fff;padding:10px 12px;text-align:left;font-size:.9em}
td{padding:8px 12px;vertical-align:top;border:1px solid #ccd6e0}
.ayah-sep td{background:#1a3a5c;color:#fff;font-weight:bold;font-size:.9em;padding:6px 12px;border-color:#1a3a5c}
.hadith-sep td{background:#1a3a5c;color:#fff;font-weight:bold;font-size:.9em;padding:6px 12px;border-color:#1a3a5c}
.label{color:#888;font-size:.82em;white-space:nowrap;width:110px;vertical-align:top}
.hadith-en td{background:#fff}
.hadith-ar td{background:#fff8e1}
.hadith-hi td{background:#f5f0ff}
.arabic-text{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.5em;direction:rtl;text-align:right;line-height:2}
.hindi-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#3a2a6c}
nav.chapter-nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:16px 0;margin-top:8px;border-top:1px solid #ccd6e0}
nav.chapter-nav a{display:inline-block;padding:8px 16px;background:#1a3a5c;color:#fff;
  border-radius:4px;text-decoration:none;font-size:.95em}
nav.chapter-nav a:hover{background:#2a5a8c}
footer{text-align:center;padding:16px 20px;font-size:.82em;color:#666;border-top:1px solid #e0e0e0;margin-top:32px;line-height:1.8}
footer a{color:#1a3a5c;text-decoration:none;font-weight:600}
footer a:hover{text-decoration:underline}
.surah-nav-select{padding:5px 8px;border-radius:4px;border:1px solid #ffd54f;background:#1a3a5c;color:#ffd54f;font-size:.9em;cursor:pointer;max-width:240px}
.surah-nav-select:focus{outline:2px solid #ffd54f;outline-offset:2px}
.verse-chooser{background:#f0f4f8;border:1px solid #ccd6e0;border-radius:6px;margin-bottom:16px}
.verse-chooser summary{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;cursor:pointer;user-select:none;list-style:none;background:#e8eef4;border-radius:6px}
.verse-chooser[open] summary{border-radius:6px 6px 0 0}
.verse-chooser summary::-webkit-details-marker{display:none}
.vc-title{font-size:1em;font-weight:bold;color:#1a3a5c}
.vc-arrow{color:#1a3a5c;transition:transform .2s}
.verse-chooser[open] .vc-arrow{transform:rotate(180deg)}
.vc-body{padding:10px 14px;max-height:340px;overflow-y:auto}
.vc-controls{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.vc-controls button{padding:6px 14px;border:none;border-radius:4px;cursor:pointer;font-size:.88em;background:#1a3a5c;color:#fff;min-height:36px}
.vc-controls button:hover{background:#2a5a8c}
.vc-range{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:6px}
.vc-range label{font-size:.88em;color:#1a3a5c;white-space:nowrap}
.vc-range input[type=number]{width:70px;padding:5px 6px;border:1px solid #ccd6e0;border-radius:4px;font-size:.88em;color:#111;background:#fff}
.vc-range input[type=number]:focus{outline:2px solid #ffd54f;outline-offset:2px}
.vc-section-title{font-size:.82em;font-weight:bold;color:#555;text-transform:uppercase;letter-spacing:.04em;margin:8px 0 4px}
.cf-list{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.cf-item input[type=checkbox]{position:absolute;opacity:0;width:0;height:0}
.cf-item label{display:inline-flex;align-items:center;padding:5px 10px;background:#fff;border:1px solid #ccd6e0;border-radius:4px;cursor:pointer;font-size:.85em;color:#1a3a5c;user-select:none;white-space:nowrap}
.cf-item label:hover{background:#dde8f2}
.cf-item input:checked+label{background:#1a3a5c;color:#fff;border-color:#1a3a5c}
.cf-item input:focus+label{outline:2px solid #ffd54f;outline-offset:2px}
@media(max-width:600px){
  .vc-controls button{min-height:44px}
  .cf-item label{min-height:44px;padding:8px 10px}
  main{padding:10px 8px}
  h1{font-size:1.15em}
  .surah-nav-select{max-width:160px;font-size:.82em}
  .table-wrap thead{display:none}
  .table-wrap table,.table-wrap tbody,.table-wrap tr{display:block;width:100%}
  .table-wrap td{display:block;width:100%;border-left:none;border-right:none;border-bottom:none;box-sizing:border-box}
  .table-wrap .label{padding:5px 10px 1px;font-size:.72em;width:auto;white-space:normal;border-top:2px solid rgba(0,0,0,.07)}
  .table-wrap td:not(.label){padding:2px 10px 8px}
  .table-wrap .hadith-sep td,.table-wrap .ayah-sep td{border:none;padding:7px 10px}
  .arabic-text{font-size:1.25em}
  nav.chapter-nav a{padding:10px 14px;min-height:44px;display:inline-flex;align-items:center}
  footer{font-size:.78em;padding:12px 14px}
}
@media(max-width:380px){
  .surah-grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr))}
  header{padding:8px 10px;gap:8px}
}
.noscript-warn{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 14px;margin-bottom:12px;font-size:.93em;color:#856404}
@media(prefers-color-scheme:dark){
  body{background:#121212;color:#e8e8e8}
  header{background:#0d2136}
  main{color:#e8e8e8}
  h2{color:#90caf9}
  td{border-color:#333;color:#e8e8e8}
  .hadith-sep td,.ayah-sep td{background:#0d2136;border-color:#0d2136}
  .label{color:#aaa}
  .hadith-en td{background:#1a1a1a}
  .hadith-ar td{background:#2a2010}
  .hadith-hi td{background:#1e1530}
  .surah-grid a{background:#1e2a3a;border-color:#334;color:#90caf9}
  .surah-grid a:hover{background:#263650}
  .sg-meta{color:#aaa}
  .notice{background:#2a2010;border-left-color:#ffc107;color:#e8e8e8}
  .verse-chooser{background:#1e2a3a;border-color:#334}
  .verse-chooser summary{background:#162030}
  .vc-title{color:#90caf9}
  .vc-arrow{color:#90caf9}
  .vc-range input[type=number]{background:#1a1a1a;border-color:#334;color:#e8e8e8}
  .cf-item label{background:#1a1a1a;border-color:#334;color:#90caf9}
  .cf-item label:hover{background:#263650}
  .cf-item input:checked+label{background:#1a3a5c;color:#fff}
  footer{color:#aaa;border-top-color:#333}
  footer a{color:#90caf9}
  th{background:#0d2136}
  .hindi-text{color:#b39ddb}
}
@media(max-width:600px) and (prefers-color-scheme:dark){
  .table-wrap .label{border-top-color:rgba(255,255,255,.08)}
}
@media print{
  header,nav.chapter-nav,.verse-chooser,footer{display:none!important}
  body{font-size:11pt;color:#000;background:#fff}
  .table-wrap table,.table-wrap tbody,.table-wrap tr,.table-wrap td{display:table!important}
  .table-wrap tbody{display:table-row-group!important}
  .table-wrap tr{display:table-row!important}
  .table-wrap td{display:table-cell!important;width:auto!important}
  .table-wrap .label{width:110px!important;white-space:nowrap!important}
  td{border-color:#999;color:#000;background:#fff!important}
  .arabic-text{font-size:1.3em}
  .hadith-sep td{background:#ddd!important;color:#000!important}
  tr[data-hadith]{display:table-row!important}
}
@keyframes hadith-pulse{0%{background:#1a3a5c}40%{background:#ffd54f}100%{background:#1a3a5c}}
.hadith-anchor-highlight td{animation:hadith-pulse .8s ease-in-out 3}
.copy-btn{background:none;border:1px solid #ccd6e0;border-radius:4px;
  padding:1px 7px;cursor:pointer;font-size:.75em;color:#888;margin-left:8px;
  vertical-align:middle;line-height:1.4}
.copy-btn:hover{background:#e8eef4;color:#1a3a5c}
.scroll-top-btn{position:fixed;bottom:24px;right:20px;width:42px;height:42px;
  border-radius:50%;background:#1a3a5c;color:#ffd54f;font-size:1.2em;font-weight:bold;
  border:none;cursor:pointer;display:none;align-items:center;justify-content:center;
  box-shadow:0 2px 8px rgba(0,0,0,.3);z-index:100;line-height:1}
.scroll-top-btn:hover{background:#2a5a8c}
.vc-font-ctrl{display:flex;align-items:center;gap:6px;margin-bottom:8px;flex-wrap:wrap}
.vc-font-ctrl span{font-size:.85em;color:#555}
.vc-font-ctrl button{padding:3px 10px;border:1px solid #ccd6e0;border-radius:4px;
  cursor:pointer;font-size:.88em;background:#fff;color:#1a3a5c;min-height:30px}
.vc-font-ctrl button:hover{background:#dde8f2}
.permalink{color:inherit;text-decoration:none;font-weight:bold}
.permalink:hover{text-decoration:underline}
@media(prefers-color-scheme:dark){
  .copy-btn{border-color:#334;color:#90caf9}
  .copy-btn:hover{background:#263650}
  .vc-font-ctrl span{color:#aaa}
  .vc-font-ctrl button{background:#1a1a1a;border-color:#334;color:#90caf9}
  .vc-font-ctrl button:hover{background:#263650}
}"""

COMPACT_FOOTER = ('<footer>'
    '<a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a>'
    ' &nbsp;|&nbsp; '
    '<a href="../index.html">&#8962; Qur\u02bcan Index</a>'
    '</footer>')

COMPACT_FOOTER_TOPLEVEL = ('<footer>'
    '<a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a>'
    ' &nbsp;|&nbsp; '
    '<a href="../../index.html">&#8962; Qur\u02bcan Index</a>'
    '</footer>')

# ---------------------------------------------------------------------------
# JavaScript for hadith pages (adapted from Quran VC_JS)
# ---------------------------------------------------------------------------

def make_hadith_js(has_hindi=False):
    """Generate the JavaScript block for hadith pages."""
    hindi_init = "'hadith-hi':false," if has_hindi else ''
    return """\
<script>
(function(){
  var CF_KEY='hadith-cf';
  var FS_KEY='hfs';
  var cfList=document.getElementById('cf-list');
  var fromInput=document.getElementById('vc-from');
  var toInput=document.getElementById('vc-to');
  var maxHadith=toInput?+toInput.max:0;
  var vcFrom=1,vcTo=maxHadith;
  var enabledTypes=new Set();

  /* ---- Default content filter prefs ---- */
  var DEFAULTS={'hadith-en':true,'hadith-ar':true,""" + hindi_init + """};
  var userPrefs=null;
  try{var raw=localStorage.getItem(CF_KEY);if(raw)userPrefs=JSON.parse(raw);}catch(e){}

  if(cfList){
    cfList.querySelectorAll('input[type=checkbox]').forEach(function(cb){
      var key=cb.dataset.rowclass;
      var on;
      if(userPrefs&&userPrefs.hasOwnProperty(key)){on=userPrefs[key];}
      else{on=DEFAULTS.hasOwnProperty(key)?DEFAULTS[key]:false;}
      cb.checked=on;
      if(on)enabledTypes.add(key);
    });
    cfList.addEventListener('change',function(e){
      if(e.target.type!=='checkbox')return;
      if(e.target.checked)enabledTypes.add(e.target.dataset.rowclass);
      else enabledTypes.delete(e.target.dataset.rowclass);
      saveCfPrefs();
      applyAllRows();
    });
  }
  function saveCfPrefs(){
    if(!cfList)return;
    var prefs={};
    cfList.querySelectorAll('input[type=checkbox]').forEach(function(cb){
      prefs[cb.dataset.rowclass]=cb.checked;
    });
    try{localStorage.setItem(CF_KEY,JSON.stringify(prefs));}catch(e){}
  }
  function applyAllRows(){
    document.querySelectorAll('tr[data-hadith]').forEach(function(tr){
      var h=+tr.dataset.hadith;
      var inRange=(h>=vcFrom&&h<=vcTo);
      if(tr.classList.contains('hadith-sep')){
        tr.style.display=inRange?'':'none';
      }else{
        var typeEnabled=false;
        enabledTypes.forEach(function(t){if(tr.classList.contains(t))typeEnabled=true;});
        tr.style.display=(inRange&&typeEnabled)?'':'none';
      }
    });
  }
  window.vcSelectAll=function(){
    vcFrom=1;vcTo=maxHadith;
    if(fromInput)fromInput.value=1;
    if(toInput)toInput.value=maxHadith;
    applyAllRows();
  };
  window.vcClearAll=function(){
    vcFrom=0;vcTo=0;
    applyAllRows();
  };
  window.vcApplyRange=function(){
    var f=parseInt(fromInput?fromInput.value:'1',10)||1;
    var t=parseInt(toInput?toInput.value:'1',10)||1;
    if(f>t){var tmp=f;f=t;t=tmp;}
    vcFrom=f;vcTo=t;
    if(fromInput)fromInput.value=f;
    if(toInput)toInput.value=t;
    applyAllRows();
  };
  applyAllRows();

  /* ---- Scroll to #h-N anchor ---- */
  (function(){
    var h=location.hash;
    if(h&&/^#h-\\d+$/.test(h)){
      var el=document.getElementById(h.slice(1));
      if(el){
        setTimeout(function(){
          el.scrollIntoView({behavior:'smooth',block:'center'});
          el.classList.add('hadith-anchor-highlight');
          setTimeout(function(){el.classList.remove('hadith-anchor-highlight');},2400);
        },80);
      }
    }
  })();

  /* ---- Font size control ---- */
  var fsSteps=[0.8,0.9,1.0,1.1,1.25,1.4,1.6];
  var fsIdx=2;
  function loadFs(){
    var s=localStorage.getItem(FS_KEY);
    if(s!==null){fsIdx=parseInt(s,10)||2;}
    if(fsIdx<0)fsIdx=0;if(fsIdx>=fsSteps.length)fsIdx=fsSteps.length-1;
  }
  function applyFs(){
    var scale=fsSteps[fsIdx];
    document.querySelectorAll('.arabic-text').forEach(function(el){
      el.style.fontSize=(1.5*scale)+'em';
    });
    document.querySelectorAll('td:not(.label)').forEach(function(el){
      el.style.fontSize=(scale)+'em';
    });
    localStorage.setItem(FS_KEY,fsIdx);
  }
  window.fsIncrease=function(){if(fsIdx<fsSteps.length-1){fsIdx++;applyFs();}};
  window.fsDecrease=function(){if(fsIdx>0){fsIdx--;applyFs();}};
  window.fsReset=function(){fsIdx=2;applyFs();};
  loadFs();
  if(fsIdx!==2)applyFs();

  /* ---- Scroll-to-top button ---- */
  var stb=document.createElement('button');
  stb.className='scroll-top-btn';
  stb.title='Back to top';
  stb.innerHTML='&#8679;';
  stb.onclick=function(){window.scrollTo({top:0,behavior:'smooth'});};
  document.body.appendChild(stb);
  window.addEventListener('scroll',function(){
    stb.style.display=window.scrollY>400?'flex':'none';
  },{passive:true});

  /* ---- Copy hadith ---- */
  window.copyHadith=function(btn,ref){
    var row=btn.closest('tr');
    if(!row)return;
    var tbod=row.parentNode;
    var texts=['['+ref+']'];
    if(tbod){
      var hid=row.dataset.hadith;
      tbod.querySelectorAll('tr[data-hadith="'+hid+'"]').forEach(function(tr){
        if(tr.classList.contains('hadith-sep'))return;
        if(tr.style.display==='none')return;
        var lbl=tr.querySelector('.label');
        var val=tr.cells[1];
        if(lbl&&val)texts.push(lbl.textContent.trim()+': '+val.textContent.trim());
      });
    }
    var text=texts.join('\\n');
    navigator.clipboard&&navigator.clipboard.writeText(text).then(function(){
      btn.textContent='\\u2714';
      setTimeout(function(){btn.textContent='\\u29c9 Copy';},1200);
    });
  };

  /* ---- Permalink click ---- */
  document.querySelectorAll('a.permalink').forEach(function(a){
    a.addEventListener('click',function(e){
      e.preventDefault();
      var url=location.origin+location.pathname+'#h-'+a.dataset.hadith;
      navigator.clipboard&&navigator.clipboard.writeText(url);
      history.replaceState(null,'','#h-'+a.dataset.hadith);
    });
  });
})();
</script>
"""


# ---------------------------------------------------------------------------
# Hadith chooser (filter panel)
# ---------------------------------------------------------------------------

def make_hadith_chooser(size, has_hindi=False):
    """Build the hadith chooser <details> panel."""
    cf_items = [
        ('hadith-en', 'English', True),
        ('hadith-ar', 'Arabic', True),
    ]
    if has_hindi:
        cf_items.append(('hadith-hi', '\u0939\u093f\u0928\u094d\u0926\u0940', False))

    cf_html = []
    for idx, (cls, label, _default) in enumerate(cf_items):
        cf_html.append(
            "<span class='cf-item'>"
            "<input type='checkbox' id='cf-%d' data-rowclass='%s'>"
            "<label for='cf-%d'>%s</label>"
            "</span>" % (idx, cls, idx, label)
        )

    return (
        "<details class='verse-chooser'>"
        "<summary><span class='vc-title'>&#x2714; Hadith &amp; Content Filter</span>"
        "<span class='vc-arrow'>&#x25BC;</span></summary>"
        "<div class='vc-body'>"
        "<div class='vc-font-ctrl'>"
        "<span>Font Size:</span>"
        "<button onclick='fsDecrease()' title='Decrease font size'>A&minus;</button>"
        "<button onclick='fsReset()' title='Reset font size'>A</button>"
        "<button onclick='fsIncrease()' title='Increase font size'>A+</button>"
        "</div>"
        "<div class='vc-section-title'>Hadith Range</div>"
        "<div class='vc-controls'>"
        "<button onclick='vcSelectAll()'>Show All</button>"
        "<button onclick='vcClearAll()'>Hide All</button>"
        "</div>"
        "<div class='vc-range'>"
        "<label>From <input type='number' id='vc-from' min='1' max='%d' value='1'></label>"
        "<label>To <input type='number' id='vc-to' min='1' max='%d' value='%d'></label>"
        "<button onclick='vcApplyRange()'>Apply Range</button>"
        "</div>"
        "<div class='vc-section-title' style='margin-top:12px'>Content</div>"
        "<div class='cf-list' id='cf-list'>%s</div>"
        "</div>"
        "</details>\n"
    ) % (size, size, size, ''.join(cf_html))


# ---------------------------------------------------------------------------
# Book nav select
# ---------------------------------------------------------------------------

def make_book_select(books_list, current_book=None, prefix=''):
    """Build <select> for jumping between books. books_list = [(book_num, book_name), ...]"""
    opts = ["<option value=''>Jump to Book\u2026</option>"]
    for bnum, bname in books_list:
        fname = '%sbook-%d.html' % (prefix, bnum)
        sel = " selected" if bnum == current_book else ''
        opts.append("<option value='%s'%s>%d. %s</option>" % (fname, sel, bnum, bname))
    return (
        "<select class='surah-nav-select' onchange='location.href=this.value'"
        " aria-label='Navigate to Book'>%s</select>" % ''.join(opts)
    )


# ---------------------------------------------------------------------------
# Page header/footer builders
# ---------------------------------------------------------------------------

def page_header(title, header_content, css_extra='', lang='en'):
    """Build the <head> + opening <body> + <header> block."""
    return """\
<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{desc}">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<header>{header}</header>
<main>
""".format(
        lang=lang,
        desc=title,
        title=title,
        css=CSS + css_extra,
        header=header_content,
    )


def page_footer(nav='', script='', compact_footer=None):
    if compact_footer is None:
        compact_footer = COMPACT_FOOTER
    return """\
{nav}
</main>
{footer}
{script}</body>
</html>""".format(nav=nav, footer=compact_footer, script=script)


# ---------------------------------------------------------------------------
# Build books data from a collection
# ---------------------------------------------------------------------------

def build_books(data):
    """Return OrderedDict: book_num -> list of valid hadiths (non-empty text)."""
    sections = data['metadata'].get('sections', {})
    book_names = {}
    for k, v in sections.items():
        if v:
            book_names[int(k)] = v

    books = defaultdict(list)
    for h in data['hadiths']:
        text = h.get('text', '').strip()
        if not text:
            continue
        ref = h.get('reference', {})
        book_num = ref.get('book', 1)
        books[book_num].append(h)

    # Book 0 — include only if it has valid hadiths
    sorted_books = OrderedDict()
    if 0 in books:
        bname = book_names.get(0, '')
        if not bname:
            bname = 'Additional Narrations'
        sorted_books[0] = books[0]

    for bnum in sorted(k for k in books if k != 0):
        sorted_books[bnum] = books[bnum]

    return sorted_books, book_names


def get_book_name(book_num, book_names):
    return book_names.get(book_num, ('Additional Narrations' if book_num == 0 else 'Book %d' % book_num))


def hadith_ref_label(h, book_num):
    """Return 'Book N:M' label for a hadith."""
    ref = h.get('reference', {})
    ref_hadith = ref.get('hadith', 0)
    hnum = ref_hadith if ref_hadith != 0 else h.get('hadithnumber', '?')
    return '[%d:%s]' % (book_num, hnum)


# ---------------------------------------------------------------------------
# HTML row builder for a single hadith
# ---------------------------------------------------------------------------

def hadith_rows(h, seq_in_book, en_text, ar_text, hi_text=None):
    """Return HTML rows for one hadith. seq_in_book is 1-based within the page."""
    hnum = h.get('hadithnumber', seq_in_book)
    ref = h.get('reference', {})
    book_num = ref.get('reference_book', ref.get('book', 1))
    ref_hadith = ref.get('hadith', 0)
    ref_display = ref_hadith if ref_hadith != 0 else hnum
    ref_label = '[%d:%s]' % (book_num, ref_display)

    copy_btn = (
        "<button class='copy-btn' onclick='copyHadith(this,\"%s\")'"
        " title='Copy this hadith'>\u29c9 Copy</button>"
    ) % ref_label

    rows = (
        "<tr class='hadith-sep' data-hadith='%d' id='h-%d'><td colspan='2'>"
        "%s <a class='permalink' href='#h-%d' data-hadith='%d'>Hadith %s</a>"
        "%s</td></tr>\n"
        "<tr class='hadith-en' data-hadith='%d'><td class='label'>English</td><td lang='en'>%s</td></tr>\n"
        "<tr class='hadith-ar' data-hadith='%d'><td class='label'>&#1575;&#1604;&#1593;&#1585;&#1576;&#1610;&#1577;</td><td class='arabic-text' lang='ar'>%s</td></tr>\n"
    ) % (
        seq_in_book, hnum,
        ref_label, hnum, seq_in_book, ref_display,
        copy_btn,
        seq_in_book, en_text,
        seq_in_book, ar_text,
    )

    if hi_text is not None:
        rows += (
            "<tr class='hadith-hi' data-hadith='%d'><td class='label'>&#2361;&#2367;&#2344;&#2381;&#2342;&#2368;</td><td class='hindi-text' lang='hi'>%s</td></tr>\n"
        ) % (seq_in_book, hi_text)

    return rows


# ---------------------------------------------------------------------------
# Generate files counter
# ---------------------------------------------------------------------------
files_written = 0


def write_file(path, content):
    global files_written
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    files_written += 1
    print('Written: %s' % path)


# ---------------------------------------------------------------------------
# Generate a small collection page (single HTML file)
# ---------------------------------------------------------------------------

def gen_small_collection(cid, cname, en_data, ar_data, hi_data=None):
    has_hindi = hi_data is not None
    en_hadiths = {h['hadithnumber']: h for h in en_data['hadiths'] if h.get('text','').strip()}
    ar_map = {}
    if ar_data:
        for h in ar_data['hadiths']:
            ar_map[h['hadithnumber']] = h.get('text', '').strip()
    hi_map = {}
    if hi_data:
        for h in hi_data['hadiths']:
            hi_map[h['hadithnumber']] = h.get('text', '').strip()

    valid_hadiths = sorted(en_hadiths.values(), key=lambda h: h['hadithnumber'])
    size = len(valid_hadiths)

    header_html = (
        "<a href='index.html'>&#8962; Hadith Index</a>"
        " | <strong>%s</strong>"
        " | <a class='header-search' href='search.html'>&#128269; Search</a>"
    ) % cname

    out = page_header(cname + ' \u2014 Hadith', header_html)
    out += '<h1>%s</h1>\n' % cname
    out += '<noscript><p class="noscript-warn">&#9888; The Hadith Filter requires JavaScript. All hadiths are shown below.</p></noscript>\n'
    out += make_hadith_chooser(size, has_hindi=has_hindi)
    out += "<div class='table-wrap'><table><thead><tr><th colspan='2'>%s \u2014 English / Arabic%s</th></tr></thead><tbody>\n" % (
        cname, ' / Hindi' if has_hindi else '')

    for seq, h in enumerate(valid_hadiths, 1):
        hnum = h['hadithnumber']
        en_text = h.get('text', '').strip()
        ar_text = ar_map.get(hnum, '')
        hi_text = hi_map.get(hnum, '') if has_hindi else None
        # embed book_num into reference for row builder
        ref = h.get('reference', {})
        h2 = dict(h)
        h2['reference'] = dict(ref)
        out += hadith_rows(h2, seq, en_text, ar_text, hi_text)

    out += '</tbody></table></div>\n'
    out += page_footer(script=make_hadith_js(has_hindi=has_hindi), compact_footer=COMPACT_FOOTER)

    write_file(os.path.join(OUT_DIR, cid + '.html'), out)


# ---------------------------------------------------------------------------
# Generate a large collection (index + per-book pages)
# ---------------------------------------------------------------------------

def gen_large_collection(cid, cname, en_data, ar_data):
    books, book_names = build_books(en_data)
    ar_books = {}
    if ar_data:
        ar_books_raw, _ = build_books(ar_data)
        # map hadithnumber -> arabic text
        for bnum, hlist in ar_books_raw.items():
            for h in hlist:
                ar_books[h['hadithnumber']] = h.get('text', '').strip()

    coll_dir = os.path.join(OUT_DIR, cid)
    os.makedirs(coll_dir, exist_ok=True)

    books_list = [(bnum, get_book_name(bnum, book_names)) for bnum in books.keys()]
    book_nums = list(books.keys())

    # ---- per-collection index.html ----
    header_html = (
        "<a href='../index.html'>&#8962; Hadith Index</a>"
        " | <strong>%s</strong>"
        " | <a class='header-search' href='../search.html'>&#128269; Search</a>"
    ) % cname

    idx_out = page_header(cname + ' \u2014 Books', header_html, compact_footer=COMPACT_FOOTER_TOPLEVEL)
    idx_out += '<h1>%s</h1>\n' % cname
    idx_out += "<div class='surah-grid'>\n"
    for bnum, bname in books_list:
        hcount = len(books[bnum])
        idx_out += (
            "<a href='book-%d.html'>"
            "<strong>Book %d</strong><br>%s"
            "<span class='sg-meta'><span>%d hadiths</span></span>"
            "</a>\n"
        ) % (bnum, bnum, bname, hcount)
    idx_out += "</div>\n"
    idx_out += page_footer(compact_footer=COMPACT_FOOTER_TOPLEVEL)
    write_file(os.path.join(coll_dir, 'index.html'), idx_out)

    # ---- per-book pages ----
    for book_idx, bnum in enumerate(book_nums):
        bname = get_book_name(bnum, book_names)
        hadiths = books[bnum]
        size = len(hadiths)
        page_title = '%s \u2014 Book %d: %s' % (cname, bnum, bname)

        # prev/next
        prev_link = ''
        next_link = ''
        if book_idx > 0:
            pb = book_nums[book_idx - 1]
            prev_link = "<a href='book-%d.html'>&laquo; Book %d</a>" % (pb, pb)
        if book_idx < len(book_nums) - 1:
            nb = book_nums[book_idx + 1]
            next_link = "<a href='book-%d.html'>Book %d &raquo;</a>" % (nb, nb)
        nav = "<nav class='chapter-nav'><span>%s</span><span>%s</span></nav>" % (prev_link, next_link)

        book_select = make_book_select(books_list, current_book=bnum)
        header_html = (
            "<a href='../index.html'>&#8962; Hadith Index</a>"
            " | <a href='index.html'>%s</a>"
            " | %s"
            " | <a class='header-search' href='../search.html'>&#128269; Search</a>"
        ) % (cname, book_select)

        out = page_header(page_title, header_html, compact_footer=COMPACT_FOOTER_TOPLEVEL)
        out += '<h1>%s \u2014 Book %d: %s</h1>\n' % (cname, bnum, bname)
        out += '<noscript><p class="noscript-warn">&#9888; The Hadith Filter requires JavaScript. All hadiths are shown below.</p></noscript>\n'
        out += make_hadith_chooser(size)
        out += "<div class='table-wrap'><table><thead><tr><th colspan='2'>%s &mdash; Book %d: %s</th></tr></thead><tbody>\n" % (cname, bnum, bname)

        for seq, h in enumerate(hadiths, 1):
            hnum = h['hadithnumber']
            en_text = h.get('text', '').strip()
            ar_text = ar_books.get(hnum, '')
            # embed book_num for label generation
            h2 = dict(h)
            ref = dict(h.get('reference', {}))
            ref['book'] = bnum
            h2['reference'] = ref
            out += hadith_rows(h2, seq, en_text, ar_text)

        out += '</tbody></table></div>\n'
        out += page_footer(nav=nav, script=make_hadith_js(), compact_footer=COMPACT_FOOTER_TOPLEVEL)
        write_file(os.path.join(coll_dir, 'book-%d.html' % bnum), out)


# ---------------------------------------------------------------------------
# Generate docs/hadith/index.html
# ---------------------------------------------------------------------------

def gen_hadith_index(collection_stats):
    """collection_stats: dict cid -> (cname, hadith_count, is_large)"""
    header_html = (
        "<a href='../index.html'>&#8962; Qur\u02bcan</a>"
        " | <strong>&#128209; Hadith Index</strong>"
        " | <a class='header-search' href='search.html'>&#128269; Search</a>"
    )
    out = page_header('Hadith Collections', header_html, compact_footer=COMPACT_FOOTER)
    out += '<h1>&#128209; Hadith Collections</h1>\n'
    out += "<div class='surah-grid'>\n"

    for cid, cname in ALL_COLLECTIONS:
        count, is_large = collection_stats.get(cid, (0, cid in LARGE_IDS))
        if is_large:
            href = '%s/index.html' % cid
        else:
            href = '%s.html' % cid
        out += (
            "<a href='%s'>"
            "<strong>%s</strong>"
            "<span class='sg-meta'><span>%d hadiths</span></span>"
            "</a>\n"
        ) % (href, cname, count)

    out += "</div>\n"
    out += page_footer(compact_footer=COMPACT_FOOTER)
    write_file(os.path.join(OUT_DIR, 'index.html'), out)


# ---------------------------------------------------------------------------
# Generate search data (sd/ files)
# ---------------------------------------------------------------------------

def gen_search_data(all_en_data, all_ar_data, hi_nawawi=None):
    sd_dir = os.path.join(OUT_DIR, 'sd')
    os.makedirs(sd_dir, exist_ok=True)

    for cid, cname in ALL_COLLECTIONS:
        en_data = all_en_data[cid]
        ar_data = all_ar_data.get(cid)

        meta = []
        en_texts = []
        ar_texts = []

        # Build ar lookup
        ar_map = {}
        if ar_data:
            for h in ar_data['hadiths']:
                ar_map[h['hadithnumber']] = h.get('text', '').strip()

        for h in en_data['hadiths']:
            text = h.get('text', '').strip()
            if not text:
                continue
            hnum = h['hadithnumber']
            ref = h.get('reference', {})
            book_num = ref.get('book', 1)
            ref_hadith = ref.get('hadith', 0)
            ref_display = ref_hadith if ref_hadith != 0 else hnum
            ref_label = '%d:%s' % (book_num, ref_display)

            sections = en_data['metadata'].get('sections', {})
            book_name = sections.get(str(book_num), '')
            if not book_name:
                book_name = 'Additional Narrations' if book_num == 0 else 'Book %d' % book_num

            meta.append([hnum, book_num, ref_label, book_name])
            en_texts.append(text)
            ar_texts.append(ar_map.get(hnum, ''))

        def jdump(path, obj):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
            global files_written
            files_written += 1
            print('Written: %s' % path)

        jdump(os.path.join(sd_dir, '%s-meta.json' % cid), meta)
        jdump(os.path.join(sd_dir, '%s-en.json' % cid), en_texts)
        jdump(os.path.join(sd_dir, '%s-ar.json' % cid), ar_texts)

        if cid == 'nawawi' and hi_nawawi:
            hi_map = {h['hadithnumber']: h.get('text','').strip() for h in hi_nawawi['hadiths']}
            hi_texts = []
            for h in en_data['hadiths']:
                if not h.get('text','').strip():
                    continue
                hi_texts.append(hi_map.get(h['hadithnumber'], ''))
            jdump(os.path.join(sd_dir, 'nawawi-hi.json'), hi_texts)


# ---------------------------------------------------------------------------
# Generate search.html
# ---------------------------------------------------------------------------

SEARCH_CSS_EXTRA = """
.search-box{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.search-box input[type=text]{flex:1;min-width:160px;padding:9px 12px;border:1px solid #ccd6e0;border-radius:4px;font-size:1em;color:#111}
.search-box input[type=text]:focus{outline:2px solid #ffd54f;outline-offset:2px}
.search-box button{padding:9px 18px;background:#1a3a5c;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:1em;min-height:44px}
.search-box button:hover{background:#2a5a8c}
.search-filter{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
.search-filter label{font-size:.9em;color:#555}
.search-filter select{padding:6px 10px;border:1px solid #ccd6e0;border-radius:4px;font-size:.9em;color:#111;background:#fff}
#search-status{font-size:.92em;color:#555;margin-bottom:10px}
.result-card{border:1px solid #ccd6e0;border-radius:6px;margin-bottom:12px;overflow:hidden}
.result-header{background:#1a3a5c;color:#fff;padding:7px 12px;font-size:.9em;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:4px}
.result-header a{color:#ffd54f;text-decoration:none;font-weight:bold;white-space:nowrap}
.result-header a:hover{text-decoration:underline}
.result-field{padding:6px 12px;font-size:.95em}
.result-field.hadith-en{background:#fff}
.result-field.hadith-ar{background:#fff8e1;font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.3em;direction:rtl;text-align:right;line-height:2}
.result-field.hadith-hi{background:#f5f0ff;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#3a2a6c}
.result-highlight{background:#fff176;border-radius:2px}
.pagination{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:16px 0;justify-content:center}
.pagination button{padding:7px 14px;border:none;border-radius:4px;cursor:pointer;background:#1a3a5c;color:#fff;font-size:.9em;min-width:36px;min-height:40px}
.pagination button:hover:not(:disabled){background:#2a5a8c}
.pagination button:disabled{background:#ccd6e0;color:#888;cursor:default}
.pagination .pg-current{background:#ffd54f;color:#1a3a5c;font-weight:bold}
.pagination .pg-ellipsis{font-size:.9em;color:#555;padding:0 4px}
@media(prefers-color-scheme:dark){
  .search-box input[type=text]{background:#1a1a1a;border-color:#334;color:#e8e8e8}
  .search-filter select{background:#1a1a1a;border-color:#334;color:#e8e8e8}
  .search-filter label{color:#aaa}
  #search-status{color:#aaa}
  .result-card{border-color:#334}
  .result-header{background:#0d2136}
  .result-field.hadith-en{background:#1a1a1a;color:#e8e8e8}
  .result-field.hadith-ar{background:#2a2010;color:#e8e8e8}
  .result-field.hadith-hi{background:#1e1530;color:#b39ddb}
  .result-highlight{background:#4a4200}
  .pagination button{background:#1a3a5c;color:#fff}
  .pagination button:disabled{background:#333;color:#888}
  .pagination .pg-current{background:#ffd54f;color:#1a3a5c}
}
"""


def gen_search_html():
    # Build collection list JSON for JavaScript
    coll_list = []
    for cid, cname in ALL_COLLECTIONS:
        coll_list.append({'id': cid, 'name': cname, 'large': cid in LARGE_IDS})
    coll_json = json.dumps(coll_list, ensure_ascii=False)

    header_html = (
        "<a href='../index.html'>&#8962; Qur\u02bcan</a>"
        " | <a href='index.html'>&#128209; Hadith</a>"
        " | <strong>&#128269; Search</strong>"
    )

    out = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Search &ndash; Hadith</title>
<style>
{css}
</style>
</head>
<body>
<header>{header}</header>
<main>
<h1>&#128269; Search Hadith Collections</h1>
<div class="search-box">
  <input type="text" id="q" placeholder="e.g. mercy, prayer, fasting&hellip;" autofocus autocomplete="off" spellcheck="false">
  <button onclick="doSearch()">Search</button>
</div>
<div class="search-filter">
  <label for="coll-select">Collection:</label>
  <select id="coll-select">
    <option value="">All collections</option>
    {coll_opts}
  </select>
</div>
<div id="search-status"></div>
<div id="results"></div>
<div id="pagination"></div>
</main>
<footer><a href="https://github.com/druvx13/Quran-data" rel="noopener noreferrer">GitHub</a> &nbsp;|&nbsp; <a href="../index.html">&#8962; Qur&#x02BC;an Index</a></footer>
<script>
(function(){{
  var PAGE_SIZE=20;
  var COLLECTIONS={coll_json};
  var allMatches=[];
  var currentPage=1;
  var currentTerms=[];
  var input=document.getElementById('q');
  var statusEl=document.getElementById('search-status');
  var resultsEl=document.getElementById('results');
  var paginEl=document.getElementById('pagination');
  var collSelect=document.getElementById('coll-select');

  var metaCache={{}};
  var enCache={{}};
  var arCache={{}};
  var hiCache={{}};
  var _pending={{}};

  function fetchJson(url){{
    if(!_pending[url]){{
      _pending[url]=fetch(url).then(function(r){{
        if(!r.ok)throw new Error('HTTP '+r.status+' ('+url+')');
        return r.json();
      }}).catch(function(){{return [];}});
    }}
    return _pending[url];
  }}

  function loadColl(cid){{
    var ps=[];
    if(!metaCache[cid])ps.push(fetchJson('sd/'+cid+'-meta.json').then(function(d){{metaCache[cid]=d;}}));
    if(!enCache[cid])ps.push(fetchJson('sd/'+cid+'-en.json').then(function(d){{enCache[cid]=d;}}));
    if(!arCache[cid])ps.push(fetchJson('sd/'+cid+'-ar.json').then(function(d){{arCache[cid]=d;}}));
    if(cid==='nawawi'&&!hiCache[cid])ps.push(fetchJson('sd/nawawi-hi.json').then(function(d){{hiCache[cid]=d;}}));
    return Promise.all(ps);
  }}

  function makeHref(cid,isLarge,bookNum,hadithnumber){{
    if(isLarge)return cid+'/book-'+bookNum+'.html#h-'+hadithnumber;
    return cid+'.html#h-'+hadithnumber;
  }}

  function escHtml(s){{
    return (''+s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }}
  function highlight(text,terms){{
    var e=escHtml(text);
    terms.forEach(function(t){{
      if(!t)return;
      var re=new RegExp('('+t.replace(/[.*+?^${{}}()|[\\]\\\\]/g,'\\\\$&')+')','gi');
      e=e.replace(re,'<mark class="result-highlight">$1</mark>');
    }});
    return e;
  }}

  function renderPage(page){{
    var total=allMatches.length;
    var totalPages=Math.ceil(total/PAGE_SIZE);
    if(page<1)page=1;
    if(page>totalPages)page=totalPages;
    currentPage=page;
    var start=(page-1)*PAGE_SIZE;
    var end=Math.min(start+PAGE_SIZE,total);
    statusEl.textContent='Showing '+(start+1)+'\u2013'+end+' of '+total+' result(s) for \u201c'+input.value.trim()+'\u201d';
    var html='';
    for(var i=start;i<end;i++){{
      var m=allMatches[i];
      var cname=m.cname;
      var refLabel='['+m.ref+']';
      var href=makeHref(m.cid,m.large,m.book,m.hnum);
      html+='<div class="result-card">'
        +'<div class="result-header"><span>'+escHtml(cname)+' &mdash; '+refLabel+' &mdash; '+escHtml(m.bname)+'</span>'
        +'<a href="'+href+'">View &rarr;</a></div>';
      var en=enCache[m.cid]&&enCache[m.cid][m.idx]||'';
      var ar=arCache[m.cid]&&arCache[m.cid][m.idx]||'';
      var hi=(m.cid==='nawawi'&&hiCache[m.cid]&&hiCache[m.cid][m.idx])||'';
      if(en)html+='<div class="result-field hadith-en">'+highlight(en,currentTerms)+'</div>';
      if(ar)html+='<div class="result-field hadith-ar">'+highlight(ar,currentTerms)+'</div>';
      if(hi)html+='<div class="result-field hadith-hi">'+highlight(hi,currentTerms)+'</div>';
      html+='</div>';
    }}
    resultsEl.innerHTML=html;
    var pgHtml='';
    if(totalPages>1){{
      pgHtml+='<div class="pagination">';
      pgHtml+='<button onclick="goPage('+(page-1)+')"'+(page<=1?' disabled':'')+'>&laquo; Prev</button>';
      var pStart=Math.max(1,page-3),pEnd=Math.min(totalPages,page+3);
      if(pStart>1){{pgHtml+='<button onclick="goPage(1)">1</button>';if(pStart>2)pgHtml+='<span class="pg-ellipsis">&hellip;</span>';}}
      for(var p=pStart;p<=pEnd;p++){{
        if(p===page)pgHtml+='<button class="pg-current" disabled>'+p+'</button>';
        else pgHtml+='<button onclick="goPage('+p+')">'+p+'</button>';
      }}
      if(pEnd<totalPages){{if(pEnd<totalPages-1)pgHtml+='<span class="pg-ellipsis">&hellip;</span>';pgHtml+='<button onclick="goPage('+totalPages+')">'+totalPages+'</button>';}}
      pgHtml+='<button onclick="goPage('+(page+1)+')"'+(page>=totalPages?' disabled':'')+'>Next &raquo;</button>';
      pgHtml+='</div>';
    }}
    paginEl.innerHTML=pgHtml;
  }}

  window.goPage=function(page){{
    renderPage(page);
    resultsEl.scrollIntoView({{behavior:'smooth',block:'start'}});
  }};

  window.doSearch=function(){{
    var q=input.value.trim();
    if(!q){{resultsEl.innerHTML='';statusEl.textContent='';paginEl.innerHTML='';allMatches=[];return;}}
    currentTerms=q.toLowerCase().split(/\\s+/).filter(Boolean);
    var filterCid=collSelect?collSelect.value:'';
    statusEl.textContent='Loading\u2026';
    resultsEl.innerHTML='';
    paginEl.innerHTML='';
    var toLoad=filterCid?COLLECTIONS.filter(function(c){{return c.id===filterCid;}}):COLLECTIONS;
    Promise.all(toLoad.map(function(c){{return loadColl(c.id);}})).then(function(){{
      allMatches=[];
      toLoad.forEach(function(c){{
        var meta=metaCache[c.id]||[];
        var enArr=enCache[c.id]||[];
        var arArr=arCache[c.id]||[];
        var hiArr=(c.id==='nawawi'&&hiCache[c.id])||[];
        for(var i=0;i<meta.length;i++){{
          var row=meta[i];
          var hnum=row[0],book=row[1],ref=row[2],bname=row[3];
          var en=enArr[i]||'';
          var ar=arArr[i]||'';
          var hi=hiArr[i]||'';
          var haystack=(en+' '+ar+' '+hi+' '+bname+' '+c.name).toLowerCase();
          if(currentTerms.every(function(t){{return haystack.indexOf(t)!==-1;}})){{
            allMatches.push({{cid:c.id,cname:c.name,large:c.large,hnum:hnum,book:book,ref:ref,bname:bname,idx:i}});
          }}
        }}
      }});
      if(allMatches.length===0){{statusEl.textContent='No results found.';resultsEl.innerHTML='';paginEl.innerHTML='';return;}}
      renderPage(1);
    }}).catch(function(err){{statusEl.textContent='Error loading search data.';console.error(err);}});
  }};

  input.addEventListener('keydown',function(e){{if(e.key==='Enter')doSearch();}});
  var params=new URLSearchParams(location.search);
  var qs=params.get('q');
  if(qs){{input.value=qs;doSearch();}}

  /* Scroll-to-top */
  var stb=document.createElement('button');
  stb.className='scroll-top-btn';
  stb.title='Back to top';
  stb.innerHTML='&#8679;';
  stb.onclick=function(){{window.scrollTo({{top:0,behavior:'smooth'}});}};
  document.body.appendChild(stb);
  window.addEventListener('scroll',function(){{stb.style.display=window.scrollY>400?'flex':'none';}},{{passive:true}});
}})();
</script>
</body>
</html>""".format(
        css=CSS + SEARCH_CSS_EXTRA,
        header=header_html,
        coll_opts='\n    '.join(
            "<option value='%s'>%s</option>" % (cid, cname)
            for cid, cname in ALL_COLLECTIONS
        ),
        coll_json=coll_json,
    )

    write_file(os.path.join(OUT_DIR, 'search.html'), out)


# ---------------------------------------------------------------------------
# Update docs/index.html and docs/search.html to add Hadith link
# ---------------------------------------------------------------------------

def update_quran_pages():
    index_path = 'docs/index.html'
    search_path = 'docs/search.html'

    for fpath in [index_path, search_path]:
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add Hadith link after the home anchor if not already present
        if 'hadith/index.html' not in content:
            # Find header home link and insert hadith link after it
            old = "<header><a href=\"index.html\">&#8962; Index</a>"
            new = "<header><a href=\"index.html\">&#8962; Index</a> | <a href=\"hadith/index.html\">&#128209; Hadith</a>"
            if old in content:
                content = content.replace(old, new, 1)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print('Updated: %s' % fpath)
            else:
                print('WARN: could not find header anchor in %s to update' % fpath)


# ---------------------------------------------------------------------------
# page_header helper needs compact_footer param removed (it was incorrect)
# Redefine page_header without that param
# ---------------------------------------------------------------------------

def page_header(title, header_content, css_extra='', lang='en', compact_footer=None):
    return """\
<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{desc}">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<header>{header}</header>
<main>
""".format(
        lang=lang,
        desc=title,
        title=title,
        css=CSS + css_extra,
        header=header_content,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print('=== Generating Hadith Website ===')

    # Load all English editions
    print('\n--- Loading English editions ---')
    all_en_data = {}
    for cid, cname in ALL_COLLECTIONS:
        print('Loading eng-%s...' % cid)
        all_en_data[cid] = fetch_edition('eng-' + cid)

    # Load all Arabic editions
    print('\n--- Loading Arabic editions ---')
    all_ar_data = {}
    for cid, cname in ALL_COLLECTIONS:
        print('Loading ara-%s...' % cid)
        try:
            all_ar_data[cid] = fetch_edition('ara-' + cid)
        except Exception as e:
            print('  WARN: could not load ara-%s: %s' % (cid, e))
            all_ar_data[cid] = None

    # Load Hindi nawawi
    print('\n--- Loading Hindi edition (nawawi) ---')
    hi_nawawi = None
    try:
        hi_nawawi = fetch_edition('hin-nawawi')
    except Exception as e:
        print('WARN: could not load hin-nawawi: %s' % e)

    # Compute collection stats for index page
    collection_stats = {}
    for cid, cname in ALL_COLLECTIONS:
        en_data = all_en_data[cid]
        count = sum(1 for h in en_data['hadiths'] if h.get('text', '').strip())
        collection_stats[cid] = (count, cid in LARGE_IDS)

    # Generate hadith index
    print('\n--- Generating docs/hadith/index.html ---')
    gen_hadith_index(collection_stats)

    # Generate small collections
    print('\n--- Generating small collection pages ---')
    for cid, cname in SMALL_COLLECTIONS:
        print('Generating %s...' % cid)
        hi_data = hi_nawawi if cid == 'nawawi' else None
        gen_small_collection(cid, cname, all_en_data[cid], all_ar_data.get(cid), hi_data)

    # Generate large collections
    print('\n--- Generating large collection pages ---')
    for cid, cname in LARGE_COLLECTIONS:
        print('Generating %s...' % cid)
        gen_large_collection(cid, cname, all_en_data[cid], all_ar_data.get(cid))

    # Generate search data
    print('\n--- Generating search data (sd/) ---')
    gen_search_data(all_en_data, all_ar_data, hi_nawawi)

    # Generate search.html
    print('\n--- Generating search.html ---')
    gen_search_html()

    # Update Quran pages
    print('\n--- Updating docs/index.html and docs/search.html ---')
    update_quran_pages()

    print('\n=== Done! %d files written. ===' % files_written)


if __name__ == '__main__':
    main()
