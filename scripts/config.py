"""Single source of truth for everything personal in the profile art."""

# ── GitHub ────────────────────────────────────────────────────────────────
USERNAME = "jeanphilippecedricndri-sudo"  # the repo must be named exactly like this
PROMPT_USER = "jp"
PROMPT_HOST = "quant"

# ── Theme (dark terminal, GitHub dark background) ─────────────────────────
BG = "#0d1117"
PANEL = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
DIM = "#8b949e"
ACCENT = "#7ee787"   # neofetch keys, prompt
ACCENT2 = "#79c0ff"  # title / highlights
ASCII_FG = "#d0d7de"

# none -> brightest, level 5 is a neon top end (only reached by outlier days)
HEAT_PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

FONT_STACK = "'Space Mono', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# ── neofetch card ─────────────────────────────────────────────────────────
CARD_TITLE = f"{PROMPT_USER}@{PROMPT_HOST}"
CARD_ROWS = [
    ("Name", "Jean Philippe Cedric N'DRI"),
    ("Role", "Quantitative Analyst"),
    ("Also", "Data Scientist"),
    ("Base", "Paris, FR"),
    ("", ""),
    ("Prev", "LBP AM · Quant Analyst"),
    ("", "SG CIB QIS · Quant Researcher"),
    ("", "BPCE · Data Scientist"),
    ("Edu", "École Polytechnique · MSc Fin. Eng."),
    ("", "NEOMA · MSc Finance & Big Data"),
    ("", ""),
    ("Stack", "Python · pandas · scikit-learn · LangGraph"),
    ("", "React · Flask · LaTeX"),
    ("Focus", "quant strategies · portfolio management"),
    ("", "factor investing · option pricing"),
    ("", "agentic AI research"),
]
