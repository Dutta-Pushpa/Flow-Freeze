# Data dictionary

`transaction_id` identifies a synthetic MFS transfer. `sender_wallet` and `receiver_wallet` are pseudonymous wallet IDs. `amount` is BDT. `channel` is app, USSD, or agent. `is_cashout` marks an agent/cash-out event. Derived features include amount log, sender/receiver velocity, hop count, cash-out flag, and new relationship.
