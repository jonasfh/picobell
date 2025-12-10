Koblingsskjema for dørtelefon / Pico
====================================

Enkel oversikt over hvordan piko kan kobles opp

flowchart TD

    PORT["28–30 V<br>Porttelefon-linje"]

    %% Power path
    PORT --> BREG["LM2596<br>(buck-regulator)"]
    BREG --> VSYS["Pico VSYS (5V)"]

    %% Signal tap
    PORT --> R1["R1 91kΩ"]
    R1 --> R2["R2 10kΩ"]
    R2 --> FILT["100 nF<br>RC-filter"]
    FILT --> SER["10kΩ serie-motstand"]
    SER --> ADC["Pico ADC input"]

    %% Protection
    ADC -->|clamp| DIO["Schottky diode<br>til 3.3V"]
    DIO --> V33["3.3V rail"]

    R2 --> GND
    BREG --> GND
    V33 --> GND
