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
flowchart LR
    subgraph HW[Raspberry Pi Pico + Porttelefon]
        BELL[Ringesignal deteksjon] --> PICO
        BTN["Døråpner-knapp (relé)"] --> PICO
        PICO -- "MikroPython/C++" --> WIFI((WiFi))
    end

    WIFI --> SERVER[Python backend på NREC]

    subgraph SERVER
        API["REST API (FastAPI/Flask)"]
        QUEUE["Message Queue (opsjon)"]
        FCM[Firebase Cloud Messaging]
    end

    SERVER <--> API
    API --> FCM

    FCM --> APP[Android/iOS App]
    APP <--> API
```

## Komponenter

* Pico: Leser ringesignalet, styrer døråpner.
* Server: Python (FastAPI/Flask). Håndterer API, push-varsler, autentisering.
* Mobilapp: Android (og evt. iOS). Mottar varsler, gir bruker mulighet til å åpne dør.

## Database

Det er behov for en database for følgende oppgaver: 

* Registrering av brukere
* Registrering av leiligheter/picoer


```mermaid
erDiagram
    USERS {
        int      id
        string   email
        string   password_hash
        string   display_name
        string   phone
        datetime created_at
        datetime updated_at
    }

    APARTMENTS {
        int      id
        string   name
        string   address
        string   pico_id
        string   fw_version
        string   metadata
        datetime created_at
    }

    USER_APARTMENT {
        int      id
        int      user_id
        int      apartment_id
        string   role
        datetime created_at
    }

    DEVICE_TOKENS {
        int      id
        int      user_id
        string   token
        string   platform
        datetime created_at
        datetime last_seen
    }

    AUDIT_LOG {
        int      id
        int      user_id
        string   event_type
        string   details
        string   ip
        datetime created_at
    }

    USERS ||--o{ USER_APARTMENT : has
    APARTMENTS ||--o{ USER_APARTMENT : has
    USERS ||--o{ DEVICE_TOKENS : owns
    USERS ||--o{ AUDIT_LOG : generates
```

## Sikkerhet

* Pico fungerer kun som klient, aldri åpen port mot internett.
* Server kjører med TLS (nginx som reverse proxy).
* Push-varsler håndteres via Firebase (Android) og evt. APNs (iOS).
* API autentisering med tokens (JWT eller lignende).
