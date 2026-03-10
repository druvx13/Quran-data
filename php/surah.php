<?php
/**
 * surah.php — Dynamic surah viewer.
 *
 * URL parameter:  ?s=<surah_number>  (1–114)
 * Optional anchor: #ayah-<N>  to jump to a specific verse.
 */
require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/loader.php';

// -----------------------------------------------------------------------
// Validate input
// -----------------------------------------------------------------------
$sura = (int)($_GET['s'] ?? 1);
if ($sura < 1 || $sura > 114) {
    header('Location: index.php');
    exit;
}

$name = surah_name($sura);
$size = surah_size($sura);

// -----------------------------------------------------------------------
// Load verses from SQLite
// -----------------------------------------------------------------------
try {
    $verses = load_surah_verses($sura);
} catch (RuntimeException $e) {
    $db_error = $e->getMessage();
    $verses   = [];
}

// -----------------------------------------------------------------------
// Page metadata
// -----------------------------------------------------------------------
$page_title   = "Surah {$sura}: " . htmlspecialchars($name, ENT_QUOTES);
$meta_desc    = "Surah {$sura}: {$name} — Arabic text, transliteration, and English & Hindi translations of the Qur'an.";
$current_sura = $sura;

require __DIR__ . '/includes/header.php';
?>
<main>
<h1>Surah <?= $sura ?>: <?= htmlspecialchars($name) ?></h1>

<?php if (!empty($db_error)): ?>
<div class="notice" style="background:#ffe0e0;border-left-color:#c00">
  <strong>Database error:</strong> <?= htmlspecialchars($db_error) ?><br>
  Please run <code>php db/init_db.php</code> to initialise the database.
</div>
<?php else: ?>

<!-- Verse &amp; Content Filter -->
<details class="verse-chooser" id="vc">
  <summary>
    <span class="vc-title">&#9881; Verse &amp; Content Filter</span>
    <span class="vc-arrow">&#9660;</span>
  </summary>
  <div class="vc-body">
    <noscript><p class="noscript-warn">JavaScript is required for filtering.</p></noscript>
    <div class="vc-controls">
      <button onclick="vcShowAll()">Show All</button>
      <button onclick="vcHideAll()">Hide All</button>
      <button onclick="vcReset()">Reset</button>
    </div>
    <div class="vc-range">
      <label>Ayah from:</label>
      <input type="number" id="vc-from" min="1" max="<?= $size ?>" value="1">
      <label>to:</label>
      <input type="number" id="vc-to"   min="1" max="<?= $size ?>" value="<?= $size ?>">
      <button onclick="vcApplyRange()">Apply</button>
    </div>
    <div class="vc-section-title">Content rows</div>
    <div class="cf-list">
      <?php
      $filters = [
        'arabic'         => 'Arabic',
        'audio'          => 'Audio (Alafasy)',
        'translit'       => 'Transliteration (Tanzil)',
        'translit-unicode'=> 'Transliteration (Unicode)',
        'trans'          => 'English (Pickthall)',
        'trans-yusuf'    => 'English (Yusuf Ali)',
        'trans-sahih'    => 'English (Saheeh Int\'l)',
        'eng-abridged'   => 'English (Abridged Expl.)',
        'hindi'          => 'Hindi (Farooq)',
        'hindi-suhail'   => 'Hindi (Suhail)',
        'hindi-mokhtasar'=> 'Hindi Tafsir (Mokhtasar)',
        'gujarati'       => 'Gujarati (Rabila)',
      ];
      foreach ($filters as $cls => $label):
        $id = 'cf-' . htmlspecialchars($cls, ENT_QUOTES);
      ?>
      <span class="cf-item">
        <input type="checkbox" id="<?= $id ?>" checked
               onchange="vcToggleClass('<?= htmlspecialchars($cls, ENT_QUOTES) ?>', this.checked)">
        <label for="<?= $id ?>"><?= htmlspecialchars($label) ?></label>
      </span>
      <?php endforeach; ?>
    </div>
  </div>
</details>

<!-- Verse table -->
<div class="table-wrap">
<table>
<thead>
  <tr><th style="width:110px">Type</th><th>Text</th></tr>
</thead>
<tbody>
<?php foreach ($verses as $ayah => $v):
    $ar  = $v['arabic']          ?? '';
    $tl  = $v['translit']        ?? '';
    $tu  = $v['translit_unicode']?? '';
    $pk  = $v['pickthall']       ?? '';
    $ya  = $v['yusufali']        ?? '';
    $sa  = $v['sahih']           ?? '';
    $ea  = $v['eng_abridged']    ?? '';
    $hi  = $v['hindi']           ?? '';
    $hs  = $v['hindi_suhail']    ?? '';
    $hm  = $v['hindi_mokhtasar'] ?? '';
    $gu  = $v['gujarati']        ?? '';
?>
<tr class="ayah-sep" data-ayah="<?= $ayah ?>" id="ayah-<?= $ayah ?>">
  <td colspan="2">Ayah <?= $ayah ?></td>
</tr>
<tr class="arabic" data-ayah="<?= $ayah ?>">
  <td class="label">&#1593;&#1614;&#1585;&#1614;&#1576;&#1616;&#1610;</td>
  <td class="arabic-text" lang="ar"><?= htmlspecialchars($ar) ?></td>
