# Data dictionary (all data is synthetic; see docs/synthetic_assumptions.md)

| column | meaning | computed from |
|---|---|---|
| transaction_id, episode_id | tx id; fraud-episode id (blank for legit) | generator |
| sender_wallet, receiver_wallet, amount_bdt | pseudonymous wallets, BDT | generator |
| sender_velocity / receiver_velocity | outgoing / incoming tx in the previous 60 min | history before tx |
| sender_fan_out_24h / receiver_fan_in_24h | distinct receivers paid / distinct senders collected from in 24h | history before tx |
| new_relationship | first ever sender→receiver transfer | history before tx |
| rapid_forwarding | sender received ≥60% of this amount in the previous 15 min (pass-through) | history before tx |
| amount_vs_sender_avg | amount / sender's mean past amount (prior used for <3 tx) | history before tx |
| account_age_days, receiver_age_days | wallet age at tx time | wallet table |
| device_changed, merchant_flag, cashout_flag, channel, hour | context flags | generator |
| true_fraud | simulation ground truth (used only for impact simulation / diagnostics) | episode |
| is_fraud | observed label = true_fraud with 7% unreported fraud and 0.3% mis-reported legit | label noise |
| next_action | receiver's OBSERVED next move within 30 min: forward / cashout / other | later transactions |
| legit_profile | normal / merchant / unusual / fraud, used only for fairness slices | generator |

Serving defaults (when a field is not supplied): see `ml/features.py::DEFAULTS`. They are documented, not hidden.
