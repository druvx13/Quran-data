<?php
/**
 * index.php — Qur'an site home page listing all 114 surahs.
 */
require_once __DIR__ . '/includes/config.php';

$page_title   = "Qur\u{2019}an \u{2013} Transliteration &amp; Translation";
$current_sura = 0;

require __DIR__ . '/includes/header.php';
?>
<main>
<h1>Qur&#x2019;an &mdash; Arabic, Transliteration, English, Hindi &amp; Gujarati Translation</h1>

<details class="notice">
<summary><strong>Public Domain Notice &amp; Source Attribution</strong></summary>
<em>Arabic Text:</em> Standard Arabic Uthmani Script.<br>
<em>Audio Recitation:</em> Mishary Rashid Alafasy &mdash; via
  <a href="https://druvx13-quran-audio-alafasy.hf.space" rel="noopener noreferrer">Hugging Face Space</a>
  (audio sourced from versebyversequran.com).<br>
<em>Transliteration:</em> Tanzil.net English Transliteration of the Qur&#x2019;an.<br>
<em>Transliteration:</em> Quran Unicode Project (translit_en.txt).<br>
<em>English Translation:</em> Mohammed Marmaduke Pickthall,
  <em>The Meaning of the Glorious Koran</em> (1930) &mdash; Public Domain.<br>
<em>English Translation:</em> Abdullah Yusuf Ali,
  <em>The Holy Quran: Text, Translation and Commentary</em> &mdash; Public Domain.<br>
<em>English Translation:</em> Saheeh International.<br>
<em>English Explanation:</em> Abridged Explanation of the Quran.<br>
<em>Hindi Translation (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;):</em>
  Muhammad Farooq Khan &amp; Muhammad Ahmed.<br>
<em>Hindi Translation (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2309;&#2344;&#2369;&#2357;&#2366;&#2342;):</em>
  Suhel Farooq Khan &amp; Saifur Rahman Nadwi.<br>
<em>Hindi Tafsir (&#2361;&#2367;&#2344;&#2381;&#2342;&#2368; &#2340;&#2347;&#2381;&#2360;&#2368;&#2352;):</em>
  Al-Mokhtasar Fi Tafsir Al-Quran Al-Karim.<br>
<em>Gujarati Translation (&#2711;&#2753;&#2716;&#2736;&#2750;&#2724;&#2752; &#2733;&#2750;&#2743;&#2750;&#2690;&#2724;&#2736;):</em>
  Rabila Al-Umry.<br>
Texts are reproduced verbatim; no alterations have been made.
</details>

<h2>Surahs (Chapters)</h2>
<div class="surah-grid">
<?php for ($i = 1; $i <= 114; $i++): ?>
  <a href="surah.php?s=<?= $i ?>"><strong><?= $i ?>.</strong> <?= htmlspecialchars(surah_name($i)) ?></a>
<?php endfor; ?>
</div>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>
