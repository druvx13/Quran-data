#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate formatted plain-text Quran translation files.

Run from the repository root:
    python3 src/gentxtforquran.py

Reads source data from data/ and writes output files to output/.
"""
import json
import os
import zipfile

os.makedirs('output', exist_ok=True)

surasize = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
suraname = ["Al-Fatihah (The Opening)","Al-Baqarah (The Cow)","Al-'Imran (The Family of Amran)","An-Nisa' (The Women)","Al-Ma'idah (The Food)","Al-An'am (The Cattle)","Al-A'raf (The Elevated Places)","Al-Anfal (Voluntary Gifts)","Al-Bara'at / At-Taubah(The Immunity)","Yunus (Jonah)","Hud (Hud)","Yusuf (Joseph)","Ar-Ra'd (The Thunder)","Ibrahim (Abraham)","Al-Hijr (The Rock)","An-Nahl (The Bee)","Bani Isra'il (The Israelites)","Al-Kahf (The Cave)","Maryam (Mary)","Ta Ha (Ta Ha)","Al-Anbiya' (The Prophets)","Al-Hajj (The Pilgrimage)","Al-Mu'minun (The Believers)","An-Nur (The Light)","Al-Furqan (The Discrimination)","Ash-Shu'ara' (The Poets)","An-Naml (The Naml)","Al-Qasas (The Narrative)","Al-'Ankabut (The Spider)","Ar-Rum (The Romans)","Luqman (Luqman)","As-Sajdah (The Adoration)","Al-Ahzab (The Allies)","Al-Saba' (The Saba')","Al-Fatir (The Originator)","Ya Sin (Ya Sin)","As-Saffat (Those Ranging in Ranks)","Sad (Sad)","Az-Zumar (The Companies)","Al-Mu'min (The Believer)","Ha Mim (Ha Mim)","Ash-Shura (Counsel)","Az-Zukhruf (Gold)","Ad-Dukhan (The Drought)","Al-Jathiyah (The Kneeling)","Al-Ahqaf (The Sandhills)","Muhammad (Muhammad)","Al-Fath (The Victory)","Al-Hujurat (The Apartments)","Qaf (Qaf)","Ad-Dhariyat (The Scatterers)","At-Tur (The Mountain)","An-Najm (The Star)","Al-Qamar (The Moon)","Ar-Rahman (The Beneficent)","Al-Waqi'ah (The Event)","Al-Hadid (Iron)","Al-Mujadilah (The Pleading Woman)","Al-Hashr (The Banishment)","Al-Mumtahanah (The Woman who is Examined)","As-Saff (The Ranks)","Al-Jumu'ah (The Congregation)","Al-Munafiqun (The Hypocrites)","At-Taghabun (The Manifestation of Losses)","At-Talaq (Divorce)","At-Tahrim (The Prohibition)","Al-Mulk (The Kingdom)","Al-Qalam (The Pen)","Al-Haqqah (The Sure Truth)","Al-Ma'arij (The Ways of Ascent)","Nuh (Noah)","Al-Jinn (The Jinn)","Al-Muzzammil (The One Covering Himself)","Al-Muddaththir (The One Wrapping Himself Up)","Al-Qiyamah (The Resurrection)","Al-Insan (The Man)","Al-Mursalat (Those Sent Forth)","An-Naba' (The Announcement)","An-Nazi'at (Those Who Yearn)","'Abasa (He Frowned)","At-Takwir (The Folding Up)","Al-Infitar (The Cleaving)","At-Tatfif (Default in Duty)","Al-Inshiqaq (The Bursting Asunder)","Al-Buruj (The Stars)","At-Tariq (The Comer by Night)","Al-A'la (The Most High)","Al-Ghashiyah (The Overwhelming Event)","Al-Fajr (The Daybreak)","Al-Balad (The City)","Ash-Shams (The Sun)","Al-Lail (The Night)","Ad-Duha (The Brightness of the Day)","Al-Inshirah (The Expansion)","At-Tin (The Fig)","Al-'Alaq (The Clot)","Al-Qadr (The Majesty)","Al-Bayyinah (The Clear Evidence)","Al-Zilzal (The Shaking)","Al-'Adiyat (The Assaulters)","Al-Qari'ah (The Calamity)","At-Takathur (The Abundance of Wealth)","Al-'Asr (The Time)","Al-Humazah (The Slanderer)","Al-Fil (The Elephant)","Al-Quraish (The Quraish)","Al-Ma'un (Acts of Kindness)","Al-Kauthar (The Abundance of Good)","Al-Kafirun (The Disbelievers)","An-Nasr (The Help)","Al-Lahab (The Flame)","Al-Ikhlas (The Unity)","Al-Falaq (The Dawn)","An-Nas (The Men)"]

translations = [
    ('data/hi.farooq.txt', 'output/quran_hindi_farooq.txt', 'Muhammad Farooq Khan and Muhammad Ahmed', 'Hindi'),
    ('data/hi.hindi.txt', 'output/quran_hindi_suhail.txt', 'Suhel Farooq Khan and Saifur Rahman Nadwi', 'Hindi'),
    ('data/en.sahih.txt', 'output/quran_english_sahih.txt', 'Saheeh International', 'English'),
    ('data/en.transliteration.txt', 'output/quran_english_translit.txt', 'Tanzil.net', 'Transliteration'),
    ('data/en.pickthall.txt', 'output/quran_english_pickthall.txt', 'Mohammed Marmaduke Pickthall', 'English'),
    ('data/en.yusufali.txt', 'output/quran_english_yusufali.txt', 'Abdullah Yusuf Ali', 'English-Piped'),
    ('data/ar.quran.txt', 'output/quran_arabic.txt', 'Standard Arabic Uthmani Script', 'Arabic'),
    ('data/translit_en.txt', 'output/quran_translit_unicode.txt', 'Quran Unicode Project', 'Transliteration-Sequential'),
    ('data/hindi-mokhtasar.json.zip', 'output/quran_hindi_mokhtasar.txt', 'Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim', 'Hindi-Tafsir-JSON'),
    ('data/abridged-explanation-of-the-quran.json.zip', 'output/quran_english_abridged.txt', 'Abridged Explanation of the Quran', 'English-Tafsir-JSON'),
    ('data/rabila-al-umry-simple.json.zip', 'output/quran_gujarati_rabila.txt', 'Rabila Al-Umry', 'Gujarati-JSON'),
    ('data/en.qarai.txt', 'output/quran_english_qarai.txt', 'Ali Quli Qarai', 'English-SuraAyah'),
    ('data/en.hilali.txt', 'output/quran_english_hilali.txt', 'Dr. Muhammad Taqi-ud-Din Al-Hilali & Dr. Muhammad Muhsin Khan', 'English-SuraAyah'),
    ('data/ahl-al-hadith-central-society-of-nepal-simple.json.zip', 'output/quran_nepali_ahl_al_hadith.txt', 'Ahl-al-Hadith Central Society of Nepal', 'Nepali-JSON'),
]

for src_file, out_file, translator, lang in translations:
    with open(out_file, 'w', encoding='utf-8') as out:
        if lang in ('Transliteration', 'Transliteration-Sequential'):
            out.write("Quran - English Transliteration\n")
            out.write("Source: %s\n" % translator)
        elif lang in ('English', 'English-Piped', 'English-SuraAyah'):
            out.write("Quran - English Translation\n")
            out.write("Translator: %s\n" % translator)
        elif lang == 'Arabic':
            out.write("Quran - Arabic\n")
            out.write("Script: %s\n" % translator)
        elif lang == 'Hindi':
            out.write("Quran - Hindi Anuvad\n")
            out.write("Anuvadak: %s\n" % translator)
        elif lang == 'Hindi-Tafsir-JSON':
            out.write("Quran - Hindi Tafsir\n")
            out.write("Tafseer: %s\n" % translator)
        elif lang == 'English-Tafsir-JSON':
            out.write("Quran - English Explanation\n")
            out.write("Source: %s\n" % translator)
        elif lang == 'Gujarati-JSON':
            out.write("Quran - Gujarati Bhashantar\n")
            out.write("Bhashantar: %s\n" % translator)
        elif lang == 'Nepali-JSON':
            out.write("Quran - Nepali Anuvad\n")
            out.write("Anuvadak: %s\n" % translator)
        out.write("=" * 60 + "\n\n")
        if lang in ('Hindi-Tafsir-JSON', 'English-Tafsir-JSON'):
            with zipfile.ZipFile(src_file, 'r') as zf:
                json_name = next(n for n in zf.namelist() if n.endswith('.json'))
                with zf.open(json_name) as jf:
                    ayah_data = json.load(jf)
            for sura_num in range(114):
                out.write("Surah %d: %s\n" % (sura_num + 1, suraname[sura_num]))
                out.write("-" * 40 + "\n")
                for ayah_num in range(1, surasize[sura_num] + 1):
                    key = "%d:%d" % (sura_num + 1, ayah_num)
                    entry = ayah_data.get(key, {})
                    if isinstance(entry, str):
                        entry = ayah_data.get(entry, {})
                    text = entry.get('text', '') if isinstance(entry, dict) else ''
                    out.write("[%d:%d] %s\n" % (sura_num + 1, ayah_num, text))
                out.write("\n")
        elif lang == 'Gujarati-JSON':
            with zipfile.ZipFile(src_file, 'r') as zf:
                json_name = next(n for n in zf.namelist() if n.endswith('.json'))
                with zf.open(json_name) as jf:
                    ayah_data = json.load(jf)
            for sura_num in range(114):
                out.write("Surah %d: %s\n" % (sura_num + 1, suraname[sura_num]))
                out.write("-" * 40 + "\n")
                for ayah_num in range(1, surasize[sura_num] + 1):
                    key = "%d:%d" % (sura_num + 1, ayah_num)
                    entry = ayah_data.get(key, {})
                    text = entry.get('t', '') if isinstance(entry, dict) else ''
                    out.write("[%d:%d] %s\n" % (sura_num + 1, ayah_num, text))
                out.write("\n")
        elif lang == 'Nepali-JSON':
            with zipfile.ZipFile(src_file, 'r') as zf:
                json_name = next(n for n in zf.namelist() if n.endswith('.json'))
                with zf.open(json_name) as jf:
                    ayah_data = json.load(jf)
            for sura_num in range(114):
                out.write("Surah %d: %s\n" % (sura_num + 1, suraname[sura_num]))
                out.write("-" * 40 + "\n")
                for ayah_num in range(1, surasize[sura_num] + 1):
                    key = "%d:%d" % (sura_num + 1, ayah_num)
                    entry = ayah_data.get(key, {})
                    text = entry.get('t', '') if isinstance(entry, dict) else ''
                    out.write("[%d:%d] %s\n" % (sura_num + 1, ayah_num, text))
                out.write("\n")
        elif lang == 'Transliteration-Sequential':
            with open(src_file, 'r', encoding='utf-8') as src:
                # Parse num|text format with sequential global ayah numbers
                for sura_num in range(114):
                    out.write("Surah %d: %s\n" % (sura_num + 1, suraname[sura_num]))
                    out.write("-" * 40 + "\n")
                    for ayah_num in range(1, surasize[sura_num] + 1):
                        raw_line = src.readline().rstrip('\n')
                        text = raw_line.split('|', 1)[1] if '|' in raw_line else ''
                        out.write("[%d:%d] %s\n" % (sura_num + 1, ayah_num, text))
                    out.write("\n")
        elif lang in ('English-SuraAyah', 'English-Piped'):
            with open(src_file, 'r', encoding='utf-8') as src:
                for sura_num in range(114):
                    out.write("Surah %d: %s\n" % (sura_num + 1, suraname[sura_num]))
                    out.write("-" * 40 + "\n")
                    for ayah_num in range(1, surasize[sura_num] + 1):
                        raw_line = src.readline().rstrip('\n')
                        text = raw_line.split('|', 2)[2] if raw_line.count('|') >= 2 else raw_line
                        out.write("[%d:%d] %s\n" % (sura_num + 1, ayah_num, text))
                    out.write("\n")
        else:
            with open(src_file, 'r', encoding='utf-8') as src:
                for sura_num in range(114):
                    out.write("Surah %d: %s\n" % (sura_num + 1, suraname[sura_num]))
                    out.write("-" * 40 + "\n")
                    for ayah_num in range(1, surasize[sura_num] + 1):
                        line = src.readline().rstrip('\n')
                        out.write("[%d:%d] %s\n" % (sura_num + 1, ayah_num, line))
                    out.write("\n")
    print("Generated: %s" % out_file)
