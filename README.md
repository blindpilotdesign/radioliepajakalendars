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

