"""Checks for consensus pulling, seeding and revisions. No internet needed."""

from datetime import date

import pandas as pd
import pytest

import agent.consensus as consensus
import agent.estimates as estimates
from agent.periods import fiscal_period, next_period, quarter_end_after
from agent.pipeline import run_on_text
from agent.revise import apply_revisions
from tests.conftest import SAMPLE_TEXT, good_classification, good_extraction


@pytest.fixture
def temp_files(tmp_path, monkeypatch):
    """Point every estimates/consensus file at an empty temporary folder."""
    est, sample_est = tmp_path / "estimates.csv", tmp_path / "sample_estimates.csv"
    cons, sample_cons = tmp_path / "consensus.csv", tmp_path / "sample_consensus.csv"
    est.write_text("ticker,fiscal_year,quarter,metric,estimate,unit,method\n")
    monkeypatch.setattr(estimates, "ESTIMATES_FILE", est)
    monkeypatch.setattr(estimates, "SAMPLE_ESTIMATES_FILE", sample_est)
    monkeypatch.setattr(consensus, "CONSENSUS_FILE", cons)
    monkeypatch.setattr(consensus, "SAMPLE_CONSENSUS_FILE", sample_cons)
    return {"estimates": est, "sample_estimates": sample_est, "consensus": cons}


# ---- fiscal periods -----------------------------------------------------------
def test_december_year_end():
    assert fiscal_period(date(2026, 9, 30), 12) == (2026, 3)
    assert fiscal_period(date(2026, 12, 31), 12) == (2026, 4)


def test_march_year_end():
    assert fiscal_period(date(2026, 6, 30), 3) == (2027, 1)
    assert fiscal_period(date(2026, 12, 31), 3) == (2027, 3)
    assert fiscal_period(date(2027, 3, 31), 3) == (2027, 4)


def test_next_period_and_quarter_end():
    assert next_period(2026, 3) == (2026, 4)
    assert next_period(2026, 4) == (2027, 1)
    assert quarter_end_after(date(2026, 9, 28), 1) == date(2026, 12, 31)


# ---- reading Yahoo's tables (simulated) ---------------------------------------
def yahoo_tables(methodology="gaap"):
    history = pd.DataFrame(
        {"epsEstimate": [1.10, 1.20, 1.30], "epsActual": [1.15, 1.18, 1.42], "methodology": methodology},
        index=pd.to_datetime(["2026-03-31", "2026-06-30", "2026-09-30"]),
    )
    eps = pd.DataFrame(
        {"avg": [1.35, 1.40], "low": [1.28, 1.30], "high": [1.41, 1.50], "numberOfAnalysts": [4, 4],
         "currency": "USD", "methodology": methodology},
        index=["0q", "+1q"],
    )
    revenue = pd.DataFrame(
        {"avg": [158_000_000, 162_500_000], "low": [154e6, 158e6], "high": [161e6, 166e6], "numberOfAnalysts": [4, 3]},
        index=["0q", "+1q"],
    )
    return history, eps, revenue


def test_rows_from_yahoo_places_each_number_in_the_right_quarter():
    rows = consensus.rows_from_yahoo("rm", 12, *yahoo_tables(), "2026-11-19")
    found = {(r["fiscal_year"], r["quarter"], r["metric"], r["kind"]): r["consensus"] for r in rows}
    assert found[(2026, 3, "diluted_eps", "historical")] == 1.30
    assert found[(2026, 4, "diluted_eps", "forward")] == 1.35
    assert found[(2027, 1, "diluted_eps", "forward")] == 1.40
    assert found[(2026, 4, "revenue", "forward")] == 158.0     # converted to millions
    assert found[(2027, 1, "revenue", "forward")] == 162.5
    assert all(r["ticker"] == "RM" for r in rows)


def test_adjusted_eps_is_labelled():
    rows = consensus.rows_from_yahoo("RM", 12, *yahoo_tables("normalized"), "2026-11-19")
    assert {r["basis"] for r in rows if r["metric"] == "diluted_eps"} == {"adjusted"}


def test_no_history_means_no_forward_guess():
    _, eps, revenue = yahoo_tables()
    assert consensus.rows_from_yahoo("RM", 12, pd.DataFrame(), eps, revenue, "2026-11-19") == []


# ---- seeding ------------------------------------------------------------------
def test_seeding_fills_gaps_only(temp_files):
    estimates.append_estimates([{"ticker": "RM", "fiscal_year": 2026, "quarter": 4, "metric": "diluted_eps",
                                 "estimate": 1.50, "method": "Team model"}])
    rows = consensus.rows_from_yahoo("RM", 12, *yahoo_tables(), "2026-11-19")
    added = consensus.seed_estimates(rows)
    added_keys = {(r["fiscal_year"], r["quarter"], r["metric"]) for r in added}
    assert (2026, 4, "diluted_eps") not in added_keys          # team number kept
    assert (2026, 4, "revenue") in added_keys
    assert estimates.load_estimates("RM", 2026, 4) == {"diluted_eps": 1.50, "revenue": 158.0}
    assert "Consensus seed: Yahoo Finance, GAAP EPS" in estimates.load_estimate_rows("RM", 2026, 3)["diluted_eps"]["method"]
    assert consensus.seed_estimates(rows) == []                 # running again adds nothing


