#!/usr/bin/env bash
# Rebuild all art locally.
#   ./build.sh                 ASCII art = Monte Carlo paths (KIND=paths|candles|vol)
#   ./build.sh photo.jpg       ASCII portrait from a photo
#   DEMO=1 ./build.sh          synthetic contributions (offline preview)
set -euo pipefail
cd "$(dirname "$0")/scripts"
if [[ $# -ge 1 ]]; then python prep_photo.py "../$1" 2>/dev/null || python prep_photo.py "$1"
else python make_ascii_source.py --kind "${KIND:-paths}"; fi
python make_info_card.py          # first: the ASCII panel matches its height
python make_ascii_svg.py
python fetch_contributions.py ${DEMO:+--demo}
python render_heatmap_svg.py
