# Setup

1. **Username** : dans `scripts/config.py`, remplace `USERNAME = "YOUR_GITHUB_USERNAME"`.
2. **Repo** : crée le repo spécial qui porte exactement ton username, puis pousse ce dossier.
   ```bash
   gh repo create <username> --public --source . --push
   ```
3. **Actions** : Settings → Actions → General → Workflow permissions → *Read and write*.
   Lance une première fois *Update profile art* depuis l'onglet Actions (`workflow_dispatch`).

## Rebuild local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements-art.txt

./build.sh                  # portrait = surface de vol implicite, heatmap live
./build.sh source-photo.jpg # portrait ASCII à partir d'une photo
DEMO=1 ./build.sh           # données synthétiques (preview hors ligne)
STATIC=1 python scripts/make_info_card.py   # frame figée pour Quick Look
```

## Où modifier quoi

| Fichier | Rôle |
|---|---|
| `scripts/config.py` | username, prompt, palette, contenu de la carte neofetch |
| `scripts/make_vol_surface.py` | surface par défaut : $\sigma(k,T) = \mathrm{atm}(T) + \mathrm{skew}(T)\,k + \mathrm{conv}(T)\,k^2$ |
| `scripts/prep_photo.py` | détourage `rembg` + CLAHE + fond blanc |
| `scripts/make_ascii_svg.py` | rampe de densité, animation SMIL ligne par ligne |
| `scripts/fetch_contributions.py` | scrape `github.com/users/<u>/contributions` (sans token) |
| `scripts/render_heatmap_svg.py` | grille 53×7, reveal diagonal CSS, KPIs |

Seule la heatmap est régénérée par le cron quotidien. Le portrait et la carte sont statiques : relance `./build.sh` quand tu changes la photo ou `config.py`, puis commit.

Space Mono est embarquée en base64 (subset aux seuls glyphes utilisés) car un SVG affiché via `<img>` ne peut pas charger de police externe.
