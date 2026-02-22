# Qur'an PHP Site (LAMP / LEMP)

A fully self-contained PHP website for the Qur'an — Arabic text, audio recitation, two transliterations, three English translations, an English explanation, two Hindi translations, a Hindi Tafsir, and a Gujarati translation — backed by a local **SQLite** database.

## Features

- **114 dynamic surah pages** — every ayah with all content streams
- **Server-side full-text search** — searches Arabic, transliteration, Yusuf Ali, and Hindi Tafsir; results paginated
- **Verse & Content Filter** — collapse/expand content rows and jump to verse ranges
- **Audio recitation** — per-ayah audio player (Mishary Rashid Alafasy), streamed from Hugging Face Space
- **SQLite database** — all 6 236 verses stored locally; zero external file reads at runtime
- **Self-contained** — copy the `/php` directory to any LAMP/LEMP server and it works

---

## Directory Structure

```
php/
├── data/                   # Bundled plain-text source files (read only by init_db.php)
│   ├── quran_arabic.txt
│   ├── en.transliteration.txt
│   ├── quran_translit_unicode.txt
│   ├── quran_english_pickthall.txt
│   ├── quran_english_yusufali.txt
│   ├── quran_english_sahih.txt
│   ├── quran_english_abridged.txt
│   ├── quran_hindi_farooq.txt
│   ├── quran_hindi_suhail.txt
│   ├── quran_hindi_mokhtasar.txt
│   └── quran_gujarati_rabila.txt
├── db/
│   ├── init_db.php         # One-time setup: imports data/ → quran.sqlite
│   └── quran.sqlite        # Generated SQLite database (gitignored)
├── includes/
│   ├── config.php          # Paths, surah metadata, helper functions
│   ├── loader.php          # PDO SQLite queries (load_surah_verses, search_verses)
│   ├── header.php          # Shared HTML <head>, CSS, sticky header
│   └── footer.php          # Shared HTML footer
├── index.php               # Home page — surah grid
├── surah.php               # Surah viewer  ?s=<1–114>
├── search.php              # Full-text search  ?q=<query>&page=<n>
└── README.md               # This file
```

---

## Requirements

| Requirement | Minimum version |
|-------------|-----------------|
| PHP         | 7.4+            |
| PHP extensions | `pdo`, `pdo_sqlite` (usually bundled) |
| Web server  | Apache 2.4+ or Nginx 1.18+ |
| Disk space  | ~120 MB (19 MB data + ~95 MB SQLite DB) |

### Check PHP extensions

```bash
php -m | grep -i 'pdo\|sqlite'
```

Expected output includes `PDO`, `pdo_sqlite`.

---

## Installation (LAMP — Apache)

```bash
# 1. Clone / copy the repository
git clone https://github.com/druvx13/Quran-data.git
cd Quran-data/php

# 2. Initialise the SQLite database (one-time, takes ~30 seconds)
php db/init_db.php

# 3. Set permissions
chmod 664 db/quran.sqlite
chmod 775 db/

# 4. Point your virtual host document root to this directory
#    Example Apache VirtualHost:
#
#    <VirtualHost *:80>
#        ServerName quran.example.com
#        DocumentRoot /var/www/html/Quran-data/php
#        <Directory /var/www/html/Quran-data/php>
#            Options -Indexes
#            AllowOverride All
#            Require all granted
#        </Directory>
#    </VirtualHost>

# 5. Reload Apache
sudo systemctl reload apache2
```

---

## Installation (LEMP — Nginx + PHP-FPM)

```bash
# 1–3. Same as above

# 4. Example Nginx server block:
#
#    server {
#        listen 80;
#        server_name quran.example.com;
#        root /var/www/html/Quran-data/php;
#        index index.php;
#
#        location / {
#            try_files $uri $uri/ /index.php$is_args$args;
#        }
#
#        location ~ \.php$ {
#            fastcgi_pass unix:/run/php/php8.1-fpm.sock;
#            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
#            include fastcgi_params;
#        }
#
#        # Deny direct access to data and db directories
#        location ~* ^/(data|db)/ { deny all; }
#    }

# 5. Reload Nginx
sudo systemctl reload nginx
```

---

## Running locally with PHP's built-in server

```bash
cd Quran-data/php
php db/init_db.php           # first-time setup
php -S localhost:8080
# Open http://localhost:8080
```

---

## Updating the database

If the source data files in `data/` are updated, simply re-run:

```bash
php db/init_db.php
```

This drops and recreates all tables from scratch.

---

## Security notes

- The `data/` and `db/` directories should **not** be directly accessible from the web.
  Use the Nginx `deny all` rule shown above, or add an Apache `.htaccess`:
  ```
  Deny from all
  ```
- All user input is validated and passed through PDO prepared statements — no SQL injection risk.
- All output is passed through `htmlspecialchars()` before rendering.
