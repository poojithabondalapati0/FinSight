from app.guardrails import normalize_ticker, redact_directives


def test_normalize_ticker():
    assert normalize_ticker(" aapl ") == "AAPL"
    assert normalize_ticker("BRK.B") == "BRK.B"
    assert normalize_ticker("NOT A TICKER!!") is None
    assert normalize_ticker("") is None


def test_redact_directives():
    text, hit = redact_directives("Analysts say you should buy now before earnings")
    assert hit and "buy now" not in text.lower()
    assert redact_directives("Valuation looks stretched")[1] is False
