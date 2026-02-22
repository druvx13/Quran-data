<?php
/**
 * search.php — Server-side Qur'an search.
 *
 * Searches Arabic text, Unicode transliteration, Yusuf Ali translation,
 * and Hindi Mokhtasar tafsir via SQLite LIKE queries.
 *
 * URL parameters:
 *   q    — search query
 *   page — result page number (default 1)
 */
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/loader.php';

// -----------------------------------------------------------------------
// Input handling
// -----------------------------------------------------------------------
$raw_query = trim($_GET['q'] ?? '');
$page      = max(1, (int)($_GET['page'] ?? 1));
$per_page  = 20;

$results    = [];
$total      = 0;
$db_error   = '';
$terms      = [];
$did_search = false;

if ($raw_query !== '') {
    $did_search = true;
    // Split into individual tokens, lowercase
    $terms = array_values(array_filter(array_map('trim', explode(' ', mb_strtolower($raw_query)))));
    try {
        // Fetch all matches (capped at 2000 for safety) then paginate in PHP
        $all_results = search_verses($terms, 2000);
        $total       = count($all_results);
        $offset      = ($page - 1) * $per_page;
        $results     = array_slice($all_results, $offset, $per_page);
    } catch (RuntimeException $e) {
        $db_error = $e->getMessage();
    }
}

$total_pages = $total > 0 ? (int)ceil($total / $per_page) : 0;

// -----------------------------------------------------------------------
// Page metadata
// -----------------------------------------------------------------------
$page_title   = 'Search &ndash; Qur&rsquo;an';
$current_sura = 0;

require __DIR__ . '/includes/header.php';

// -----------------------------------------------------------------------
// Helper: highlight matched terms in a text string
// -----------------------------------------------------------------------
function highlight(string $text, array $terms): string {
    $escaped = htmlspecialchars($text, ENT_QUOTES);
    foreach ($terms as $term) {
        if ($term === '') continue;
        $pat     = preg_quote($term, '/');
        $escaped = preg_replace(
            '/(' . $pat . ')/iu',
            '<mark class="result-highlight">$1</mark>',
            $escaped
        );
    }
    return $escaped;
}

// -----------------------------------------------------------------------
// Helper: build pagination URL
// -----------------------------------------------------------------------
function page_url(int $p): string {
    return 'search.php?q=' . urlencode($_GET['q'] ?? '') . '&page=' . $p;
}
?>
<main>
<h1>&#128269; Search the Qur&#x2019;an</h1>
<p style="font-size:.93em;color:#555;margin-bottom:14px">
  Search Arabic text, transliteration, English translation (Yusuf Ali), or
  &#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Hindi Tafsir).
  Results link directly to the verse.
</p>

<!-- Search form -->
<form method="get" action="search.php" class="search-box">
  <input type="text" name="q" id="q"
         placeholder="e.g. mercy, rahman, bismillah&hellip;"
         value="<?= htmlspecialchars($raw_query, ENT_QUOTES) ?>"
         autofocus autocomplete="off" spellcheck="false">
  <button type="submit">Search</button>
</form>

<?php if (!empty($db_error)): ?>
<div class="notice" style="background:#ffe0e0;border-left-color:#c00">
  <strong>Database error:</strong> <?= htmlspecialchars($db_error) ?><br>
  Please run <code>php db/init_db.php</code> to initialise the database.
</div>

<?php elseif ($did_search && $total === 0): ?>
<p id="search-status">No results found for &ldquo;<?= htmlspecialchars($raw_query) ?>&rdquo;.</p>

<?php elseif ($did_search): ?>
<p id="search-status">
  Showing <?= number_format(($page - 1) * $per_page + 1) ?>–<?= number_format(min($page * $per_page, $total)) ?>
  of <?= number_format($total) ?> result(s) for
  &ldquo;<?= htmlspecialchars($raw_query) ?>&rdquo;
</p>

<!-- Result cards -->
<?php foreach ($results as $row):
    $s    = (int)$row['surah_id'];
    $a    = (int)$row['ayah_id'];
    $name = $row['surah_name'];
    $ar   = $row['arabic']           ?? '';
    $tu   = $row['translit_unicode'] ?? '';
    $ya   = $row['yusufali']         ?? '';
    $hm   = $row['hindi_mokhtasar']  ?? '';
    $href = 'surah.php?s=' . $s . '#ayah-' . $a;
?>
<div class="result-card">
  <div class="result-header">
    <span>Surah <?= $s ?>:<?= $a ?> &mdash; <?= htmlspecialchars($name) ?></span>
    <a href="<?= $href ?>">View verse &rarr;</a>
  </div>
  <?php if ($ar !== ''): ?>
  <div class="result-arabic"><?= highlight($ar, $terms) ?></div>
  <?php endif; ?>
  <?php if ($tu !== ''): ?>
  <div class="result-translit"><?= highlight($tu, $terms) ?></div>
  <?php endif; ?>
  <?php if ($ya !== ''): ?>
  <div class="result-trans"><?= highlight($ya, $terms) ?></div>
  <?php endif; ?>
  <?php if ($hm !== ''): ?>
  <div class="result-hindi-mokhtasar"><?= highlight($hm, $terms) ?></div>
  <?php endif; ?>
</div>
<?php endforeach; ?>

<!-- Pagination -->
<?php if ($total_pages > 1): ?>
<div class="pagination">
  <?php if ($page > 1): ?>
    <a href="<?= page_url($page - 1) ?>">&laquo; Prev</a>
  <?php else: ?>
    <span class="pg-disabled">&laquo; Prev</span>
  <?php endif; ?>

  <?php
  $p_start = max(1, $page - 3);
  $p_end   = min($total_pages, $page + 3);
  if ($p_start > 1):
  ?><a href="<?= page_url(1) ?>">1</a><?php
    if ($p_start > 2) echo '<span class="pg-ellipsis">&hellip;</span>';
  endif;
  for ($p = $p_start; $p <= $p_end; $p++):
    if ($p === $page):
  ?><span class="pg-current"><?= $p ?></span><?php
    else:
  ?><a href="<?= page_url($p) ?>"><?= $p ?></a><?php
    endif;
  endfor;
  if ($p_end < $total_pages):
    if ($p_end < $total_pages - 1) echo '<span class="pg-ellipsis">&hellip;</span>';
  ?><a href="<?= page_url($total_pages) ?>"><?= $total_pages ?></a><?php
  endif;
  ?>

  <?php if ($page < $total_pages): ?>
    <a href="<?= page_url($page + 1) ?>">Next &raquo;</a>
  <?php else: ?>
    <span class="pg-disabled">Next &raquo;</span>
  <?php endif; ?>
</div>
<?php endif; ?>

<?php endif; ?>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>
