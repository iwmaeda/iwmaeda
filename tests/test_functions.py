from iwmaeda.functions import hello


def test_hello_returns_greeting() -> None:
    result = hello("World")
    assert result == "Hello, World!"
