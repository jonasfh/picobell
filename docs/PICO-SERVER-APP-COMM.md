Kommunikasjon mellom Pico og Android/iOS App
============================================

Diagrammet nedenfor beskriver kommunikasjonen mellom Pico, serveren (API) og 
enhetene (appene) ved bruk av Firebase Cloud Messaging (FCM).

```mermaid
sequenceDiagram
    participant P as Pico
    participant S as Server (API)
    participant D as Devices (App)
    
    P->>S: POST /doorbell/ring (med pico_serial)
    S->>D: FCM-notification (alle devices i samme apartment)
    D->>S: POST /doorbell/open (bruker trykker "åpne")
    loop 3 minutter
        P->>S: GET /doorbell/status?pico_serial=XYZ
        S-->>P: { "open": true/false }
    end
    alt open = true
        P->>P: Åpne døra
    else
        P->>P: Gjør ingenting
    end
```


