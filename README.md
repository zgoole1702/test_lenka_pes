# Sensor Dashboard — Render.com Deployment

Flask + PostgreSQL app for receiving and displaying RPi sensor data.

## Files
- `app.py` — Flask server (API + dashboard)
- `rpi_sender.py` — Script to run on your Raspberry Pi
- `requirements.txt` — Python dependencies
- `Procfile` — Start command for Render

---

## Deploy to Render (Free, ~10 minutes)

### Step 1 — Push to GitHub
Create a free GitHub account, make a new repo, and upload all these files.

### Step 2 — Create PostgreSQL database on Render
1. Go to https://render.com → sign up free
2. Dashboard → **New → PostgreSQL**
3. Name it anything (e.g. `sensor-db`)
4. Plan: **Free**
5. Click **Create Database**
6. Wait ~1 min, then copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3 — Create Web Service on Render
1. Dashboard → **New → Web Service**
2. Connect GitHub → select your repo
3. Settings:
   - **Name**: anything (e.g. `sensor-dashboard`)
   - **Runtime**: Python 3
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free
4. Scroll to **Environment Variables** → Add:
   - Key: `DATABASE_URL`
   - Value: paste the Internal Database URL from Step 2
5. Click **Create Web Service**

### Step 4 — Get your URL
After deploy finishes (~2 min), your dashboard is live at:
`https://sensor-dashboard.onrender.com`

---

## RPi Setup

1. Copy `rpi_sender.py` to your Raspberry Pi
2. Edit `SERVER_URL` to your Render URL
3. Fill in `read_sensors()` with your actual sensor code
4. Install requests: `pip3 install requests`
5. Run: `python3 rpi_sender.py`

**Auto-start on boot:**
```
crontab -e
# Add this line:
@reboot python3 /home/pi/rpi_sender.py >> /home/pi/sensor.log 2>&1 &
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web dashboard |
| POST | `/data` | Submit sensor reading (JSON) |
| GET | `/api/readings?limit=100` | Raw JSON data |

### POST /data body
```json
{
  "value1": 23.5,
  "value2": 60.1,
  "value3": 1013.2,
  "value4": 0.5,
  "value5": 99.9,
  "date": "2024-01-15",
  "time": "14:30:00"
}
```
