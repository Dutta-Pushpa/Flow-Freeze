"""Central, documented simulation + policy parameters (every synthetic assumption lives here)."""
SEED = 42
CURRENCY = "BDT"
WALLETS = 800            # synthetic wallet population
TRANSACTIONS = 20_000    # target number of transactions
DAYS = 21                # simulated calendar window
START = "2026-09-10"     # simulation start (Asia/Dhaka)

# --- fraud-episode assumptions -------------------------------------------------
EPISODE_RATE = 0.03      # share of base events that start a fraud episode
STEALTH_ATO = 0.22       # share of account-takeovers that look statistically normal
STEALTH_SCAM = 0.35      # share of scams that look statistically normal (victim sends a normal amount)
LABEL_MISS_RATE = 0.07   # true fraud that was never reported -> labelled 0 (label noise)
LABEL_FALSE_RATE = 0.003 # legitimate tx wrongly labelled fraud (label noise)

# --- modelling / policy --------------------------------------------------------
TARGET_FPR = 0.02              # operating point chosen on the validation window
RISK_THRESHOLD = 0.5           # legacy name; real threshold is learned and stored in the artifact
CASHOUT_HOLD_THRESHOLD = 0.50  # next-move cash-out probability that triggers a partial-hold recommendation
ANALYST_DELAY_MIN = 5          # minutes between alert and an approved hold
HOLD_SAFETY_MARGIN = 0.10      # extra % held on top of the estimated tainted amount
MIN_PER_ALERT = 6              # analyst minutes per alert (assumption, replace with ops time-and-motion data)
HOLD_MAX_HOURS = 24            # a temporary hold auto-expires unless a human extends it
