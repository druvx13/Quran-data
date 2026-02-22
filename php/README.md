# Qur'an PHP Site (LAMP / LEMP)

A fully self-contained PHP website for the Qur'an — Arabic text, audio recitation, two transliterations, three English translations, an English explanation, two Hindi translations, a Hindi Tafsir, and a Gujarati translation — backed by a pre-built local **SQLite** database.

**No configuration required.** Download, upload to any PHP host, done.

## Features

- **114 dynamic surah pages** — every ayah with all content streams
- **Server-side full-text search** — searches Arabic, transliteration, Yusuf Ali, and Hindi Tafsir; results paginated
- **Verse & Content Filter** — collapse/expand content rows and jump to verse ranges
- **Audio recitation** — per-ayah audio player (Mishary Rashid Alafasy), streamed from Hugging Face Space
- **Pre-built SQLite database** — all 6 236 verses ready to use; no setup commands needed
- **Self-contained** — upload the `/php` directory to any LAMP/LEMP host and it works instantly

---

## Directory Structure

```
php/
├── data/                   # Bundled plain-text source files
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
│   ├── quran.sqlite        # Pre-built SQLite database (included — no setup needed)
│   └── init_db.php         # Optional: rebuild the DB if data/ files are updated
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
| PHP extensions | `pdo`, `pdo_sqlite` (usually bundled on all hosts) |
| Web server  | Apache 2.4+ or Nginx 1.18+ |
| Disk space  | ~50 MB          |

---

## Installation (LAMP — Apache)

```bash
# 1. Download / clone the repository
git clone https://github.com/druvx13/Quran-data.git

# 2. Upload the php/ directory to your server's document root (or a subdirectory)
#    e.g. copy to /var/www/html/quran

# 3. Set permissions (the db/ directory must be readable by the web server)
chmod 644 db/quran.sqlite
chmod 755 db/

# That's it — open your browser and go!
```

Example Apache VirtualHost:

```apache
<VirtualHost *:80>
    ServerName quran.example.com
    DocumentRoot /var/www/html/quran
    <Directory /var/www/html/quran>
        Options -Indexes
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

---

## Installation (LEMP — Nginx + PHP-FPM)

Upload the `php/` directory, set permissions as above, then add an Nginx server block:

```nginx
server {
    listen 80;
    server_name quran.example.com;
    root /var/www/html/quran;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php$is_args$args;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    # Deny direct web access to data and db directories
    location ~* ^/(data|db)/ { deny all; }
}
```

---

## Shared / cPanel hosting

1. Download this repository as a ZIP from GitHub.
2. Extract and upload the contents of `php/` into `public_html/` (or a subdirectory) via FTP or cPanel File Manager.
3. Open your browser — the site works immediately.

> **Note:** Most shared hosts (cPanel, Plesk, DirectAdmin) ship with PHP 7.4+ and PDO SQLite pre-enabled. No SSH or terminal access is required.

---

## Running locally with PHP's built-in server

```bash
cd Quran-data/php
php -S localhost:8080
# Open http://localhost:8080
```

---

## Rebuilding the database (optional)

The pre-built `db/quran.sqlite` is included in the repository and is ready to use.
You only need to rebuild it if you modify the source data files in `data/`:

```bash
cd Quran-data/php
php db/init_db.php
```

---

## Security notes

- The `data/` and `db/` directories should **not** be directly accessible from the web.
  The Nginx config above already blocks them. For Apache, an `.htaccess` is sufficient:
  ```
  Deny from all
  ```
- All user input is validated and passed through PDO prepared statements — no SQL injection risk.
- All output is passed through `htmlspecialchars()` before rendering.
