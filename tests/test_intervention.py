from intervention.recommender import recommend
def test_recommendation_requires_human():
    result=recommend(22000,15000,.81,["cash-out path"])
    assert result["requires_human_approval"] is True and result["collateral_estimate"] == 7000
