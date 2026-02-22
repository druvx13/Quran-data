<?php
/**
 * loader.php — SQLite-backed data access for the Qur'an PHP site.
 *
 * All queries go to the local SQLite database (db/quran.sqlite).
 * Run db/init_db.php once to build the database from the bundled
 * text files in data/.  After that the site has zero external
 * file dependencies.
 */

require_once __DIR__ . '/config.php';

/**
 * Return a shared PDO connection to the SQLite database.
 * Throws a RuntimeException if the database has not been initialised yet.
 */
function get_db(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        if (!file_exists(DB_PATH)) {
            throw new RuntimeException(
                'Database not found. Please run <code>php db/init_db.php</code> first.'
            );
        }
        $pdo = new PDO('sqlite:' . DB_PATH);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        $pdo->exec('PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;');
    }
    return $pdo;
}

/**
 * Load all verses for a single surah from SQLite.
 * Returns array indexed by ayah number (1-based); each element is an
 * associative array with all content columns.
 */
function load_surah_verses(int $sura): array {
    $db   = get_db();
    $stmt = $db->prepare(
        'SELECT ayah_id, arabic, translit, translit_unicode,
                pickthall, yusufali, sahih, eng_abridged,
                hindi, hindi_suhail, hindi_mokhtasar, gujarati
         FROM   verses
         WHERE  surah_id = :s
         ORDER  BY ayah_id'
    );
    $stmt->execute([':s' => $sura]);
    $rows = [];
    foreach ($stmt->fetchAll() as $row) {
        $rows[(int)$row['ayah_id']] = $row;
    }
    return $rows;
}

/**
 * Full-text search across Arabic, Unicode transliteration, Yusuf Ali
 * translation, and Hindi Mokhtasar tafsir.
 *
 * Uses SQLite LIKE for broad compatibility (no FTS5 required).
 * Returns an array of result rows, each with keys:
 *   surah_id, ayah_id, surah_name, arabic, translit_unicode,
 *   yusufali, hindi_mokhtasar
 *
 * $terms is an array of lowercase search tokens (all must match).
 */
function search_verses(array $terms, int $limit = 500): array {
    if (empty($terms)) return [];

    $db = get_db();

    // Build WHERE clause: every term must appear in the concatenated haystack.
    // Keys are constructed as ':t' . $i (always a safe integer-derived string).
    $conditions = [];
    $params     = [];
    foreach ($terms as $i => $term) {
        $key = ':t' . $i;
        // Search across four columns; LOWER() for case-insensitive matching
        $conditions[] =
            "(LOWER(v.arabic) LIKE {$key}"
            . " OR LOWER(v.translit_unicode) LIKE {$key}"
            . " OR LOWER(v.yusufali) LIKE {$key}"
            . " OR LOWER(v.hindi_mokhtasar) LIKE {$key}"
            . " OR LOWER(s.name) LIKE {$key})";
        $params[$key] = '%' . $term . '%';
    }
    $where = implode(' AND ', $conditions);

    $sql = "SELECT v.surah_id, v.ayah_id, s.name AS surah_name,
                   v.arabic, v.translit_unicode, v.yusufali, v.hindi_mokhtasar
            FROM   verses v
            JOIN   surahs s ON s.id = v.surah_id
            WHERE  {$where}
            ORDER  BY v.surah_id, v.ayah_id
            LIMIT  :lim";

    $stmt = $db->prepare($sql);
    foreach ($params as $k => $v) {
        $stmt->bindValue($k, $v, PDO::PARAM_STR);
    }
    $stmt->bindValue(':lim', $limit, PDO::PARAM_INT);
    $stmt->execute();
    return $stmt->fetchAll();
}
