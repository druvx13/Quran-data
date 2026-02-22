<?php
/**
 * loader.php — Functions to parse Qur'an data files and return verse data.
 *
 * All public functions accept a surah number (1–114) and return an array
 * keyed by ayah number, or a flat array of all verses for search use.
 */

require_once __DIR__ . '/config.php';

/**
 * Parse a file with lines in the format:
 *   [sura:ayah] text
 * and return an array [$sura][$ayah] => $text.
 * When $sura_filter > 0, only lines for that surah are included.
 */
function parse_bracket_file(string $path, int $sura_filter = 0): array {
    $data = [];
    $fh = @fopen($path, 'r');
    if ($fh === false) return $data;
    while (($line = fgets($fh)) !== false) {
        $line = rtrim($line, "\r\n");
        if (!preg_match('/^\[(\d+):(\d+)\]\s*(.*)$/', $line, $m)) continue;
        $s = (int)$m[1];
        $a = (int)$m[2];
        if ($sura_filter > 0 && $s !== $sura_filter) {
            // Once we've passed the target surah, stop reading
            if ($s > $sura_filter) break;
            continue;
        }
        $data[$s][$a] = $m[3];
    }
    fclose($fh);
    return $data;
}

/**
 * Parse the Tanzil transliteration file (trans/en.transliteration.txt).
 * Format: sura|ayah|text_with_html_tags  (comment lines start with #)
 * Returns array [$sura][$ayah] => $text.
 */
function parse_translit_file(string $path, int $sura_filter = 0): array {
    $data = [];
    $fh = @fopen($path, 'r');
    if ($fh === false) return $data;
    while (($line = fgets($fh)) !== false) {
        $line = rtrim($line, "\r\n");
        if ($line === '' || $line[0] === '#') continue;
        $parts = explode('|', $line, 3);
        if (count($parts) !== 3) continue;
        $s = (int)$parts[0];
        $a = (int)$parts[1];
        if ($sura_filter > 0 && $s !== $sura_filter) {
            if ($s > $sura_filter) break;
            continue;
        }
        $data[$s][$a] = $parts[2];
    }
    fclose($fh);
    return $data;
}

/**
 * Load all verse data for a single surah.
 * Returns an array indexed by ayah number (1-based) where each element is an
 * associative array with keys: arabic, translit, translit_unicode, pickthall,
 * yusufali, sahih, eng_abridged, hindi, hindi_suhail, hindi_mokhtasar, gujarati.
 */
function load_surah_verses(int $sura): array {
    $size = surah_size($sura);
    if ($size === 0) return [];

    // Load each data source for this surah only
    $arabic          = parse_bracket_file(OUTPUT_DIR . 'quran_arabic.txt',           $sura)[$sura] ?? [];
    $translit_u      = parse_bracket_file(OUTPUT_DIR . 'quran_translit_unicode.txt',  $sura)[$sura] ?? [];
    $pickthall       = parse_bracket_file(OUTPUT_DIR . 'quran_english_pickthall.txt', $sura)[$sura] ?? [];
    $yusufali        = parse_bracket_file(OUTPUT_DIR . 'quran_english_yusufali.txt',  $sura)[$sura] ?? [];
    $sahih           = parse_bracket_file(OUTPUT_DIR . 'quran_english_sahih.txt',     $sura)[$sura] ?? [];
    $eng_abridged    = parse_bracket_file(OUTPUT_DIR . 'quran_english_abridged.txt',  $sura)[$sura] ?? [];
    $hindi           = parse_bracket_file(OUTPUT_DIR . 'quran_hindi_farooq.txt',      $sura)[$sura] ?? [];
    $hindi_suhail    = parse_bracket_file(OUTPUT_DIR . 'quran_hindi_suhail.txt',      $sura)[$sura] ?? [];
    $hindi_mokhtasar = parse_bracket_file(OUTPUT_DIR . 'quran_hindi_mokhtasar.txt',   $sura)[$sura] ?? [];
    $gujarati        = parse_bracket_file(OUTPUT_DIR . 'quran_gujarati_rabila.txt',   $sura)[$sura] ?? [];
    $translit        = parse_translit_file(TRANS_DIR  . 'en.transliteration.txt',     $sura)[$sura] ?? [];

    $verses = [];
    for ($a = 1; $a <= $size; $a++) {
        $verses[$a] = [
            'arabic'          => $arabic[$a]          ?? '',
            'translit'        => $translit[$a]         ?? '',
            'translit_unicode'=> $translit_u[$a]       ?? '',
            'pickthall'       => $pickthall[$a]        ?? '',
            'yusufali'        => $yusufali[$a]         ?? '',
            'sahih'           => $sahih[$a]            ?? '',
            'eng_abridged'    => $eng_abridged[$a]     ?? '',
            'hindi'           => $hindi[$a]            ?? '',
            'hindi_suhail'    => $hindi_suhail[$a]     ?? '',
            'hindi_mokhtasar' => $hindi_mokhtasar[$a]  ?? '',
            'gujarati'        => $gujarati[$a]         ?? '',
        ];
    }
    return $verses;
}

/**
 * Load a lightweight dataset for all 6236 ayahs for the search page.
 * Returns an array of rows: [sura, ayah, surah_name, arabic, translit_unicode,
 * yusufali, hindi_mokhtasar].
 */
function load_search_data(): array {
    $arabic          = parse_bracket_file(OUTPUT_DIR . 'quran_arabic.txt');
    $translit_u      = parse_bracket_file(OUTPUT_DIR . 'quran_translit_unicode.txt');
    $yusufali        = parse_bracket_file(OUTPUT_DIR . 'quran_english_yusufali.txt');
    $hindi_mokhtasar = parse_bracket_file(OUTPUT_DIR . 'quran_hindi_mokhtasar.txt');

    $rows = [];
    for ($s = 1; $s <= 114; $s++) {
        $size = surah_size($s);
        $name = surah_name($s);
        for ($a = 1; $a <= $size; $a++) {
            $rows[] = [
                'sura'            => $s,
                'ayah'            => $a,
                'name'            => $name,
                'arabic'          => $arabic[$s][$a]          ?? '',
                'translit_unicode'=> $translit_u[$s][$a]      ?? '',
                'yusufali'        => $yusufali[$s][$a]        ?? '',
                'hindi_mokhtasar' => $hindi_mokhtasar[$s][$a] ?? '',
            ];
        }
    }
    return $rows;
}
