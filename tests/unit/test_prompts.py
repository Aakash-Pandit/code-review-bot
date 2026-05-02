from application.app import build_review_prompt


def test_build_review_prompt_full_mode():
    prompt = build_review_prompt("x = 1", None, "full")
    assert "bugs and logic errors" in prompt
    assert "security vulnerabilities" in prompt
    assert "performance problems" in prompt


def test_build_review_prompt_security_mode():
    prompt = build_review_prompt("x = 1", None, "security")
    assert "security vulnerabilities only" in prompt


def test_build_review_prompt_performance_mode():
    prompt = build_review_prompt("x = 1", None, "performance")
    assert "performance problems only" in prompt


def test_build_review_prompt_explain_mode():
    prompt = build_review_prompt("x = 1", None, "explain")
    assert "Explain what this code does" in prompt


def test_build_review_prompt_with_language():
    prompt = build_review_prompt("x = 1", "Python", "full")
    assert "The code is written in Python" in prompt


def test_build_review_prompt_without_language():
    prompt = build_review_prompt("x = 1", None, "full")
    assert "The code is written in" not in prompt


def test_build_review_prompt_unknown_mode_defaults_to_full():
    prompt = build_review_prompt("x = 1", None, "nonexistent")
    assert "bugs and logic errors" in prompt


def test_build_review_prompt_none_mode_defaults_to_full():
    prompt = build_review_prompt("x = 1", None, None)
    assert "bugs and logic errors" in prompt


def test_build_review_prompt_code_in_backtick_block():
    code = "def foo(): pass"
    prompt = build_review_prompt(code, None, "full")
    assert f"```\n{code}\n```" in prompt
