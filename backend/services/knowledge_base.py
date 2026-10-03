"""Small typology / policy corpus for retrieval. Replace with upay's real SOPs after controlled validation."""
KB = [
 "Mule pass-through: funds received and forwarded or cashed out within minutes, often through a young or recently re-activated account.",
 "Account takeover: new device or SIM change followed by an unusually large transfer to a recipient never paid before.",
 "Scam payment: customer sends a normal-looking amount voluntarily to a new recipient; the signal is the recipient's behaviour (fan-in, rapid onward movement).",
 "Layering: value hops across several new wallets before reaching an agent cash-out point; trace downstream and estimate tainted share proportionally.",
 "Proportionate action: hold only the estimated tainted amount, not the whole wallet; the remainder is presumed legitimate.",
 "Holds must be time-limited, notify the customer where legally permitted, and offer a re-review/appeal path; a human must approve every hold.",
 "Intermediate wallets may belong to innocent victims or recipients of mistaken transfers; confirm before escalation.",
 "Escalation: suspected cases should follow upay's compliance process and regulator reporting duties (confirm exact obligations with compliance)."]
