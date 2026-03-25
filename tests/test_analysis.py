import numpy as np

from rent_control.analysis import (
    build_baseline_by_decile,
    build_baseline_by_tenure,
    build_baseline_summary,
    build_reform_by_decile,
    build_reform_summary,
    get_published_estimates,
    weighted_mean,
    weighted_sum,
    weighted_sum_bn,
)


def test_weighted_sum():
    assert weighted_sum([10, 20], [1, 3]) == 70.0


def test_weighted_mean():
    assert weighted_mean([10, 20], [1, 3]) == 17.5


def test_weighted_mean_zero_weights():
    assert weighted_mean([10, 20], [0, 0]) == 0.0


def test_weighted_sum_bn():
    assert weighted_sum_bn([1e9, 2e9], [1, 1]) == 3.0


def test_build_baseline_summary():
    # Use large weights to ensure values are significant at bn scale
    rent = np.array([12000.0, 8000.0, 6000.0, 10000.0])
    hb = np.array([5000.0, 3000.0, 0.0, 4000.0])
    uc = np.array([2000.0, 1000.0, 0.0, 1500.0])
    tenure = np.array(
        ["RENT_PRIVATELY", "RENT_FROM_COUNCIL", "OWNER_OCCUPIED", "RENT_FROM_HA"]
    )
    weights = np.array([100000, 100000, 100000, 100000])

    summary = build_baseline_summary(rent, hb, uc, tenure, weights)

    assert summary["n_private_renters"] == 100000
    assert summary["n_social_renters"] == 200000
    assert summary["total_private_rent_bn"] > 0
    assert summary["hb_spending_bn"] > 0
    assert summary["total_housing_benefit_bn"] == round(
        summary["hb_spending_bn"] + summary["uc_housing_spending_bn"], 2
    )


def test_build_baseline_by_tenure():
    rent = np.array([12000, 8000, 10000, 0, 0])
    hb = np.array([5000, 3000, 4000, 0, 0])
    uc = np.array([2000, 1000, 1500, 0, 0])
    tenure = np.array([
        "RENT_PRIVATELY", "RENT_FROM_COUNCIL", "RENT_FROM_HA",
        "OWNED_OUTRIGHT", "OWNED_WITH_MORTGAGE",
    ])
    weights = np.array([1, 1, 1, 1, 1])

    rows = build_baseline_by_tenure(rent, hb, uc, tenure, weights)

    assert len(rows) == 5
    assert rows[0]["tenure"] == "Council"
    assert rows[1]["tenure"] == "Housing Association"
    assert rows[2]["tenure"] == "Private"
    assert rows[3]["tenure"] == "Owned outright"
    assert rows[4]["tenure"] == "Owned with mortgage"
    assert rows[0]["n_households"] == 1
    assert rows[3]["avg_rent"] == 0


def test_build_baseline_by_decile():
    n = 20
    rent = np.full(n, 10000.0)
    hb = np.full(n, 3000.0)
    uc = np.full(n, 1000.0)
    decile = np.array([d for d in range(1, 11) for _ in range(2)])
    weights = np.ones(n)

    rows = build_baseline_by_decile(rent, hb, uc, decile, weights)

    assert len(rows) == 10
    assert rows[0]["decile"] == 1
    assert rows[9]["decile"] == 10


def test_build_reform_summary():
    b_hb = np.array([5000.0, 3000.0])
    b_uc = np.array([2000.0, 1000.0])
    b_inc = np.array([20000.0, 15000.0])
    b_rent = np.array([12000.0, 10000.0])
    r_hb = np.array([4000.0, 2500.0])
    r_uc = np.array([1500.0, 800.0])
    r_inc = np.array([19500.0, 14700.0])
    r_rent = np.array([10800.0, 9000.0])
    target_mask = np.array([True, True])
    weights = np.array([100000.0, 100000.0])

    summary = build_reform_summary(
        b_hb, b_uc, b_inc, b_rent,
        r_hb, r_uc, r_inc, r_rent,
        target_mask, weights,
    )

    # Government saves money (less HB/UC spending)
    assert summary["total_fiscal_bn"] < 0
    assert summary["rent_saved_bn"] > 0
    assert "tenant_net_gain_bn" in summary


def test_build_reform_by_decile():
    b_hb = np.array([5000.0, 3000.0])
    b_uc = np.array([2000.0, 1000.0])
    b_inc = np.array([20000.0, 30000.0])
    b_rent = np.array([12000.0, 10000.0])
    r_hb = np.array([4000.0, 2500.0])
    r_uc = np.array([1500.0, 800.0])
    r_inc = np.array([19500.0, 29700.0])
    r_rent = np.array([10800.0, 9000.0])
    target_mask = np.array([True, True])
    decile = np.array([1, 2])
    weights = np.array([100000.0, 100000.0])

    rows = build_reform_by_decile(
        b_hb, b_uc, b_inc, b_rent,
        r_hb, r_uc, r_inc, r_rent,
        target_mask, decile, weights,
    )

    assert len(rows) == 10
    assert rows[0]["decile"] == 1
    assert rows[0]["rent_saved_mn"] > 0
    # Deciles 3-10 should have zero since no data
    assert rows[5]["rent_saved_mn"] == 0


def test_get_published_estimates():
    lha = get_published_estimates("lha_unfreeze")
    assert len(lha["estimates"]) == 4
    assert lha["estimates"][0]["source"] == "Resolution Foundation"

    unknown = get_published_estimates("nonexistent_policy")
    assert unknown["estimates"] == []
