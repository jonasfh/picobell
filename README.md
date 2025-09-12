# PicoBell Doorbell Project

Prosjekt for å gjøre eksisterende porttelefon smartere.   Målet er å kunne motta ringesignaler på mobil, og åpne døren fra en egen app – uten å miste dagens funksjonalitet.  

Se [docs](docs/) for detaljert dokumentasjon.

## Struktur

    doorbell-project/
    │
    ├── pico/                # Alt for Pico-mikrokontrolleren
    │   ├── firmware/        # C++/Micropython/Pico SDK kode
    │   └── docs/            # Notater om HW-tilkobling, skjema osv.
    │
    ├── server/           # PHP-backend (API)
    │   ├── public/       # Web-root (index.php)
    │   ├── src/          # PHP-kode (controllers, services)
    │   ├── config/       # Konfig (dotenv, secrets, firebase.json)
    │   ├── vendor/       # Composer dependencies
    │   ├── composer.json # Composer config
    │   └── composer.lock
    │
    ├── mobile/              # Klient-app
    │   ├── android/         # Android-kode
    │   ├── ios/             # (ev. senere)
    │   └── shared/          # Felles ressurser (ikon, assets, logoer)
    │
    ├── docs/                # Arkitekturdiagrammer, flyt, API-spec
    │
    └── .gitignore


## Arkitektur (oversikt)

```mermaid
flowchart TD
    PICO[Raspberry Pi Pico] -- "HTTP(S) client" --> SERVER[Python backend]
    SERVER -- "Push notification (FCM)" --> ANDROID[Android app]
    SERVER -- "Push notification (APNs)" --> IOS[iOS app]
    ANDROID <--> SERVER
    IOS <--> SERVER

