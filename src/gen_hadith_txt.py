#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate formatted plain-text Hadith collection files.

Run from the repository root:
    python3 src/gen_hadith_txt.py

Downloads hadith data from fawazahmed0/hadith-api (jsDelivr CDN),
caches in data/hadith/*.json.zip, and writes output files to output/hadith/.
"""
import json
import os
import zipfile
import urllib.request
from collections import defaultdict

HADITH_BASE_URL = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/'
DATA_DIR = 'data/hadith'
OUT_DIR = 'output/hadith'

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)


def fetch_edition(edition_id):
    """Download and cache a hadith edition JSON.  Returns the parsed dict."""
    cache_path = os.path.join(DATA_DIR, edition_id + '.json.zip')
    if os.path.exists(cache_path):
        with zipfile.ZipFile(cache_path, 'r') as zf:
            with zf.open(edition_id + '.json') as jf:
                return json.load(jf)

    url = HADITH_BASE_URL + edition_id + '.min.json'
    print('Downloading %s ...' % url)
    raw = urllib.request.urlopen(url, timeout=60).read()
    data = json.loads(raw)
    with zipfile.ZipFile(cache_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(edition_id + '.json', json.dumps(data, ensure_ascii=False))
    return data


def write_collection(data, out_file, collection_name):
    """Write a single hadith collection to a plain-text file."""
    sections = data['metadata'].get('sections', {})
    hadiths = data['hadiths']

    # Build book-number → name mapping (skip entry '0' which is blank)
    book_names = {
        int(k): v for k, v in sections.items()
        if k != '0' and v
    }

    with open(out_file, 'w', encoding='utf-8') as out:
        # Header
        out.write('Hadith - English Translation\n')
        out.write('Collection: %s\n' % collection_name)
        out.write('=' * 60 + '\n\n')

        # Group hadiths by book number
        books = defaultdict(list)
        for h in hadiths:
            ref = h.get('reference', {})
            book_num = ref.get('book', 1)
            books[book_num].append(h)

        for book_num in sorted(books.keys()):
            book_title = book_names.get(book_num, 'Book %d' % book_num)
            out.write('Book %d: %s\n' % (book_num, book_title))
            out.write('-' * 40 + '\n')
            for h in books[book_num]:
                ref_hadith = h.get('reference', {}).get('hadith', 0)
                # When reference.hadith is 0 (un-indexed entries), fall back to
                # the global hadithnumber which is always a unique identifier.
                hadith_num = ref_hadith if ref_hadith != 0 else h.get('hadithnumber', '?')
                text = h.get('text', '').strip()
                if text:
                    out.write('[%d:%s] %s\n' % (book_num, hadith_num, text))
            out.write('\n')

    print('Generated: %s' % out_file)


# ---------------------------------------------------------------------------
# Collection definitions
# ---------------------------------------------------------------------------
# Each entry: (edition_id, output_filename, collection_name)
COLLECTIONS = [
    # Large collections (multiple books)
    ('eng-bukhari',   'hadith_english_bukhari.txt',   'Sahih al-Bukhari'),
    ('eng-muslim',    'hadith_english_muslim.txt',    'Sahih Muslim'),
    ('eng-abudawud',  'hadith_english_abudawud.txt',  'Sunan Abu Dawud'),
    ('eng-tirmidhi',  'hadith_english_tirmidhi.txt',  'Jami at-Tirmidhi'),
    ('eng-ibnmajah',  'hadith_english_ibnmajah.txt',  'Sunan Ibn Majah'),
    ('eng-nasai',     'hadith_english_nasai.txt',     'Sunan an-Nasai'),
    ('eng-malik',     'hadith_english_malik.txt',     'Muwatta Malik'),
    # Small collections (single section)
    ('eng-nawawi',    'hadith_english_nawawi.txt',    'Forty Hadith of an-Nawawi'),
    ('eng-qudsi',     'hadith_english_qudsi.txt',     'Forty Hadith Qudsi'),
    ('eng-dehlawi',   'hadith_english_dehlawi.txt',   'Forty Hadith of Shah Waliullah Dehlawi'),
]

for edition_id, out_name, coll_name in COLLECTIONS:
    edition_data = fetch_edition(edition_id)
    out_path = os.path.join(OUT_DIR, out_name)
    write_collection(edition_data, out_path, coll_name)
