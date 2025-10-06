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

## Systemoversikt

```mermaid
flowchart LR
    subgraph Mobile["Android app"]
        M1["Bruker logger inn med Google"]
        M2["Får JWT fra server"]
        M3["Kaller /profile-endepunkter"]
    end

    subgraph Web["Web (test/cli)"]
        W1["Kan kalle auth/google"]
        W2["Kan teste med JWT"]
    end

    subgraph Server["Picobell server (Slim/PHP)"]
        S1["AuthController"]
        S2["ProfileController"]
        S3["DevicesController"]
        S4["ApartmentsController"]
        S5["AdminController"]
    end

    subgraph DB["SQLite (dev) / Postgres (prod senere?)"]
        D1["users"]
        D2["devices"]
        D3["apartments"]
        D4["user_apartment (role)"]
    end

    M1 --> S1
    W1 --> S1
    S1 --> D1
    S1 --> M2
    S1 --> W2
    M3 --> S2
    M3 --> S3
    M3 --> S4
    S2 --> D1
    S3 --> D2
    S4 --> D3
    S4 --> D4
    S5 --> D1
    S5 --> D2
    S5 --> D3
```

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

## Authentisering

```mermaid
sequenceDiagram
    participant U as User (Android/Web)
    participant G as Google OAuth
    participant S as Picobell Server
    participant DB as Database

    U->>G: Login with Google
    G-->>U: Google ID token
    U->>S: POST /auth/google (ID token)
    S->>G: Verify ID token
    G-->>S: Token valid + user info
    S->>DB: Lookup user by email
    DB-->>S: User found or new created
    S-->>U: JWT (id, email, role)

    U->>S: Call protected endpoint (with Bearer JWT)
    S->>S: Verify JWT signature
    S->>DB: (optional) fetch user details
    DB-->>S: User info
    S-->>U: Response
```
