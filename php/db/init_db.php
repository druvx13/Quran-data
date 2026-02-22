<?php
/**
 * init_db.php — One-time database initialiser for the Qur'an PHP site.
 *
 * Run from the /php directory (or anywhere) as:
 *
 *     php db/init_db.php
 *
 * Reads the bundled text files from data/ and imports all 6 236 verses
 * into an SQLite database at db/quran.sqlite.
 *
 * Safe to re-run: drops and recreates all tables each time.
 */

require_once __DIR__ . '/../includes/config.php';

$db_file = DB_PATH;
$data    = DATA_DIR;

// -----------------------------------------------------------------------
// Helper: emit a progress line (works both from CLI and a browser)
// -----------------------------------------------------------------------
function log_line(string $msg): void {
    if (PHP_SAPI === 'cli') {
        echo $msg . "\n";
    } else {
        echo nl2br(htmlspecialchars($msg)) . "<br>\n";
        if (ob_get_level()) ob_flush();
        flush();
    }
}

// -----------------------------------------------------------------------
// Open / create the SQLite database
// -----------------------------------------------------------------------
log_line('Opening database: ' . $db_file);
$pdo = new PDO('sqlite:' . $db_file);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Performance pragmas for bulk insert
$pdo->exec('PRAGMA journal_mode=WAL;');
$pdo->exec('PRAGMA synchronous=NORMAL;');
$pdo->exec('PRAGMA temp_store=MEMORY;');
$pdo->exec('PRAGMA cache_size=10000;');

// -----------------------------------------------------------------------
// Create tables
// -----------------------------------------------------------------------
$pdo->exec('DROP TABLE IF EXISTS verses');
$pdo->exec('DROP TABLE IF EXISTS surahs');

