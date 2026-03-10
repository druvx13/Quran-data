<?php
/**
 * config.php — Configuration and surah metadata for the Qur'an PHP site.
 *
 * All paths are relative to the /php directory so the site is fully
 * self-contained and portable to any LAMP/LEMP server.
 */

// Absolute path to the /php directory (works wherever the site is deployed)
define('PHP_ROOT', dirname(__DIR__) . '/');

// Bundled plain-text data files (imported once by db/init_db.php)
define('DATA_DIR', PHP_ROOT . 'data/');

// SQLite database path (created by db/init_db.php)
define('DB_PATH',  PHP_ROOT . 'db/quran.sqlite');

// -----------------------------------------------------------------------
// Surah verse counts (114 entries, accessed as SURA_SIZE[0..113])
// -----------------------------------------------------------------------
const SURA_SIZE = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,
    110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,
    182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,
    29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,
    40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,
    11,11,8,3,9,5,4,7,3,6,3,5,4,5,6];

// Surah names indexed 1–114
const SURA_NAME = [
    1=>"Al-Fatihah (The Opening)",2=>"Al-Baqarah (The Cow)",
    3=>"Al-'Imran (The Family of Amran)",4=>"An-Nisa' (The Women)",
    5=>"Al-Ma'idah (The Food)",6=>"Al-An'am (The Cattle)",
    7=>"Al-A'raf (The Elevated Places)",8=>"Al-Anfal (Voluntary Gifts)",
    9=>"Al-Bara'at / At-Taubah(The Immunity)",10=>"Yunus (Jonah)",
    11=>"Hud (Hud)",12=>"Yusuf (Joseph)",13=>"Ar-Ra'd (The Thunder)",
    14=>"Ibrahim (Abraham)",15=>"Al-Hijr (The Rock)",16=>"An-Nahl (The Bee)",
    17=>"Bani Isra'il (The Israelites)",18=>"Al-Kahf (The Cave)",
    19=>"Maryam (Mary)",20=>"Ta Ha (Ta Ha)",
    21=>"Al-Anbiya' (The Prophets)",22=>"Al-Hajj (The Pilgrimage)",
    23=>"Al-Mu'minun (The Believers)",24=>"An-Nur (The Light)",
    25=>"Al-Furqan (The Discrimination)",26=>"Ash-Shu'ara' (The Poets)",
    27=>"An-Naml (The Naml)",28=>"Al-Qasas (The Narrative)",
    29=>"Al-'Ankabut (The Spider)",30=>"Ar-Rum (The Romans)",
    31=>"Luqman (Luqman)",32=>"As-Sajdah (The Adoration)",
    33=>"Al-Ahzab (The Allies)",34=>"Al-Saba' (The Saba')",
    35=>"Al-Fatir (The Originator)",36=>"Ya Sin (Ya Sin)",
    37=>"As-Saffat (Those Ranging in Ranks)",38=>"Sad (Sad)",
    39=>"Az-Zumar (The Companies)",40=>"Al-Mu'min (The Believer)",
    41=>"Ha Mim (Ha Mim)",42=>"Ash-Shura (Counsel)",
    43=>"Az-Zukhruf (Gold)",44=>"Ad-Dukhan (The Drought)",
    45=>"Al-Jathiyah (The Kneeling)",46=>"Al-Ahqaf (The Sandhills)",
    47=>"Muhammad (Muhammad)",48=>"Al-Fath (The Victory)",
    49=>"Al-Hujurat (The Apartments)",50=>"Qaf (Qaf)",
    51=>"Ad-Dhariyat (The Scatterers)",52=>"At-Tur (The Mountain)",
    53=>"An-Najm (The Star)",54=>"Al-Qamar (The Moon)",
    55=>"Ar-Rahman (The Beneficent)",56=>"Al-Waqi'ah (The Event)",
    57=>"Al-Hadid (Iron)",58=>"Al-Mujadilah (The Pleading Woman)",
    59=>"Al-Hashr (The Banishment)",
    60=>"Al-Mumtahanah (The Woman who is Examined)",
    61=>"As-Saff (The Ranks)",62=>"Al-Jumu'ah (The Congregation)",
    63=>"Al-Munafiqun (The Hypocrites)",
    64=>"At-Taghabun (The Manifestation of Losses)",
    65=>"At-Talaq (Divorce)",66=>"At-Tahrim (The Prohibition)",
    67=>"Al-Mulk (The Kingdom)",68=>"Al-Qalam (The Pen)",
    69=>"Al-Haqqah (The Sure Truth)",70=>"Al-Ma'arij (The Ways of Ascent)",
    71=>"Nuh (Noah)",72=>"Al-Jinn (The Jinn)",
    73=>"Al-Muzzammil (The One Covering Himself)",
    74=>"Al-Muddaththir (The One Wrapping Himself Up)",
    75=>"Al-Qiyamah (The Resurrection)",76=>"Al-Insan (The Man)",
    77=>"Al-Mursalat (Those Sent Forth)",78=>"An-Naba' (The Announcement)",
    79=>"An-Nazi'at (Those Who Yearn)",80=>"'Abasa (He Frowned)",
    81=>"At-Takwir (The Folding Up)",82=>"Al-Infitar (The Cleaving)",
    83=>"At-Tatfif (Default in Duty)",84=>"Al-Inshiqaq (The Bursting Asunder)",
    85=>"Al-Buruj (The Stars)",86=>"At-Tariq (The Comer by Night)",
    87=>"Al-A'la (The Most High)",88=>"Al-Ghashiyah (The Overwhelming Event)",
    89=>"Al-Fajr (The Daybreak)",90=>"Al-Balad (The City)",
    91=>"Ash-Shams (The Sun)",92=>"Al-Lail (The Night)",
    93=>"Ad-Duha (The Brightness of the Day)",
    94=>"Al-Inshirah (The Expansion)",95=>"At-Tin (The Fig)",
    96=>"Al-'Alaq (The Clot)",97=>"Al-Qadr (The Majesty)",
    98=>"Al-Bayyinah (The Clear Evidence)",99=>"Al-Zilzal (The Shaking)",
    100=>"Al-'Adiyat (The Assaulters)",101=>"Al-Qari'ah (The Calamity)",
    102=>"At-Takathur (The Abundance of Wealth)",103=>"Al-'Asr (The Time)",
    104=>"Al-Humazah (The Slanderer)",105=>"Al-Fil (The Elephant)",
    106=>"Al-Quraish (The Quraish)",107=>"Al-Ma'un (Acts of Kindness)",
    108=>"Al-Kauthar (The Abundance of Good)",
    109=>"Al-Kafirun (The Disbelievers)",110=>"An-Nasr (The Help)",
    111=>"Al-Lahab (The Flame)",112=>"Al-Ikhlas (The Unity)",
    113=>"Al-Falaq (The Dawn)",114=>"An-Nas (The Men)",
];

/** Return verse count for surah $n (1–114). */
function surah_size(int $n): int {
    return SURA_SIZE[$n - 1] ?? 0;
}

/** Return surah name for surah $n (1–114). */
function surah_name(int $n): string {
    return SURA_NAME[$n] ?? '';
}
