from src.tools import calculator, get_time


def test_calculator_ok():
    assert "7.0" in calculator("1+2*3") or "7" in calculator("1+2*3")


def test_calculator_bad_input():
    out = calculator("__import__('os').system('ls')")
    assert "错误" in out


def test_get_time_format():
    t = get_time()
    assert len(t) >= 10
    assert "-" in t
