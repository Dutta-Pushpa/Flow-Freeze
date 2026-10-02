from data_generator.generate_transactions import generate_transactions
def test_synthetic_data_is_reproducible():
    assert generate_transactions(5).equals(generate_transactions(5))
