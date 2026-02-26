#!/usr/bin/env python3
# ============================================================
# RPi Sender — Skripta za slanje podataka sa senzora
# Pokreće se na Raspberry Pi uređaju.
# Šalje očitavanja na web server u zadatim intervalima.
# ============================================================

import requests
import datetime
import time
import random  # Samo za testne podatke — ukloni kada povežeš prave senzore

# ============================================================
# PODEŠAVANJA — izmeni ovo!
# ============================================================

# URL tvog servera na Render-u (zameni sa stvarnim URL-om)
SERVER_URL = "https://TVOJ-APP.onrender.com/data"

# Koliko sekundi između dva slanja (npr. 60 = jednom u minutu)
INTERVAL_SEKUNDI = 60

# ============================================================


def ocitaj_senzore():
    """
    IZMENI OVU FUNKCIJU sa stvarnim očitavanjima sa tvojih senzora!
    Trenutno vraća nasumične vrednosti samo za testiranje.

    Primer za DHT22 senzor (temperatura i vlažnost):
        import Adafruit_DHT
        vlaznost, temperatura = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
        return {
            "value1": temperatura,
            "value2": vlaznost,
            ...
        }
    """
    return {
        "value1": round(random.uniform(20, 30), 2),   # npr. temperatura (°C)
        "value2": round(random.uniform(40, 80), 2),   # npr. vlažnost (%)
        "value3": round(random.uniform(1000, 1020), 2),  # npr. pritisak (hPa)
        "value4": round(random.uniform(0, 100), 2),   # npr. svetlost (%)
        "value5": round(random.uniform(0, 5), 2),     # npr. napon (V)
    }


def posalji_podatke():
    """Čita senzore i šalje podatke na server."""
    sada = datetime.datetime.now()
    ocitavanja = ocitaj_senzore()

    # Pripremi podatke za slanje
    payload = {
        **ocitavanja,
        "date": sada.strftime("%Y-%m-%d"),   # Format: 2026-02-26
        "time": sada.strftime("%H:%M:%S"),   # Format: 19:10:00
    }

    try:
        odgovor = requests.post(SERVER_URL, json=payload, timeout=10)
        if odgovor.status_code == 201:
            print(f"[{sada}] Uspešno poslato: {ocitavanja}")
        else:
            print(f"[{sada}] Greška servera {odgovor.status_code}: {odgovor.text}")
    except requests.exceptions.ConnectionError:
        print(f"[{sada}] Nema konekcije — server nije dostupan")
    except requests.exceptions.Timeout:
        print(f"[{sada}] Timeout — server nije odgovorio na vreme")
    except Exception as e:
        print(f"[{sada}] Neočekivana greška: {e}")


# ============================================================
# Glavna petlja — šalje podatke u beskonačnoj petlji
# ============================================================
if __name__ == "__main__":
    print(f"Pokrenuto! Šaljem podatke svakih {INTERVAL_SEKUNDI}s na {SERVER_URL}")
    print("Pritisni Ctrl+C za zaustavljanje.\n")

    while True:
        posalji_podatke()
        time.sleep(INTERVAL_SEKUNDI)
