# Sensor Dashboard — Uputstvo za Postavljanje

Kompletan vodič za postavljanje sistema koji prima podatke sa Raspberry Pi uređaja, čuva ih u bazi podataka i prikazuje ih na web stranici.

---

## Šta ćeš dobiti

- **Web server** (Flask) koji prima podatke sa RPi i čuva ih u bazi
- **PostgreSQL baza** — podaci se nikad ne gube
- **Web dashboard** — pregled svih očitavanja u realnom vremenu
- **Besplatno hostovanje** na Render.com — bez kreditne kartice
- **URL** tipa `https://tvoj-naziv.onrender.com`

---

## Potrebni nalozi (oba besplatna)

1. **GitHub** — https://github.com — za čuvanje koda
2. **Render** — https://render.com — za hostovanje aplikacije i baze

---

## Korak 1 — Postavi GitHub repozitorijum

1. Idi na https://github.com i napravi nalog ako nemaš
2. Klikni **New repository**
3. Daj mu ime (npr. `sensor-dashboard`)
4. Ostavi sve ostalo kao podrazumevano, klikni **Create repository**
5. Klikni **Add file → Upload files**
6. Dodaj ova 3 fajla (dati su ispod):
   - `app.py`
   - `requirements.txt`
   - `Procfile`
7. Klikni **Commit changes**

---

## Korak 2 — Napravi PostgreSQL bazu na Render-u

> 📸 *[Ovde ubaci screenshot stranice "New Postgres" sa Render-a — zamagli DATABASE_URL]*

1. Idi na https://render.com i napravi nalog
2. Dashboard → **New → PostgreSQL**
3. Ime: bilo šta (npr. `sensor-db`)
4. Region: **Oregon (US West)** — ostavi podrazumevano
5. Plan: **Free** ($0/mesec, 1GB storage)
6. Klikni **Create Database**
7. Sačekaj ~1 minut dok se kreira
8. Klikni na bazu → skroluj do sekcije **Connections**
9. Kopiraj **Internal Database URL** (počinje sa `postgresql://...`)

---

## Korak 3 — Napravi Web Servis na Render-u

> 📸 *[Ovde ubaci screenshot stranice "New Web Service" sa Render-a]*

1. Dashboard → **New → Web Service**
2. Poveži GitHub nalog → izaberi repozitorijum
3. Podesi sledeće:

| Polje | Vrednost |
|-------|----------|
| **Language** | Python |
| **Branch** | main |
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Instance Type** | Free |

4. Skroluj do **Environment Variables** → klikni **Add Environment Variable**:

| Name | Value |
|------|-------|
| `DATABASE_URL` | *(nalepi URL koji si kopirao u Koraku 2)* |

5. Klikni **Deploy Web Service**

---

## Korak 4 — Prati deploy

> 📸 *[Ovde ubaci screenshot loga sa uspešnim deployom]*

Render će prikazati log. Čekaj da vidiš:

```
==> Build successful 🎉
==> Deploying...
==> Your service is live 🎉
```

Ako deploy uspe, tvoj dashboard je dostupan na:
**`https://naziv-servisa.onrender.com`**

### Česti problemi

| Greška | Rešenje |
|--------|---------|
| `Could not open requirements file` | Fajlovi nisu uploadovani na GitHub — ponovi Korak 1 |
| `connection refused` na bazu | `DATABASE_URL` nije dobro unet — proveri env varijablu |
| Status **Failed** odmah | Klikni **Manual Deploy → Deploy latest commit** |

---

## Korak 5 — Testiraj sa računara (Fedora/Linux)

Pre nego što poveže RPi, možeš testirati sa računara. Otvori terminal i pokreni:

### Pošalji jedno očitavanje:
```bash
curl -X POST https://naziv-servisa.onrender.com/data \
  -H "Content-Type: application/json" \
  -d '{"value1": 23.5, "value2": 60.1, "value3": 1013.2, "value4": 0.5, "value5": 99.9, "date": "2026-02-26", "time": "19:10:00"}'
```

Treba da dobiješ odgovor: `{"ok": true}`

### Pošalji 10 nasumičnih očitavanja odjednom:
```bash
for i in {1..10}; do
  curl -X POST https://naziv-servisa.onrender.com/data \
    -H "Content-Type: application/json" \
    -d "{\"value1\": $(shuf -i 20-30 -n1).$(shuf -i 0-9 -n1), \"value2\": $(shuf -i 40-80 -n1).$(shuf -i 0-9 -n1), \"value3\": $(shuf -i 1000-1020 -n1).$(shuf -i 0-9 -n1), \"value4\": $(shuf -i 0-5 -n1).$(shuf -i 0-9 -n1), \"value5\": $(shuf -i 90-100 -n1).$(shuf -i 0-9 -n1), \"date\": \"2026-02-26\", \"time\": \"19:$(shuf -i 10-59 -n1):00\"}"
  sleep 0.5
done
```

Nakon toga osvježi dashboard u browseru — treba da se pojavi 10 redova sa podacima.

---

## Korak 6 — Podesi Raspberry Pi

1. Kopiraj fajl `rpi_sender.py` na Raspberry Pi (npr. u `/home/pi/`)
2. Otvori fajl i izmeni **samo jedan red** — URL servera:

```python
SERVER_URL = "https://naziv-servisa.onrender.com/data"  # ← izmeni ovo
```

3. Instaliraj potrebnu biblioteku:
```bash
pip3 install requests
```

4. Pokreni skriptu:
```bash
python3 rpi_sender.py
```

5. Izmeni funkciju `read_sensors()` da vraća stvarne vrednosti sa tvojih senzora umesto test vrednosti.

### Automatski start pri pokretanju RPi

Da bi se skripta automatski pokretala kada se RPi upali:

```bash
crontab -e
```

Dodaj na kraj fajla:
```
@reboot python3 /home/pi/rpi_sender.py >> /home/pi/sensor.log 2>&1 &
```

---

## Fajlovi — Objašnjenje

### `app.py` — Glavni server
Flask aplikacija koja:
- Prima podatke od RPi na `POST /data`
- Čuva ih u PostgreSQL bazi
- Prikazuje dashboard na `GET /`

### `requirements.txt` — Python zavisnosti
```
flask>=3.0.0
gunicorn>=21.0.0
psycopg2-binary>=2.9.0
```

### `Procfile` — Komanda za pokretanje na Render-u
```
web: gunicorn app:app --bind 0.0.0.0:$PORT
```

### `rpi_sender.py` — Skripta za RPi
Šalje podatke sa senzora na server svakih N sekundi.

---

## API Referenca

| Metoda | Putanja | Opis |
|--------|---------|------|
| `GET` | `/` | Web dashboard |
| `POST` | `/data` | Prima novo očitavanje (JSON) |
| `GET` | `/api/readings?limit=100` | Vraća podatke kao JSON |

### Format podataka za `POST /data`:
```json
{
  "value1": 23.5,
  "value2": 60.1,
  "value3": 1013.2,
  "value4": 0.5,
  "value5": 99.9,
  "date": "2026-02-26",
  "time": "19:10:00"
}
```

---

## Napomene

- **Besplatni Render tier** — servis "zaspi" nakon 15 minuta neaktivnosti, prvo buđenje traje ~30 sekundi. Ako RPi šalje podatke redovno, servis ostaje budan.
- **Baza podataka** — besplatni PostgreSQL na Render-u ima 1GB prostora, što je dovoljno za milione očitavanja.
- **Sigurnost** — nikad ne stavljaj `DATABASE_URL` u kod ili na GitHub. Uvek koristiti Environment Variables na Render-u.
