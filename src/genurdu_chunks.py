#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split the Urdu Quran translation into 50-line chunk files.

Run from the repository root:
    python3 src/genurdu_chunks.py

Reads data/ur.jalandhry.txt (6,236 lines, one ayah per line) and writes
chunk files to output/urdu/part_001.txt, part_002.txt, ... one file per
50 lines, yielding 125 files in total.
"""
import os

INPUT_FILE = 'data/ur.jalandhry.txt'
OUTPUT_DIR = 'output/urdu'
CHUNK_SIZE = 50

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
chunk_num = 1
for start in range(0, total_lines, CHUNK_SIZE):
    chunk_lines = lines[start:start + CHUNK_SIZE]
    out_path = os.path.join(OUTPUT_DIR, 'part_%03d.txt' % chunk_num)
    with open(out_path, 'w', encoding='utf-8') as out:
        out.writelines(chunk_lines)
    chunk_num += 1

total_chunks = chunk_num - 1
print("Split %d lines into %d chunk files in %s/" % (total_lines, total_chunks, OUTPUT_DIR))
