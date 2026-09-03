#!/usr/bin/env python3
"""Radio Liepāja — raidījumu grafiks (FastAPI).
Viens serviss: pasniedz lapu (index.html) un apstrādā saglabāšanu (data.json).
Domāts Coolify konteineram ar persistent volume mapē /data.
"""
import json
import os
import secrets
import tempfile

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(title="Radio Liepāja grafiks")
security = HTTPBasic()

# --- konfigurācija no vides mainīgajiem (Coolify Environment Variables) ---
# DATA_DIR = persistent volume mape (Coolify: Persistent Storage -> /data)
DATA_DIR = os.environ.get("DATA_DIR", "/data")
DATA_FILE = os.path.join(DATA_DIR, "data.json")

# admin akreditācija (Coolify env: ADMIN_USER, ADMIN_PASS)
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "liepaja2026")

# statiskie faili (index.html) — konteinerā blakus šim failam
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "static", "index.html")

ALLOWED_FIELDS = {"date", "start", "end", "name", "host", "genre", "desc", "status"}
ALLOWED_STATUS = {"apstiprināts", "melnraksts", "atcelts"}


def _ensure_data():
    """Nodrošina, ka /data un data.json eksistē (pirmā palaišana)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        seed = [
            {"date": "2026-09-07", "start": "07:00", "end": "09:00",
             "name": "Rīta Osta", "host": "Ilze Bērziņa", "genre": "Rīta ēteris",
             "desc": "Rīta ziņas un mūzika.", "status": "apstiprināts"},
        ]
        _write_atomic(seed)


def _write_atomic(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


def _clean(rec):
    out = {k: ("" if rec.get(k) is None else str(rec.get(k, ""))) for k in ALLOWED_FIELDS}
    if out["status"] not in ALLOWED_STATUS:
        out["status"] = "melnraksts"
    return out


def check_admin(cred: HTTPBasicCredentials = Depends(security)):
    """HTTP Basic Auth pārbaude (konstantā laikā, pret timing uzbrukumiem)."""
    u_ok = secrets.compare_digest(cred.username, ADMIN_USER)
    p_ok = secrets.compare_digest(cred.password, ADMIN_PASS)
    if not (u_ok and p_ok):
        raise HTTPException(status_code=401, detail="Nav autorizēts",
                            headers={"WWW-Authenticate": "Basic"})
    return cred.username


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def index():
    if not os.path.exists(INDEX_FILE):
        return JSONResponse({"error": "index.html nav atrasts"}, status_code=500)
    return FileResponse(INDEX_FILE, media_type="text/html")


@app.get("/data.json")
def get_data():
    _ensure_data()
    return FileResponse(DATA_FILE, media_type="application/json",
                        headers={"Cache-Control": "no-store"})


@app.post("/api/grafiks/save")
async def save(request: Request, user: str = Depends(check_admin)):
    try:
        body = await request.body()
        data = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="Nederīgs JSON")
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Sagaidīts JSON masīvs")
    cleaned = [_clean(r) for r in data if isinstance(r, dict)]
    try:
        _write_atomic(cleaned)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Neizdevās saglabāt: {e}")
    return {"ok": True, "count": len(cleaned)}


_ensure_data()