def test_pre_report_consensus_beats_a_forward_pull(temp_files):
    consensus.save_consensus(consensus.rows_from_yahoo("RM", 12, *yahoo_tables(), "2026-08-01"))
    late = [{**r, "consensus": 9.99, "kind": "forward", "pulled_at": "2026-11-19"}
            for r in consensus.rows_from_yahoo("RM", 12, *yahoo_tables(), "x") if r["quarter"] == 3]
    consensus.save_consensus(late)
    assert consensus.load_consensus("RM", 2026, 3)["diluted_eps"]["consensus"] == 1.30


# ---- revisions ----------------------------------------------------------------
def _sample_run(fake_claude, temp_files, next_quarter_rows):
    estimates.append_estimates(
        [{"ticker": "SAMPLE", "fiscal_year": 2026, "quarter": 3, "metric": m, "estimate": v, "method": "Team"}
         for m, v in [("revenue", 150.0), ("operating_income", 18.5), ("net_income", 12.5), ("diluted_eps", 1.25)]]
    )
    consensus.save_consensus(next_quarter_rows)
    fake_claude(good_extraction(), good_classification())
    return run_on_text("SAMPLE", "test", SAMPLE_TEXT, "test", save=False)


def test_revision_starts_from_consensus_when_we_have_no_number(fake_claude, temp_files):
    street = [{"pulled_at": "2026-11-01", "ticker": "SAMPLE", "fiscal_year": 2026, "quarter": 4, "period_end": "2026-12-31",
               "metric": "revenue", "consensus": 158.0, "low": None, "high": None, "analysts": 4,
               "unit": "USD millions", "basis": "provider-defined", "kind": "forward", "source": "Test"}]
    result = _sample_run(fake_claude, temp_files, street)
    revenue = next(r for r in result["revisions"] if r["metric"] == "revenue")
    assert (revenue["base"], revenue["change_pct"], revenue["proposed"]) == (158.0, 5.2, 166.2)
    assert revenue["base_source"].startswith("consensus")
    assert next(r for r in result["revisions"] if r["metric"] == "net_income")["base"] is None
    assert next(r for r in result["metrics"] if r["metric"] == "revenue")["consensus"] is None  # no Q3 consensus in this test

    written = apply_revisions(result, {"revenue": 166.2}, "Approve")
    assert len(written) == 1
    assert estimates.load_estimates("SAMPLE", 2026, 4) == {"revenue": 166.2}
    assert "agent suggested +5.2% (R4)" in written[0]["method"]


def test_analyst_override_and_unchanged_numbers(fake_claude, temp_files):
    result = _sample_run(fake_claude, temp_files, [])
    estimates.append_estimates([{"ticker": "SAMPLE", "fiscal_year": 2026, "quarter": 4, "metric": m,
                                 "estimate": v, "method": "Team"} for m, v in [("revenue", 160.0), ("operating_income", 20.0)]])
    from agent.revise import propose_revisions
    result["revisions"] = propose_revisions(result)
    operating = next(r for r in result["revisions"] if r["metric"] == "operating_income")
    assert operating["proposed"] == 20.0                     # HOLD: unchanged
    written = apply_revisions(result, {"revenue": 165.0, "operating_income": 20.0}, "Approve with edits")
    assert [w["metric"] for w in written] == ["revenue"]     # unchanged team number not rewritten
    assert "analyst set 165.0 instead of 168.3" in written[0]["method"]


def test_negative_base_moves_the_right_way(fake_claude, temp_files):
    result = _sample_run(fake_claude, temp_files, [])
    estimates.append_estimates([{"ticker": "SAMPLE", "fiscal_year": 2026, "quarter": 4, "metric": "net_income",
                                 "estimate": -10.0, "method": "Team"}])
    from agent.revise import propose_revisions
    net_income = next(r for r in propose_revisions(result) if r["metric"] == "net_income")
    assert net_income["proposed"] == -9.3  # a beat shrinks the expected loss


def test_seeded_estimate_is_flagged(fake_claude, temp_files):
    estimates.append_estimates([{"ticker": "SAMPLE", "fiscal_year": 2026, "quarter": 3, "metric": "diluted_eps",
                                 "estimate": 1.30, "method": "Consensus seed: Yahoo Finance, ADJUSTED (non-GAAP) EPS"}])
    fake_claude(good_extraction(), good_classification())
    result = run_on_text("SAMPLE", "test", SAMPLE_TEXT, "test", save=False)
    assert any("adjusted (non-GAAP) consensus" in flag for flag in result["flags"])


def test_big_tech_fiscal_years():
    assert fiscal_period(date(2026, 12, 26), 9) == (2027, 1)   # Apple: late-September year end
    assert fiscal_period(date(2026, 9, 30), 6) == (2027, 1)    # Microsoft: June year end
    assert fiscal_period(date(2026, 10, 25), 1) == (2027, 3)   # NVIDIA: late-January year end
