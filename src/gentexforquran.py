#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate intermediate LaTeX content files from translation data.

Run from the repository root:
    python3 src/gentexforquran.py

Reads source data from data/ and writes generated .tex files to latex/.
"""
import os

os.makedirs('latex', exist_ok=True)

surasize = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
suraname = ["Al-Fatihah (The Opening)","Al-Baqarah (The Cow)","Al-'Imran (The Family of Amran)","An-Nisa' (The Women)","Al-Ma'idah (The Food)","Al-An'am (The Cattle)","Al-A'raf (The Elevated Places)","Al-Anfal (Voluntary Gifts)","Al-Bara'at / At-Taubah(The Immunity)","Yunus (Jonah)","Hud (Hud)","Yusuf (Joseph)","Ar-Ra'd (The Thunder)","Ibrahim (Abraham)","Al-Hijr (The Rock)","An-Nahl (The Bee)","Bani Isra'il (The Israelites)","Al-Kahf (The Cave)","Maryam (Mary)","Ta Ha (Ta Ha)","Al-Anbiya' (The Prophets)","Al-Hajj (The Pilgrimage)","Al-Mu'minun (The Believers)","An-Nur (The Light)","Al-Furqan (The Discrimination)","Ash-Shu'ara' (The Poets)","An-Naml (The Naml)","Al-Qasas (The Narrative)","Al-'Ankabut (The Spider)","Ar-Rum (The Romans)","Luqman (Luqman)","As-Sajdah (The Adoration)","Al-Ahzab (The Allies)","Al-Saba' (The Saba')","Al-Fatir (The Originator)","Ya Sin (Ya Sin)","As-Saffat (Those Ranging in Ranks)","Sad (Sad)","Az-Zumar (The Companies)","Al-Mu'min (The Believer)","Ha Mim (Ha Mim)","Ash-Shura (Counsel)","Az-Zukhruf (Gold)","Ad-Dukhan (The Drought)","Al-Jathiyah (The Kneeling)","Al-Ahqaf (The Sandhills)","Muhammad (Muhammad)","Al-Fath (The Victory)","Al-Hujurat (The Apartments)","Qaf (Qaf)","Ad-Dhariyat (The Scatterers)","At-Tur (The Mountain)","An-Najm (The Star)","Al-Qamar (The Moon)","Ar-Rahman (The Beneficent)","Al-Waqi'ah (The Event)","Al-Hadid (Iron)","Al-Mujadilah (The Pleading Woman)","Al-Hashr (The Banishment)","Al-Mumtahanah (The Woman who is Examined)","As-Saff (The Ranks)","Al-Jumu'ah (The Congregation)","Al-Munafiqun (The Hypocrites)","At-Taghabun (The Manifestation of Losses)","At-Talaq (Divorce)","At-Tahrim (The Prohibition)","Al-Mulk (The Kingdom)","Al-Qalam (The Pen)","Al-Haqqah (The Sure Truth)","Al-Ma'arij (The Ways of Ascent)","Nuh (Noah)","Al-Jinn (The Jinn)","Al-Muzzammil (The One Covering Himself)","Al-Muddaththir (The One Wrapping Himself Up)","Al-Qiyamah (The Resurrection)","Al-Insan (The Man)","Al-Mursalat (Those Sent Forth)","An-Naba' (The Announcement)","An-Nazi'at (Those Who Yearn)","'Abasa (He Frowned)","At-Takwir (The Folding Up)","Al-Infitar (The Cleaving)","At-Tatfif (Default in Duty)","Al-Inshiqaq (The Bursting Asunder)","Al-Buruj (The Stars)","At-Tariq (The Comer by Night)","Al-A'la (The Most High)","Al-Ghashiyah (The Overwhelming Event)","Al-Fajr (The Daybreak)","Al-Balad (The City)","Ash-Shams (The Sun)","Al-Lail (The Night)","Ad-Duha (The Brightness of the Day)","Al-Inshirah (The Expansion)","At-Tin (The Fig)","Al-'Alaq (The Clot)","Al-Qadr (The Majesty)","Al-Bayyinah (The Clear Evidence)","Al-Zilzal (The Shaking)","Al-'Adiyat (The Assaulters)","Al-Qari'ah (The Calamity)","At-Takathur (The Abundance of Wealth)","Al-'Asr (The Time)","Al-Humazah (The Slanderer)","Al-Fil (The Elephant)","Al-Quraish (The Quraish)","Al-Ma'un (Acts of Kindness)","Al-Kauthar (The Abundance of Good)","Al-Kafirun (The Disbelievers)","An-Nasr (The Help)","Al-Lahab (The Flame)","Al-Ikhlas (The Unity)","Al-Falaq (The Dawn)","An-Nas (The Men)"]

# Each entry: (output_tex, input_data, latex_env)
# latex_env='hindi'  → wrap translation in \begin{hindi}...\end{hindi}
# latex_env='english' → emit translation as plain \flushleft{...} (newline stripped)
TARGET_FILES = [
    ('latex/qum.tex',  'data/hi.farooq.txt',         'hindi'),
    ('latex/qup.tex',  'data/hi.hindi.txt',           'hindi'),
    ('latex/qus.tex',  'data/en.sahih.txt',           'english'),
    ('latex/qut.tex',  'data/en.transliteration.txt', 'english'),
    ('latex/qupk.tex', 'data/en.pickthall.txt',       'english'),
]

for out_path, in_path, latex_env in TARGET_FILES:
    with open(out_path, 'w', encoding='utf-8') as out_f, \
         open(in_path, 'r', encoding='utf-8') as in_f:
        for sura_idx in range(114):
            out_f.write("\\chapter{%s}\n" % suraname[sura_idx])
            out_f.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
            for count in range(surasize[sura_idx]):
                out_f.write("\\flushright{\\begin{Arabic}\n")
                out_f.write("\\quranayah[%d][%d]\n" % (sura_idx + 1, count + 1))
                out_f.write("\\end{Arabic}}\n")
                line = in_f.readline()
                if latex_env == 'hindi':
                    out_f.write("\\flushleft{\\begin{hindi}\n")
                    out_f.write(line)
                    out_f.write("\\end{hindi}}\n")
                else:
                    out_f.write("\\flushleft{%s}\n" % line.rstrip('\n'))
    print("Generated: %s" % out_path)

