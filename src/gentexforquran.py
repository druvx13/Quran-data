#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate intermediate LaTeX content files from translation data.

Run from the repository root:
    python3 src/gentexforquran.py

Reads source data from data/ and writes generated .tex files to latex/.
"""
import os

os.makedirs('latex', exist_ok=True)

surasize=[7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
suraname=["Al-Fatihah (The Opening)","Al-Baqarah (The Cow)","Al-'Imran (The Family of Amran)","An-Nisa' (The Women)","Al-Ma'idah (The Food)","Al-An'am (The Cattle)","Al-A'raf (The Elevated Places)","Al-Anfal (Voluntary Gifts)","Al-Bara'at / At-Taubah(The Immunity)","Yunus (Jonah)","Hud (Hud)","Yusuf (Joseph)","Ar-Ra'd (The Thunder)","Ibrahim (Abraham)","Al-Hijr (The Rock)","An-Nahl (The Bee)","Bani Isra'il (The Israelites)","Al-Kahf (The Cave)","Maryam (Mary)","Ta Ha (Ta Ha)","Al-Anbiya' (The Prophets)","Al-Hajj (The Pilgrimage)","Al-Mu'minun (The Believers)","An-Nur (The Light)","Al-Furqan (The Discrimination)","Ash-Shu'ara' (The Poets)","An-Naml (The Naml)","Al-Qasas (The Narrative)","Al-'Ankabut (The Spider)","Ar-Rum (The Romans)","Luqman (Luqman)","As-Sajdah (The Adoration)","Al-Ahzab (The Allies)","Al-Saba' (The Saba')","Al-Fatir (The Originator)","Ya Sin (Ya Sin)","As-Saffat (Those Ranging in Ranks)","Sad (Sad)","Az-Zumar (The Companies)","Al-Mu'min (The Believer)","Ha Mim (Ha Mim)","Ash-Shura (Counsel)","Az-Zukhruf (Gold)","Ad-Dukhan (The Drought)","Al-Jathiyah (The Kneeling)","Al-Ahqaf (The Sandhills)","Muhammad (Muhammad)","Al-Fath (The Victory)","Al-Hujurat (The Apartments)","Qaf (Qaf)","Ad-Dhariyat (The Scatterers)","At-Tur (The Mountain)","An-Najm (The Star)","Al-Qamar (The Moon)","Ar-Rahman (The Beneficent)","Al-Waqi'ah (The Event)","Al-Hadid (Iron)","Al-Mujadilah (The Pleading Woman)","Al-Hashr (The Banishment)","Al-Mumtahanah (The Woman who is Examined)","As-Saff (The Ranks)","Al-Jumu'ah (The Congregation)","Al-Munafiqun (The Hypocrites)","At-Taghabun (The Manifestation of Losses)","At-Talaq (Divorce)","At-Tahrim (The Prohibition)","Al-Mulk (The Kingdom)","Al-Qalam (The Pen)","Al-Haqqah (The Sure Truth)","Al-Ma'arij (The Ways of Ascent)","Nuh (Noah)","Al-Jinn (The Jinn)","Al-Muzzammil (The One Covering Himself)","Al-Muddaththir (The One Wrapping Himself Up)","Al-Qiyamah (The Resurrection)","Al-Insan (The Man)","Al-Mursalat (Those Sent Forth)","An-Naba' (The Announcement)","An-Nazi'at (Those Who Yearn)","'Abasa (He Frowned)","At-Takwir (The Folding Up)","Al-Infitar (The Cleaving)","At-Tatfif (Default in Duty)","Al-Inshiqaq (The Bursting Asunder)","Al-Buruj (The Stars)","At-Tariq (The Comer by Night)","Al-A'la (The Most High)","Al-Ghashiyah (The Overwhelming Event)","Al-Fajr (The Daybreak)","Al-Balad (The City)","Ash-Shams (The Sun)","Al-Lail (The Night)","Ad-Duha (The Brightness of the Day)","Al-Inshirah (The Expansion)","At-Tin (The Fig)","Al-'Alaq (The Clot)","Al-Qadr (The Majesty)","Al-Bayyinah (The Clear Evidence)","Al-Zilzal (The Shaking)","Al-'Adiyat (The Assaulters)","Al-Qari'ah (The Calamity)","At-Takathur (The Abundance of Wealth)","Al-'Asr (The Time)","Al-Humazah (The Slanderer)","Al-Fil (The Elephant)","Al-Quraish (The Quraish)","Al-Ma'un (Acts of Kindness)","Al-Kauthar (The Abundance of Good)","Al-Kafirun (The Disbelievers)","An-Nasr (The Help)","Al-Lahab (The Flame)","Al-Ikhlas (The Unity)","Al-Falaq (The Dawn)","An-Nas (The Men)"]

with open('latex/qum.tex', 'w') as farooq_out, \
     open('data/hi.farooq.txt', 'r') as farooq_in:
    for sura_idx in range(114):
        farooq_out.write("\\chapter{%s}\n" % (suraname[sura_idx]) )
        farooq_out.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        count=0
        while(count<surasize[sura_idx]):
            farooq_out.write("\\flushright{\\begin{Arabic}\n")
            farooq_out.write("\\quranayah[%d][%d]\n" %(sura_idx+1,count+1))
            farooq_out.write("\\end{Arabic}}\n")
            count=count+1
            translation_line=farooq_in.readline()
            farooq_out.write("\\flushleft{\\begin{hindi}\n")
            farooq_out.write(translation_line)
            farooq_out.write("\\end{hindi}}\n")

with open('latex/qup.tex', 'w') as suhail_out, \
     open('data/hi.hindi.txt', 'r') as suhail_in:
    for sura_idx in range(114):
        suhail_out.write("\\chapter{%s}\n" % (suraname[sura_idx]) )
        suhail_out.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        count=0
        while(count<surasize[sura_idx]):
            suhail_out.write("\\flushright{\\begin{Arabic}\n")
            suhail_out.write("\\quranayah[%d][%d]\n" %(sura_idx+1,count+1))
            suhail_out.write("\\end{Arabic}}\n")
            count=count+1
            translation_line=suhail_in.readline()
            suhail_out.write("\\flushleft{\\begin{hindi}\n")
            suhail_out.write(translation_line)
            suhail_out.write("\\end{hindi}}\n")

with open('latex/qus.tex','w') as targetu, open('data/en.sahih.txt','r', encoding='utf-8') as transu:
    for sura_idx in range(114):
        targetu.write("\\chapter{%s}\n" % (suraname[sura_idx]) )
        targetu.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        count=0
        while(count<surasize[sura_idx]):
            targetu.write("\\flushright{\\begin{Arabic}\n")
            targetu.write("\\quranayah[%d][%d]\n" %(sura_idx+1,count+1))
            targetu.write("\\end{Arabic}}\n")
            count=count+1
            translation_line=transu.readline()
            targetu.write("\\flushleft{%s}\n" % translation_line.rstrip('\n'))

with open('latex/qut.tex','w') as targett, open('data/en.transliteration.txt','r', encoding='utf-8') as transt:
    for sura_idx in range(114):
        targett.write("\\chapter{%s}\n" % (suraname[sura_idx]) )
        targett.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        count=0
        while(count<surasize[sura_idx]):
            targett.write("\\flushright{\\begin{Arabic}\n")
            targett.write("\\quranayah[%d][%d]\n" %(sura_idx+1,count+1))
            targett.write("\\end{Arabic}}\n")
            count=count+1
            translation_line=transt.readline()
            targett.write("\\flushleft{%s}\n" % translation_line.rstrip('\n'))

with open('latex/qupk.tex','w') as targetpk, open('data/en.pickthall.txt','r', encoding='utf-8') as transpk:
    for sura_idx in range(114):
        targetpk.write("\\chapter{%s}\n" % (suraname[sura_idx]) )
        targetpk.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        count=0
        while(count<surasize[sura_idx]):
            targetpk.write("\\flushright{\\begin{Arabic}\n")
            targetpk.write("\\quranayah[%d][%d]\n" %(sura_idx+1,count+1))
            targetpk.write("\\end{Arabic}}\n")
            count=count+1
            translation_line=transpk.readline()
            targetpk.write("\\flushleft{%s}\n" % translation_line.rstrip('\n'))

import json, zipfile

with zipfile.ZipFile('data/hindi-mokhtasar.json.zip', 'r') as zf:
    json_name = next(n for n in zf.namelist() if n.endswith('.json'))
    with zf.open(json_name) as jf:
        mokhtasar_data = json.load(jf)

with open('latex/qumokhtasar.tex', 'w', encoding='utf-8') as mokhtasar_out, \
     open('data/translit_en.txt', 'r', encoding='utf-8') as translit_in:
    for sura_idx in range(114):
        mokhtasar_out.write("\\chapter{%s}\n" % (suraname[sura_idx]))
        mokhtasar_out.write("\\begin{Arabic}\n\\Huge{\\centerline{\\basmalah}}\\end{Arabic}\n")
        count = 0
        while count < surasize[sura_idx]:
            mokhtasar_out.write("\\flushright{\\begin{Arabic}\n")
            mokhtasar_out.write("\\quranayah[%d][%d]\n" % (sura_idx + 1, count + 1))
            mokhtasar_out.write("\\end{Arabic}}\n")
            count += 1
            raw_line = translit_in.readline().rstrip('\n')
            translit_text = raw_line.split('|', 1)[1] if '|' in raw_line else raw_line
            translit_text = translit_text.replace('_', '\\_')
            mokhtasar_out.write("\\flushleft{\\textit{%s}}\n" % translit_text)
            key = "%d:%d" % (sura_idx + 1, count)
            entry = mokhtasar_data.get(key, {})
            if isinstance(entry, str):
                entry = mokhtasar_data.get(entry, {})
            hindi_text = entry.get('text', '') if isinstance(entry, dict) else ''
            hindi_text = hindi_text.replace('{', '\\{').replace('}', '\\}')
            mokhtasar_out.write("\\flushleft{\\begin{hindi}\n")
            mokhtasar_out.write(hindi_text + "\n")
            mokhtasar_out.write("\\end{hindi}}\n")