$pdo->exec('
CREATE TABLE surahs (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    verse_count INTEGER NOT NULL
)');

$pdo->exec('
CREATE TABLE verses (
    surah_id          INTEGER NOT NULL,
    ayah_id           INTEGER NOT NULL,
    arabic            TEXT,
    translit          TEXT,
    translit_unicode  TEXT,
    pickthall         TEXT,
    yusufali          TEXT,
    sahih             TEXT,
    eng_abridged      TEXT,
    hindi             TEXT,
    hindi_suhail      TEXT,
    hindi_mokhtasar   TEXT,
    gujarati          TEXT,
    PRIMARY KEY (surah_id, ayah_id),
    FOREIGN KEY (surah_id) REFERENCES surahs(id)
)');

// Full-text-search virtual table (FTS5) for fast searching
$pdo->exec('
CREATE VIRTUAL TABLE IF NOT EXISTS verses_fts USING fts5(
    surah_id UNINDEXED,
    ayah_id  UNINDEXED,
    arabic,
    translit_unicode,
    yusufali,
    hindi_mokhtasar,
    content=verses,
    content_rowid=rowid
)');

log_line('Tables created.');

// -----------------------------------------------------------------------
// Populate surahs table
// -----------------------------------------------------------------------
$ins_surah = $pdo->prepare('INSERT INTO surahs (id, name, verse_count) VALUES (?,?,?)');
foreach (SURA_NAME as $id => $name) {
    $ins_surah->execute([$id, $name, surah_size($id)]);
}
log_line('Inserted 114 surah records.');

// -----------------------------------------------------------------------
// Helper parsers
// -----------------------------------------------------------------------

/**
 * Parse a file with lines:  [sura:ayah] text
 * Returns: $data[$sura][$ayah] = $text
 */
function parse_bracket(string $path): array {
    $data = [];
    $fh   = fopen($path, 'r');
    if (!$fh) { log_line("WARNING: cannot open $path"); return $data; }
    while (($line = fgets($fh)) !== false) {
        $line = rtrim($line, "\r\n");
        if (!preg_match('/^\[(\d+):(\d+)\]\s*(.*)$/', $line, $m)) continue;
        $data[(int)$m[1]][(int)$m[2]] = $m[3];
    }
    fclose($fh);
    return $data;
}

/**
 * Parse the Tanzil transliteration file:  sura|ayah|text
 * Returns: $data[$sura][$ayah] = $text
 */
function parse_translit(string $path): array {
    $data = [];
    $fh   = fopen($path, 'r');
    if (!$fh) { log_line("WARNING: cannot open $path"); return $data; }
    while (($line = fgets($fh)) !== false) {
        $line = rtrim($line, "\r\n");
        if ($line === '' || $line[0] === '#') continue;
        $parts = explode('|', $line, 3);
        if (count($parts) === 3) {
            $data[(int)$parts[0]][(int)$parts[1]] = $parts[2];
        }
    }
    fclose($fh);
    return $data;
}

// -----------------------------------------------------------------------
// Load all data sources
// -----------------------------------------------------------------------
log_line('Loading data files …');
$arabic          = parse_bracket($data . 'quran_arabic.txt');
$translit        = parse_translit($data . 'en.transliteration.txt');
$translit_u      = parse_bracket($data . 'quran_translit_unicode.txt');
$pickthall       = parse_bracket($data . 'quran_english_pickthall.txt');
$yusufali        = parse_bracket($data . 'quran_english_yusufali.txt');
$sahih           = parse_bracket($data . 'quran_english_sahih.txt');
$eng_abridged    = parse_bracket($data . 'quran_english_abridged.txt');
$hindi           = parse_bracket($data . 'quran_hindi_farooq.txt');
$hindi_suhail    = parse_bracket($data . 'quran_hindi_suhail.txt');
$hindi_mokhtasar = parse_bracket($data . 'quran_hindi_mokhtasar.txt');
$gujarati        = parse_bracket($data . 'quran_gujarati_rabila.txt');
log_line('All data files loaded.');

// -----------------------------------------------------------------------
// Insert verses in a single transaction
// -----------------------------------------------------------------------
$ins = $pdo->prepare('
    INSERT INTO verses
        (surah_id, ayah_id, arabic, translit, translit_unicode,
         pickthall, yusufali, sahih, eng_abridged,
         hindi, hindi_suhail, hindi_mokhtasar, gujarati)
    VALUES
        (:s,:a,:ar,:tl,:tu,:pk,:ya,:sa,:ea,:hi,:hs,:hm,:gu)
');

$pdo->beginTransaction();
$total = 0;
for ($s = 1; $s <= 114; $s++) {
    $size = surah_size($s);
    for ($a = 1; $a <= $size; $a++) {
        $ins->execute([
            ':s'  => $s,
            ':a'  => $a,
            ':ar' => $arabic[$s][$a]          ?? '',
            ':tl' => $translit[$s][$a]         ?? '',
            ':tu' => $translit_u[$s][$a]       ?? '',
            ':pk' => $pickthall[$s][$a]        ?? '',
            ':ya' => $yusufali[$s][$a]         ?? '',
            ':sa' => $sahih[$s][$a]            ?? '',
            ':ea' => $eng_abridged[$s][$a]     ?? '',
            ':hi' => $hindi[$s][$a]            ?? '',
            ':hs' => $hindi_suhail[$s][$a]     ?? '',
            ':hm' => $hindi_mokhtasar[$s][$a]  ?? '',
            ':gu' => $gujarati[$s][$a]         ?? '',
        ]);
        $total++;
    }
}
$pdo->commit();
log_line("Inserted {$total} verse records.");

// -----------------------------------------------------------------------
// Populate the FTS5 index
// -----------------------------------------------------------------------
$pdo->exec("INSERT INTO verses_fts(verses_fts) VALUES('rebuild')");
log_line('FTS5 index built.');

// -----------------------------------------------------------------------
// Create indexes for common queries
// -----------------------------------------------------------------------
$pdo->exec('CREATE INDEX IF NOT EXISTS idx_verses_surah ON verses(surah_id)');
log_line('Indexes created.');

log_line('');
log_line('Database initialised successfully: ' . $db_file);
log_line('File size: ' . number_format(filesize($db_file) / 1048576, 2) . ' MB');
