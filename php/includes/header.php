<?php
/**
 * header.php — Common HTML <head> and sticky header for all pages.
 *
 * Expected variables set by the calling page before include:
 *   $page_title  (string) — value for <title>
 *   $meta_desc   (string, optional) — content for <meta name="description">
 *   $current_sura (int, optional) — currently viewed surah (0 = none)
 */

require_once __DIR__ . '/config.php';

$page_title   = $page_title   ?? "Qur\u{2019}an \u{2013} Transliteration &amp; Translation";
$meta_desc    = $meta_desc    ?? "Side-by-side Arabic text, transliteration, and multi-language translations of the Qur'an.";
$current_sura = $current_sura ?? 0;

// Build the surah <select> drop-down
$opts = '<option value="">Jump to Surah&hellip;</option>';
for ($i = 1; $i <= 114; $i++) {
    $sel   = ($i === $current_sura) ? ' selected' : '';
    $name  = htmlspecialchars(surah_name($i), ENT_QUOTES);
    $opts .= "<option value=\"surah.php?s={$i}\"{$sel}>{$i}. {$name}</option>";
}
$surah_select = "<select class='surah-nav-select' onchange='location.href=this.value' aria-label='Navigate to Surah'>{$opts}</select>";
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<?php if (!empty($meta_desc)): ?>
<meta name="description" content="<?= htmlspecialchars($meta_desc, ENT_QUOTES) ?>">
<?php endif; ?>
<title><?= $page_title ?></title>
<style>
*,*::before,*::after{box-sizing:border-box}
body{margin:0;padding:0;font-family:system-ui,Arial,Helvetica,sans-serif;
  font-size:16px;background:#fff;color:#111;line-height:1.6}
header{background:#1a3a5c;color:#fff;padding:12px 16px;position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
header a{color:#ffd54f;text-decoration:none;font-weight:bold;font-size:1.1em}
header a:hover{text-decoration:underline}
.header-search{margin-left:auto}
main{padding:16px;max-width:900px;margin:0 auto}
h1{font-size:1.4em;margin:0 0 12px}
h2{font-size:1.2em;color:#1a3a5c;margin:20px 0 8px}
.surah-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-top:16px}
.surah-grid a{display:block;padding:10px 12px;background:#f0f4f8;border:1px solid #ccd6e0;
  border-radius:6px;text-decoration:none;color:#1a3a5c;font-size:.95em}
.surah-grid a:hover{background:#dde8f2}
.notice{background:#fff8e1;border-left:4px solid #ffd54f;padding:12px 16px;margin-bottom:20px;font-size:.95em}
.notice summary{cursor:pointer}
.table-wrap{overflow-x:auto;width:100%}
table{width:100%;border-collapse:collapse;margin-bottom:24px}
th{background:#1a3a5c;color:#fff;padding:10px 12px;text-align:left;font-size:.9em}
td{padding:8px 12px;vertical-align:top;border:1px solid #ccd6e0}
.ayah-sep td{background:#1a3a5c;color:#fff;font-weight:bold;font-size:.9em;padding:6px 12px;border-color:#1a3a5c}
.label{color:#888;font-size:.82em;white-space:nowrap;width:110px}
.translit td{background:#f0f4f8}
.translit-unicode td{background:#e8eaf6}
.trans td{background:#fff}
.trans-yusuf td{background:#e8f5e9}
.trans-sahih td{background:#e3f2fd}
.hindi td{background:#f5f0ff}
.hindi-suhail td{background:#fff3e0}
.hindi-mokhtasar td{background:#e8f5e0}
.eng-abridged td{background:#e8f4fd}
.audio td{background:#e0f7fa}
.audio-player{width:100%;max-width:420px;height:36px;vertical-align:middle}
.translit-text{font-style:normal;font-weight:600}
.translit-unicode-text{font-style:normal;font-weight:600;color:#283593}
.hindi-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#3a2a6c}
.hindi-suhail-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#5d4037}
.hindi-mokhtasar-text{font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1b5e20}
.gujarati td{background:#fce4ec}
.gujarati-text{font-family:'Noto Sans Gujarati',Arial,sans-serif;color:#880e4f}
.arabic td{background:#fff8e1}
.arabic-text{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.5em;direction:rtl;text-align:right;line-height:2}
nav.chapter-nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  padding:16px 0;margin-top:8px;border-top:1px solid #ccd6e0}
nav.chapter-nav a{display:inline-block;padding:8px 16px;background:#1a3a5c;color:#fff;
  border-radius:4px;text-decoration:none;font-size:.95em}
nav.chapter-nav a:hover{background:#2a5a8c}
footer{text-align:center;padding:20px;font-size:.85em;color:#666;border-top:1px solid #e0e0e0;margin-top:32px}
.surah-nav-select{padding:5px 8px;border-radius:4px;border:1px solid #ffd54f;background:#1a3a5c;color:#ffd54f;font-size:.9em;cursor:pointer;max-width:240px}
.surah-nav-select:focus{outline:2px solid #ffd54f;outline-offset:2px}
.verse-chooser{background:#f0f4f8;border:1px solid #ccd6e0;border-radius:6px;margin-bottom:16px}
.verse-chooser summary{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;cursor:pointer;user-select:none;list-style:none;background:#e8eef4;border-radius:6px}
.verse-chooser[open] summary{border-radius:6px 6px 0 0}
.verse-chooser summary::-webkit-details-marker{display:none}
.vc-title{font-size:1em;font-weight:bold;color:#1a3a5c}
.vc-arrow{color:#1a3a5c;transition:transform .2s}
.verse-chooser[open] .vc-arrow{transform:rotate(180deg)}
.vc-body{padding:10px 14px}
.vc-controls{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap}
.vc-controls button{padding:6px 14px;border:none;border-radius:4px;cursor:pointer;font-size:.88em;background:#1a3a5c;color:#fff;min-height:36px}
.vc-controls button:hover{background:#2a5a8c}
.vc-range{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:6px}
.vc-range label{font-size:.88em;color:#1a3a5c;white-space:nowrap}
.vc-range input[type=number]{width:70px;padding:5px 6px;border:1px solid #ccd6e0;border-radius:4px;font-size:.88em;color:#111;background:#fff}
.vc-range input[type=number]:focus{outline:2px solid #ffd54f;outline-offset:2px}
.vc-section-title{font-size:.82em;font-weight:bold;color:#555;text-transform:uppercase;letter-spacing:.04em;margin:8px 0 4px}
.cf-list{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.cf-item input[type=checkbox]{position:absolute;opacity:0;width:0;height:0}
.cf-item label{display:inline-flex;align-items:center;padding:5px 10px;background:#fff;border:1px solid #ccd6e0;border-radius:4px;cursor:pointer;font-size:.85em;color:#1a3a5c;user-select:none;white-space:nowrap}
.cf-item label:hover{background:#dde8f2}
.cf-item input:checked+label{background:#1a3a5c;color:#fff;border-color:#1a3a5c}
.cf-item input:focus+label{outline:2px solid #ffd54f;outline-offset:2px}
@media(max-width:600px){.vc-controls button{min-height:44px}.cf-item label{min-height:44px;padding:8px 10px}}
.noscript-warn{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 14px;margin-bottom:12px;font-size:.93em;color:#856404}
/* Search page */
.search-box{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.search-box input[type=text]{flex:1;min-width:200px;padding:9px 12px;border:1px solid #ccd6e0;border-radius:4px;font-size:1em;color:#111}
.search-box input[type=text]:focus{outline:2px solid #ffd54f;outline-offset:2px}
.search-box button{padding:9px 18px;background:#1a3a5c;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:1em}
.search-box button:hover{background:#2a5a8c}
#search-status{font-size:.92em;color:#555;margin-bottom:10px}
.result-card{border:1px solid #ccd6e0;border-radius:6px;margin-bottom:12px;overflow:hidden}
.result-header{background:#1a3a5c;color:#fff;padding:7px 12px;font-size:.9em;display:flex;align-items:center;justify-content:space-between}
.result-header a{color:#ffd54f;text-decoration:none;font-weight:bold}
.result-header a:hover{text-decoration:underline}
.result-arabic{font-family:'Scheherazade New','Amiri','Traditional Arabic',serif;font-size:1.4em;direction:rtl;text-align:right;line-height:2;padding:8px 12px;background:#fff8e1}
.result-translit{padding:6px 12px;background:#e8eaf6;font-weight:600;color:#283593;font-size:.95em}
.result-trans{padding:6px 12px;background:#e8f5e9;font-size:.95em}
.result-highlight{background:#fff176;border-radius:2px}
.result-hindi-mokhtasar{padding:6px 12px;background:#e8f5e0;font-family:'Noto Sans Devanagari',Arial,sans-serif;color:#1b5e20;font-size:.95em}
.pagination{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:16px 0;justify-content:center}
.pagination a,.pagination span{display:inline-block;padding:7px 14px;border-radius:4px;font-size:.9em;min-width:36px;text-align:center}
.pagination a{background:#1a3a5c;color:#fff;text-decoration:none}
.pagination a:hover{background:#2a5a8c}
.pagination .pg-current{background:#ffd54f;color:#1a3a5c;font-weight:bold}
.pagination .pg-disabled{background:#ccd6e0;color:#888;cursor:default}
.pagination .pg-ellipsis{color:#555}
@media(prefers-color-scheme:dark){
  body{background:#121212;color:#e8e8e8}
  header{background:#0d2136}
  main{color:#e8e8e8}
  h2{color:#90caf9}
  td{border-color:#333;color:#e8e8e8}
  .ayah-sep td{background:#0d2136;border-color:#0d2136}
  .label{color:#aaa}
  .translit td{background:#1e2a3a}
  .translit-unicode td{background:#1a1f3a}
  .trans td{background:#1a1a1a}
  .trans-yusuf td{background:#1a2a1a}
  .trans-sahih td{background:#132030}
  .hindi td{background:#1e1530}
  .hindi-suhail td{background:#2a1f10}
  .hindi-mokhtasar td{background:#102010}
  .eng-abridged td{background:#102028}
  .gujarati td{background:#200010}
  .audio td{background:#0d2228}
  .arabic td{background:#2a2010}
  .surah-grid a{background:#1e2a3a;border-color:#334;color:#90caf9}
  .surah-grid a:hover{background:#263650}
  .notice{background:#2a2010;border-left-color:#ffc107;color:#e8e8e8}
  .verse-chooser{background:#1e2a3a;border-color:#334}
  .verse-chooser summary{background:#162030}
  .vc-title{color:#90caf9}
  .vc-arrow{color:#90caf9}
  .vc-range input[type=number]{background:#1a1a1a;border-color:#334;color:#e8e8e8}
  .cf-item label{background:#1a1a1a;border-color:#334;color:#90caf9}
  .cf-item label:hover{background:#263650}
  .cf-item input:checked+label{background:#1a3a5c;color:#fff}
  footer{color:#aaa;border-top-color:#333}
  th{background:#0d2136}
  .translit-unicode-text{color:#9fa8da}
  .hindi-text{color:#b39ddb}
  .hindi-suhail-text{color:#ffcc80}
  .hindi-mokhtasar-text{color:#a5d6a7}
  .gujarati-text{color:#f48fb1}
  .search-box input[type=text]{background:#1a1a1a;border-color:#334;color:#e8e8e8}
  .result-card{border-color:#334}
  .result-arabic{background:#2a2010}
  .result-translit{background:#1a1f3a;color:#9fa8da}
  .result-trans{background:#1a2a1a}
  .result-hindi-mokhtasar{background:#102010;color:#a5d6a7}
  .pagination a{background:#1a3a5c}
  .pagination .pg-current{background:#ffd54f;color:#1a3a5c}
  .pagination .pg-disabled{background:#333;color:#666}
}
@media print{
  header,nav.chapter-nav,.verse-chooser,footer{display:none!important}
  body{font-size:11pt;color:#000;background:#fff}
  td{border-color:#999;color:#000;background:#fff!important}
  .arabic-text{font-size:1.3em}
  .ayah-sep td{background:#ddd!important;color:#000!important}
  tr[data-ayah]{display:table-row!important}
}
</style>
</head>
<body>
<header>
  <a href="index.php">&#8962; Index</a>
  <?= $surah_select ?>
  <a class="header-search" href="search.php">&#128269; Search</a>
</header>
