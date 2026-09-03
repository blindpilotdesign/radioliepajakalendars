# Radio Liepāja — grafiks (Coolify projekts, FastAPI)

Atsevišķs, neatkarīgs projekts. Viens konteiners pasniedz gan lapu, gan
saglabāšanas API. Dati glabājas persistent volume — pārdzīvo restartus/deploy.

## Faili
| Fails | Nozīme |
|---|---|
| `app.py` | FastAPI serviss — pasniedz lapu + apstrādā saglabāšanu |
| `static/index.html` | Kalendāra lapa (režģis, admin, atkārtošana) |
| `Dockerfile` | Konteinera būve |
| `docker-compose.yml` | Compose variants (ja deploy caur Compose) |
| `requirements.txt` | Python atkarības |

## Kā tas strādā
- `GET /` → lapa (index.html)
- `GET /data.json` → grafika dati (lasa lapa un tava live sistēma)
- `POST /api/grafiks/save` → saglabā (prasa HTTP Basic Auth)
- `GET /health` → veselības pārbaude Coolify monitoringam
- Dati: `/data/data.json` konteinerā = **persistent volume** uz servera

---

## PIEEJA 1 — GitHub repo (ieteicams)

1. Izveido GitHub repo (zem Ētera Osta konta), iegrūd visus šos failus.
2. Coolify: **New Resource → Application → Public/Private Repository**.
3. Norādi repo; Build Pack: **Dockerfile**.
4. **Persistent Storage** (svarīgi!): pievieno volume:
   - Name: `grafiks_data`
   - Mount Path: `/data`
5. **Environment Variables**:
   - `DATA_DIR` = `/data`
   - `ADMIN_USER` = `admin`  (vai cits)
   - `ADMIN_PASS` = `tava_stiprā_parole`
6. **Port**: 8000 (Coolify parasti noķer no Dockerfile EXPOSE).
7. Pievieno domēnu (piem. `grafiks.radioliepaja.lv` vai `radioliepaja.lv/grafiks`)
   Coolify sadaļā **Domains**. Coolify pats sakārto HTTPS (Let's Encrypt).
8. Deploy. Katrs `git push` → auto-redeploy.

---

## PIEEJA 2 — Docker Compose (bez Git)

1. Coolify: **New Resource → Docker Compose**.
2. Ielīmē `docker-compose.yml` saturu (vai norādi to).
3. Pārliecinies, ka volume `grafiks_data:/data` ir saglabāts (tas ir compose failā).
4. Nomaini `ADMIN_PASS` compose failā.
5. Pievieno domēnu + portu 8000 kā Pieejā 1.
6. Deploy. Izmaiņas jāaugšupielādē rokā (nav auto-deploy kā ar Git).

> Abām pieejām KRITISKI: persistent volume uz `/data`. Bez tā katrs
> redeploy izdzēš `data.json` un grafiks pazūd.

---

## Pēc deploy — pārbaude
1. Atver domēnu → jāredz kalendārs ar paraugu ierakstu.
2. `/health` → `{"ok":true}`.
3. **Pieteikties** lapā (tas pats ADMIN_USER/ADMIN_PASS).
4. Pievieno raidījumu, spied **Saglabāt** → pārlūks prasa Basic Auth
   (ievadi to pašu admin/paroli) → "Saglabāts serverī ✓".
5. Restartē konteineru Coolify → dati paliek (volume tests).

## Drošība
- ADMIN_PASS glabājas Coolify env, NE kodā. Nomaini noklusējumu.
- Saglabāšanu sargā HTTP Basic Auth serverī (app.py, konstantā laika salīdzinājums).
- Klienta parole index.html tikai atver admin UI — liec to vienādu ar ADMIN_PASS.
  (Vari to arī noņemt un paļauties tikai uz servera Basic Auth.)

## Live savienojums
`data.json` lauki: date, start, end, name, host, genre, desc, status.
Tava mājaslapa lasa `https://TAVS_DOMENS/data.json` un rāda live.
Filtrs: status == "apstiprināts" → ēterā.