</tr>
<tr class="audio" data-ayah="<?= $ayah ?>">
  <td class="label">Audio (Alafasy)</td>
  <td><audio class="audio-player" controls preload="none"
       src="https://druvx13-quran-audio-alafasy.hf.space/<?= sprintf('%03d%03d', $sura, $ayah) ?>.mp3"
       title="Surah <?= $sura ?>, Ayah <?= $ayah ?> — Mishary Alafasy recitation"></audio></td>
</tr>
<tr class="translit" data-ayah="<?= $ayah ?>">
  <td class="label">Transliteration (Tanzil)</td>
  <td class="translit-text"><?= htmlspecialchars($tl) ?></td>
</tr>
<tr class="translit-unicode" data-ayah="<?= $ayah ?>">
  <td class="label">Transliteration (Unicode)</td>
  <td class="translit-unicode-text"><?= htmlspecialchars($tu) ?></td>
</tr>
<tr class="trans" data-ayah="<?= $ayah ?>">
  <td class="label">English (Pickthall)</td>
  <td lang="en"><?= htmlspecialchars($pk) ?></td>
</tr>
<tr class="trans-yusuf" data-ayah="<?= $ayah ?>">
  <td class="label">English (Yusuf Ali)</td>
  <td lang="en"><?= htmlspecialchars($ya) ?></td>
</tr>
<tr class="trans-sahih" data-ayah="<?= $ayah ?>">
  <td class="label">English (Saheeh Int&#x2019;l)</td>
  <td lang="en"><?= htmlspecialchars($sa) ?></td>
</tr>
<tr class="eng-abridged" data-ayah="<?= $ayah ?>">
  <td class="label">English (Abridged Expl.)</td>
  <td lang="en"><?= htmlspecialchars($ea) ?></td>
</tr>
<tr class="hindi" data-ayah="<?= $ayah ?>">
  <td class="label">&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; (Farooq)</td>
  <td class="hindi-text" lang="hi"><?= htmlspecialchars($hi) ?></td>
</tr>
<tr class="hindi-suhail" data-ayah="<?= $ayah ?>">
  <td class="label">&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; (Suhail)</td>
  <td class="hindi-suhail-text" lang="hi"><?= htmlspecialchars($hs) ?></td>
</tr>
<tr class="hindi-mokhtasar" data-ayah="<?= $ayah ?>">
  <td class="label">&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352; (Mokhtasar)</td>
  <td class="hindi-mokhtasar-text" lang="hi"><?= htmlspecialchars($hm) ?></td>
</tr>
<tr class="gujarati" data-ayah="<?= $ayah ?>">
  <td class="label">&#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752; (Rabila)</td>
  <td class="gujarati-text" lang="gu"><?= htmlspecialchars($gu) ?></td>
</tr>
<?php endforeach; ?>
</tbody>
</table>
</div>

<!-- Prev / Next navigation -->
<nav class="chapter-nav">
  <?php if ($sura > 1): ?>
    <a href="surah.php?s=<?= $sura - 1 ?>">&laquo; Surah <?= $sura - 1 ?>: <?= htmlspecialchars(surah_name($sura - 1)) ?></a>
  <?php else: ?>
    <span></span>
  <?php endif; ?>
  <?php if ($sura < 114): ?>
    <a href="surah.php?s=<?= $sura + 1 ?>">Surah <?= $sura + 1 ?>: <?= htmlspecialchars(surah_name($sura + 1)) ?> &raquo;</a>
  <?php endif; ?>
</nav>

<?php endif; ?>
</main>

<script>
(function() {
  // Verse & Content Filter JS
  var rows = document.querySelectorAll('tr[data-ayah]');

  function setClass(cls, show) {
    document.querySelectorAll('tr.' + cls).forEach(function(r) {
      r.style.display = show ? '' : 'none';
    });
  }

  window.vcToggleClass = function(cls, show) { setClass(cls, show); };

  window.vcShowAll = function() {
    document.querySelectorAll('.cf-item input').forEach(function(cb) {
      cb.checked = true;
      setClass(cb.id.replace('cf-', ''), true);
    });
    rows.forEach(function(r) { r.style.display = ''; });
  };

  window.vcHideAll = function() {
    document.querySelectorAll('.cf-item input').forEach(function(cb) {
      cb.checked = false;
      setClass(cb.id.replace('cf-', ''), false);
    });
  };

  window.vcReset = function() {
    vcShowAll();
    document.getElementById('vc-from').value = 1;
    document.getElementById('vc-to').value   = <?= $size ?>;
  };

  window.vcApplyRange = function() {
    var from = parseInt(document.getElementById('vc-from').value, 10) || 1;
    var to   = parseInt(document.getElementById('vc-to').value,   10) || <?= $size ?>;
    rows.forEach(function(r) {
      var a = parseInt(r.getAttribute('data-ayah'), 10);
      r.style.display = (a >= from && a <= to) ? '' : 'none';
    });
  };
})();
</script>
<?php require __DIR__ . '/includes/footer.php'; ?>
