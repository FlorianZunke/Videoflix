# Videoflix Backend

Ein Django-basiertes Backend für eine Video-Streaming-Plattform mit Benutzerauthentifizierung, JWT-Token-Management und HLS-Videostreaming.

## 📋 Inhaltsverzeichnis

- [Features](#features)
- [Systemanforderungen](#systemanforderungen)
- [Installation](#installation)
  - [Windows Setup](#windows-setup)
  - [macOS Setup](#macos-setup)
- [Konfiguration](#konfiguration)
- [API Endpoints](#api-endpoints)
  - [Authentifizierung](#authentifizierung)
  - [Videos](#videos)
- [Docker Setup](#docker-setup)
- [Häufige Probleme](#häufige-probleme)
- [Entwicklung](#entwicklung)

---

## Features

✨ **Authentifizierung & Autorisierung**
- Benutzerregistrierung mit E-Mail-Aktivierung
- Cookie-basierte JWT-Token-Authentifizierung
- Passwort-Reset mit E-Mail-Bestätigung
- Token-Refresh-Mechanismus

🎥 **Video-Management**
- Video-Upload mit Metadaten (Titel, Beschreibung, Kategorie)
- HLS (HTTP Live Streaming) für verschiedene Auflösungen
- Video-Konversionsstatus-Tracking
- Thumbnail-Verwaltung

🔧 **Backend-Features**
- Django REST Framework für RESTful APIs
- PostgreSQL-Datenbankunterstützung
- Redis-Caching für Performance
- Asynchrone Job-Verarbeitung mit RQ
- CORS-Unterstützung für Frontend-Integration
- Email-Support für Benutzerbenachrichtigungen

---

## Systemanforderungen

### Allgemein
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- ffmpeg (für Videokonvertierung)

### Windows
- Git Bash oder PowerShell
- Virtualenv oder venv

### macOS
- Homebrew (optional, aber empfohlen)
- Xcode Command Line Tools

---

## Installation

### Windows Setup

#### Voraussetzungen installieren

```powershell
# Git installieren (falls nicht vorhanden)
# Herunterladen von: https://git-scm.com/download/win

# Python 3.12 installieren
# Herunterladen von: https://www.python.org/downloads/
# WICHTIG: "Add Python to PATH" während Installation aktivieren!

# PostgreSQL installieren
# Herunterladen von: https://www.postgresql.org/download/windows/

# Redis installieren (Option 1: Windows Subsystem for Linux)
# https://docs.microsoft.com/en-us/windows/wsl/tutorials/databases

# ffmpeg installieren
# Herunterladen von: https://ffmpeg.org/download.html
# Oder mit Chocolatey:
choco install ffmpeg
```

#### Projekt-Setup

```powershell
# 1. Zum Projektverzeichnis navigieren
cd C:\Users\[YourUsername]\Programierung\Backend_Projekte\Videoflix\Videoflix

# 2. Virtuelle Umgebung erstellen
python -m venv env

# 3. Virtuelle Umgebung aktivieren
.\env\Scripts\Activate.ps1

# Wenn die Aktivierung fehlschlägt, führen Sie aus:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

# 5. Environment-Variablen konfigurieren
# Datei .env im Projektverzeichnis erstellen und .env.template kopieren
Copy-Item .env.template .env

# 6. Datenbank-Migrationen durchführen
python manage.py migrate

# 7. Admin-User erstellen
python manage.py createsuperuser

# 8. Development-Server starten
python manage.py runserver

# Der Server läuft dann unter: http://localhost:8000
```

#### RQ Worker starten (für Hintergrund-Jobs)

```powershell
# In einem separaten PowerShell-Fenster:
python manage.py rqworker default
```

---

### macOS Setup

#### Voraussetzungen mit Homebrew installieren

```bash
# Homebrew installieren (falls nicht vorhanden)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Git installieren
brew install git

# Python 3.12 installieren
brew install python@3.12

# PostgreSQL installieren
brew install postgresql@15

# PostgreSQL-Service starten
brew services start postgresql@15

# Redis installieren
brew install redis

# Redis-Service starten
brew services start redis

# ffmpeg installieren
brew install ffmpeg
```

#### Projekt-Setup

```bash
# 1. Zum Projektverzeichnis navigieren
cd ~/Programierung/Backend_Projekte/Videoflix/Videoflix

# 2. Virtuelle Umgebung erstellen
python3.12 -m venv env

# 3. Virtuelle Umgebung aktivieren
source env/bin/activate

# 4. Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt

# 5. Environment-Variablen konfigurieren
cp .env.template .env

# 6. Datenbank-Migrationen durchführen
python manage.py migrate

# 7. Admin-User erstellen
python manage.py createsuperuser

# 8. Development-Server starten
python manage.py runserver

# Der Server läuft dann unter: http://localhost:8000
```

#### RQ Worker starten (für Hintergrund-Jobs)

```bash
# In einem separaten Terminal-Fenster:
python manage.py rqworker default
```

---

## Konfiguration

### Environment-Variablen (.env)

Erstellen Sie eine `.env`-Datei im Projektverzeichnis. Verwenden Sie `.env.template` als Vorlage:

```env
# Django Settings
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your_secure_password
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY="your-secret-key-here"
DEBUG=True  # WICHTIG: In Produktion auf False setzen!
ALLOWED_HOSTS=localhost,127.0.0.1,example.com
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://localhost:3000

# Datenbankverbindung
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=your_db_password
DB_HOST=localhost  # "db" in Docker
DB_PORT=5432

# Redis-Konfiguration
REDIS_HOST=localhost  # "redis" in Docker
REDIS_PORT=6379
REDIS_DB=0
REDIS_LOCATION=redis://localhost:6379/1

# E-Mail-Konfiguration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@videoflix.com

# Frontend-URL
FRONTEND_URL=http://localhost:3000
```

### Wichtige Einstellungen in `core/settings.py`

- **INSTALLED_APPS**: Registrierte Django-Apps
- **DATABASES**: PostgreSQL-Verbindung
- **CACHES**: Redis-Cache-Konfiguration
- **RQ_QUEUES**: Hintergrund-Job-Queue-Einstellungen
- **CORS_ALLOWED_ORIGINS**: Erlaubte Frontend-Domains

---

## API Endpoints

### Basis-URL
```
http://localhost:8000/api/
```

### Authentifizierung

#### 📝 Benutzer registrieren
**Endpoint:** `POST /register/`

**Request-Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "password_confirm": "secure_password"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  },
  "token": "activation_token_here"
}
```

---

#### ✉️ Benutzerkonto aktivieren
**Endpoint:** `GET /activate/<uidb64>/<token>/`

**Beschreibung:** Klick-Link aus Aktivierungs-E-Mail

**Response (200 OK):**
```json
{
  "detail": "Account activated successfully"
}
```

---

#### 🔐 Anmelden (Login)
**Endpoint:** `POST /login/`

**Request-Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Cookies gesetzt:**
- `access_token`: JWT Access Token (HTTPOnly)
- `refresh_token`: JWT Refresh Token (HTTPOnly)

---

#### 🔄 Token erneuern
**Endpoint:** `POST /token/refresh/`

**Beschreibung:** Erneuert den Access Token mit dem Refresh Token

**Response (200 OK):**
```json
{
  "detail": "Token refreshed successfully"
}
```

---

#### 🚪 Abmelden (Logout)
**Endpoint:** `POST /logout/`

**Authentifizierung erforderlich:** Ja (Bearer Token oder Cookie)

**Response (200 OK):**
```json
{
  "detail": "Logout successful"
}
```

---

#### 🔑 Passwort zurücksetzen (Anfragen)
**Endpoint:** `POST /password_reset/`

**Request-Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "detail": "Password reset link sent to your email"
}
```

---

#### 🔐 Passwort bestätigen
**Endpoint:** `POST /password_confirm/<uidb64>/<token>/`

**Request-Body:**
```json
{
  "password": "new_password",
  "password_confirm": "new_password"
}
```

**Response (200 OK):**
```json
{
  "detail": "Password reset successfully"
}
```

---

### Videos

#### 📺 Alle Videos auflisten
**Endpoint:** `GET /video/`

**Authentifizierung erforderlich:** Ja

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Mein erstes Video",
      "description": "Eine Videobeschreibung",
      "created_at": "2026-02-20T10:30:00Z",
      "category": "Tutorial",
      "thumbnail_url": "/media/thumbnails/thumbnail1.jpg",
      "conversion_status": "completed"
    }
  ]
}
```

---

#### 🎬 Video-Details
**Endpoint:** `GET /video/{id}/`

**Authentifizierung erforderlich:** Ja

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Mein erstes Video",
  "description": "Eine Videobeschreibung",
  "created_at": "2026-02-20T10:30:00Z",
  "category": "Tutorial",
  "thumbnail_url": "/media/thumbnails/thumbnail1.jpg",
  "conversion_status": "completed"
}
```

---

#### 🎥 Video HLS-Manifest
**Endpoint:** `GET /video/{movie_id}/{resolution}/index.m3u8`

**Authentifizierung erforderlich:** Ja

**Beschreibung:** Streamt HLS-Manifest für Video-Wiedergabe
- **Auflösungen:** 720p, 1080p, etc. (abhängig von konvertiertem Video)

**Response:** m3u8 Playlist-Datei

---

#### 📹 Video HLS-Segment
**Endpoint:** `GET /video/{movie_id}/{resolution}/{segment}`

**Authentifizierung erforderlich:** Ja

**Beschreibung:** Streamt einzelne Video-Segmente

**Response:** .ts (MPEG Transport Stream) Segment-Datei

---

## Docker Setup

### Docker installieren

**Windows:**
```
https://docs.docker.com/desktop/install/windows-install/
```

**macOS:**
```
https://docs.docker.com/desktop/install/mac-install/
```

### Mit Docker Compose starten

```bash
# 1. .env-Datei erstellen (siehe Konfiguration)
cp .env.template .env

# 2. Docker Images bauen
docker-compose build

# 3. Container starten
docker-compose up -d

# 4. Migrationen durchführen
docker-compose exec web python manage.py migrate

# 5. Superuser erstellen
docker-compose exec web python manage.py createsuperuser

# 6. RQ Worker starten
docker-compose exec web python manage.py rqworker default

# Logs anschauen
docker-compose logs -f web

# Services stoppen
docker-compose down
```

### Docker Compose Services

- **db (PostgreSQL):** Port 5432
- **redis (Redis):** Port 6379
- **web (Django):** Port 8000

### Häufige Docker-Befehle

```bash
# Container neu bauen
docker-compose build

# Container in Hintergrund starten
docker-compose up -d

# Logs in Echtzeit anschauen
docker-compose logs -f [service_name]

# In Container gehen
docker-compose exec web bash

# Migrationen durchführen
docker-compose exec web python manage.py migrate

# Django-Shell öffnen
docker-compose exec web python manage.py shell

# Static Files sammeln
docker-compose exec web python manage.py collectstatic --noinput

# Alle Container stoppen
docker-compose down

# Container und Volumes löschen
docker-compose down -v
```

---

## Häufige Probleme

### 🔴 Problem: "ModuleNotFoundError: No module named 'django'"

**Ursache:** Virtuelle Umgebung nicht aktiviert

**Lösung:**
```powershell
# Windows
.\env\Scripts\Activate.ps1

# macOS/Linux
source env/bin/activate
```

---

### 🔴 Problem: "FATAL: role 'videoflix_user' does not exist"

**Ursache:** PostgreSQL-Benutzer existiert nicht

**Lösung:**

```bash
# Windows/macOS
psql -U postgres

# In psql:
CREATE USER videoflix_user WITH PASSWORD 'your_password';
ALTER ROLE videoflix_user SET client_encoding TO 'utf8';
ALTER ROLE videoflix_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE videoflix_user SET default_transaction_deferrable TO on;
ALTER ROLE videoflix_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE videoflix_db TO videoflix_user;

# Datenbank erstellen
CREATE DATABASE videoflix_db OWNER videoflix_user;

# Beenden
\q
```

---

### 🔴 Problem: "django.db.utils.ProgrammingError: relation 'auth_customuser' does not exist"

**Ursache:** Migrationen nicht durchgeführt

**Lösung:**
```bash
python manage.py migrate
```

---

### 🔴 Problem: "ConnectionRefusedError" bei Redis/PostgreSQL

**Ursache:** Datenbankservice läuft nicht

**Lösung:**

```bash
# Windows (PowerShell)
# PostgreSQL starten
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start

# Redis starten (falls installiert)
# Oder mit WSL

# macOS
brew services start postgresql@15
brew services start redis
```

---

### 🔴 Problem: "CORS policy: response to preflight request" Error

**Ursache:** CORS nicht korrekt konfiguriert

**Lösung:**
1. Überprüfen Sie `CORS_ALLOWED_ORIGINS` in `.env`:
```env
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

2. Frontend-URL muss übereinstimmen

3. Starten Sie den Server neu

---

### 🔴 Problem: "Email not sending / SMTP Error"

**Ursache:** E-Mail-Konfiguration falsch

**Lösung:**

1. Überprüfen Sie `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password  # Nicht das normale Passwort!
EMAIL_USE_TLS=True
```

2. Für Gmail: [App Password generieren](https://support.google.com/accounts/answer/185833)

3. Test-E-Mail senden:
```bash
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Test Message', 'noreply@videoflix.com', ['recipient@example.com'])
```

---

### 🔴 Problem: "Static files not loading" (404 Fehler)

**Ursache:** Static files nicht gesammelt

**Lösung:**
```bash
python manage.py collectstatic --noinput
```

In Docker:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

---

### 🔴 Problem: "Video-Konvertierung läuft nicht"

**Ursache:** RQ Worker läuft nicht

**Lösung:**

```bash
# Worker starten
python manage.py rqworker default

# In Docker:
docker-compose exec web python manage.py rqworker default
```

---

### 🔴 Problem: "ffmpeg: command not found"

**Ursache:** ffmpeg nicht installiert

**Lösung:**

```bash
# Windows (Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Docker sollte es bereits haben
```

---

### 🔴 Problem: "Migrations Fehler / 'auth_app_customuser' does not exist"

**Ursache:** Migrationen aus alter Version

**Lösung:**

```bash
# Datenbank zurücksetzen (Vorsicht: Löscht alle Daten!)
python manage.py flush

# Oder mit Docker:
docker-compose exec web python manage.py flush

# Dann neu migrieren:
python manage.py migrate
```

---

## Entwicklung

### Projektstruktur

```
Videoflix/
├── auth_app/               # Authentifizierungs-App
│   ├── api/
│   │   ├── authentication.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── migrations/
│   ├── templates/          # E-Mail-Templates
│   └── models.py
├── video_app/              # Video-Management-App
│   ├── api/
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── migrations/
│   └── models.py
├── core/                   # Projekt-Konfiguration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── backend.Dockerfile
└── README.md
```

### Wichtige Dateien

- **settings.py**: Django-Konfiguration
- **urls.py**: URL-Routing (core) und App-URLs
- **views.py**: API-Views (auth_app und video_app)
- **serializers.py**: Daten-Serialisierung für APIs
- **models.py**: Datenbankmodelle

### Tests ausführen

```bash
# Alle Tests
python manage.py test

# Specific app
python manage.py test auth_app

# Mit Verbose-Output
python manage.py test -v 2
```

### Datenbank-Migrationen

```bash
# Neue Migration erstellen
python manage.py makemigrations

# Migrationen anschauen
python manage.py showmigrations

# Spezifische Migration durchführen
python manage.py migrate auth_app 0001

# Letzte Migration zurücknehmen
python manage.py migrate auth_app 0001
```

### Management Commands

```bash
# Admin-User erstellen
python manage.py createsuperuser

# Django Shell öffnen
python manage.py shell

# Database schöpfen
python manage.py dbshell

# Static Files sammeln
python manage.py collectstatic

# RQ Worker starten
python manage.py rqworker default

# RQ Admin-Interface
python manage.py rqworker-admin
```

---

## Zusätzliche Ressourcen

- [Django Dokumentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Dokumentation](https://www.postgresql.org/docs/)
- [Redis Dokumentation](https://redis.io/documentation)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [HLS Streaming](https://en.wikipedia.org/wiki/HTTP_Live_Streaming)

---

## Lizenz

Dieses Projekt ist proprietary.

## Support

Bei Fragen oder Problemen:
1. Überprüfen Sie die "Häufige Probleme" Sektion
2. Überprüfen Sie die Django/DRF Dokumentation
3. Kontaktieren Sie den Entwickler

---

**Letzte Aktualisierung:** 25. Februar 2026
