# ============================================================
# Sensor Dashboard — Flask server
# Prima podatke sa RPi, čuva u PostgreSQL bazi,
# i prikazuje ih na web stranici.
# ============================================================

from flask import Flask, request, jsonify, render_template_string
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)

# URL baze se čita iz environment varijable (postavlja se na Render-u)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    """Otvara konekciju ka PostgreSQL bazi."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Kreira tabelu ako već ne postoji. Pokreće se pri startu aplikacije."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id SERIAL PRIMARY KEY,
                    value1 REAL,
                    value2 REAL,
                    value3 REAL,
                    value4 REAL,
                    value5 REAL,
                    date TEXT,
                    time TEXT,
                    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()

# Inicijalizuj bazu pri pokretanju
init_db()

# ============================================================
# HTML šablon za dashboard stranicu
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sensor Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0e1a; --panel: #0f1628; --border: #1e2d4a;
    --accent: #00d4ff; --accent2: #00ff9d; --text: #c8d8f0; --muted: #4a6080;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Exo 2', sans-serif; min-height: 100vh; }
  body::before {
    content: ''; position: fixed; inset: 0;
    background: radial-gradient(ellipse at 20% 20%, rgba(0,212,255,0.04) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 80%, rgba(0,255,157,0.03) 0%, transparent 60%);
    pointer-events: none;
  }
  header {
    padding: 24px 32px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 16px;
    background: rgba(15,22,40,0.8); backdrop-filter: blur(10px);
    position: sticky; top: 0; z-index: 10;
  }
  .logo { width: 36px; height: 36px; border: 2px solid var(--accent); border-radius: 8px; display: grid; place-items: center; color: var(--accent); font-size: 18px; font-family: 'Share Tech Mono', monospace; }
  header h1 { font-size: 1.2rem; font-weight: 600; letter-spacing: 0.08em; }
  header h1 span { color: var(--accent); }
  .status-dot { margin-left: auto; width: 8px; height: 8px; border-radius: 50%; background: var(--accent2); box-shadow: 0 0 10px var(--accent2); animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
  .container { max-width: 1200px; margin: 0 auto; padding: 32px; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 32px; }
  .stat-card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 20px; position: relative; overflow: hidden; transition: border-color 0.2s; }
  .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--accent), var(--accent2)); opacity: 0.6; }
  .stat-card:hover { border-color: var(--accent); }
  .stat-label { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
  .stat-value { font-family: 'Share Tech Mono', monospace; font-size: 1.8rem; color: var(--accent); line-height: 1; }
  .stat-sub { font-size: 0.75rem; color: var(--muted); margin-top: 4px; }
  .section-title { font-size: 0.75rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
  .section-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }
  .table-wrap { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
  table { width: 100%; border-collapse: collapse; }
  th { padding: 12px 16px; text-align: left; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); background: rgba(0,0,0,0.2); font-weight: 400; font-family: 'Share Tech Mono', monospace; }
  td { padding: 12px 16px; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem; border-top: 1px solid var(--border); color: var(--text); }
  tr:hover td { background: rgba(0,212,255,0.03); }
  tr:first-child td { border-top: none; }
  .val { color: var(--accent); }
  .datetime { color: var(--muted); font-size: 0.78rem; }
  .empty { text-align: center; padding: 48px; color: var(--muted); }
  .refresh-btn { background: transparent; border: 1px solid var(--border); color: var(--accent); padding: 6px 14px; border-radius: 6px; font-size: 0.75rem; font-family: 'Share Tech Mono', monospace; cursor: pointer; letter-spacing: 0.05em; transition: all 0.2s; margin-left: auto; display: block; margin-bottom: 12px; }
  .refresh-btn:hover { background: rgba(0,212,255,0.1); border-color: var(--accent); }
  .api-box { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-top: 32px; }
  .api-box code { display: block; background: rgba(0,0,0,0.4); border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: var(--accent2); margin-top: 12px; white-space: pre-wrap; word-break: break-all; }
</style>
</head>
<body>
<header>
  <div class="logo">S</div>
  <h1>SENSOR <span>DASHBOARD</span></h1>
  <div class="status-dot"></div>
</header>
<div class="container">
  {% if latest %}
  <div class="stats-grid">
    {% for i in range(1,6) %}
    <div class="stat-card">
      <div class="stat-label">Value {{ i }}</div>
      <div class="stat-value">{{ latest['value' ~ i] if latest['value' ~ i] is not none else '—' }}</div>
      <div class="stat-sub">poslednje očitavanje</div>
    </div>
    {% endfor %}
    <div class="stat-card">
      <div class="stat-label">Ukupno očitavanja</div>
      <div class="stat-value">{{ total }}</div>
      <div class="stat-sub">{{ latest.date }} {{ latest.time }}</div>
    </div>
  </div>
  {% endif %}
  <div class="section-title">Poslednja očitavanja</div>
  <button class="refresh-btn" onclick="location.reload()">↻ OSVJEŽI</button>
  <div class="table-wrap">
    {% if rows %}
    <table>
      <thead><tr><th>#</th><th>V1</th><th>V2</th><th>V3</th><th>V4</th><th>V5</th><th>Datum</th><th>Vreme</th></tr></thead>
      <tbody>
        {% for row in rows %}
        <tr>
          <td class="datetime">{{ row.id }}</td>
          <td class="val">{{ row.value1 }}</td>
          <td class="val">{{ row.value2 }}</td>
          <td class="val">{{ row.value3 }}</td>
          <td class="val">{{ row.value4 }}</td>
          <td class="val">{{ row.value5 }}</td>
          <td class="datetime">{{ row.date }}</td>
          <td class="datetime">{{ row.time }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div class="empty">Nema podataka. Čeka se na očitavanja sa senzora...</div>
    {% endif %}
  </div>
  <div class="api-box">
    <div class="section-title" style="margin-bottom:12px">Slanje podataka sa RPi</div>
    Pošalji podatke sa Raspberry Pi koristeći curl:
    <code>curl -X POST https://TVOJ-APP.onrender.com/data \
  -H "Content-Type: application/json" \
  -d '{"value1": 23.5, "value2": 60.1, "value3": 1013.2, "value4": 0.5, "value5": 99.9, "date": "2026-02-26", "time": "19:10:00"}'</code>
  </div>
</div>
<!-- Automatsko osvežavanje svakih 30 sekundi -->
<script>setTimeout(() => location.reload(), 30000);</script>
</body>
</html>
"""

# ============================================================
# Rute (URL endpoint-i)
# ============================================================

@app.route("/")
def dashboard():
    """Prikazuje glavni dashboard sa tabelom očitavanja."""
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Uzmi poslednjih 100 očitavanja, sortirano od najnovijeg
            cur.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 100")
            rows = cur.fetchall()
            # Ukupan broj očitavanja u bazi
            cur.execute("SELECT COUNT(*) as cnt FROM readings")
            total = cur.fetchone()["cnt"]
    latest = rows[0] if rows else None
    return render_template_string(HTML_TEMPLATE, rows=rows, latest=latest, total=total)


@app.route("/data", methods=["POST"])
def receive_data():
    """
    Prima JSON podatke sa RPi i čuva ih u bazi.
    Očekivani format:
    {
        "value1": 23.5, "value2": 60.1, "value3": 1013.2,
        "value4": 0.5, "value5": 99.9,
        "date": "2026-02-26", "time": "19:10:00"
    }
    """
    d = request.get_json(force=True)
    if not d:
        return jsonify({"error": "Nema JSON tela u zahtevu"}), 400
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO readings (value1, value2, value3, value4, value5, date, time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    d.get("value1"), d.get("value2"), d.get("value3"),
                    d.get("value4"), d.get("value5"),
                    d.get("date"), d.get("time")
                ))
            conn.commit()
        return jsonify({"ok": True}), 201
    except Exception as e:
        # Vrati grešku ako nešto pođe po zlu
        return jsonify({"error": str(e)}), 500


@app.route("/api/readings")
def api_readings():
    """Vraća očitavanja kao JSON — korisno za integraciju sa drugim alatima."""
    limit = min(int(request.args.get("limit", 100)), 1000)
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM readings ORDER BY id DESC LIMIT %s", (limit,))
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


# Pokretanje lokalnog servera (samo za testiranje, ne za produkciju)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
