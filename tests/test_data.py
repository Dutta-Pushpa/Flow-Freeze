import pandas as pd
from data_generator.generate_transactions import generate_transactions, generate_dataset

def test_synthetic_data_is_reproducible():
    assert generate_transactions(300).equals(generate_transactions(300))

def test_fraud_and_legit_overlap_not_separable_by_one_feature():
    df = generate_transactions(6000); f = df[df.true_fraud == 1]; l = df[df.true_fraud == 0]
    assert 0.02 < df.true_fraud.mean() < 0.12
    assert (f.amount_vs_sender_avg < 1.8).mean() > 0.10          # stealth fraud exists
    assert (l.amount_vs_sender_avg > 2.5).mean() > 0.01          # legitimate look-alikes exist
    assert df.is_fraud.ne(df.true_fraud).sum() > 0                # label noise exists

def test_features_are_causal_and_next_action_is_observed():
    df, wallets, eps = generate_dataset(3000)
    assert df.ts_min.is_monotonic_increasing and set(df.next_action) <= {"forward", "cashout", "other"}
    assert df.hour.between(0, 23).all() and len(wallets) == 800 and len(eps) > 0
