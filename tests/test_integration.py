from pathlib import Path

from pypatree.__main__ import run

FIXTURES = Path(__file__).parent / "fixtures"


def test_broken_package_skipped(monkeypatch, caplog, capsys) -> None:
    fixture = FIXTURES / "broken_pkg"
    monkeypatch.chdir(fixture)
    monkeypatch.syspath_prepend(str(fixture))
    run()
    assert "broken" not in capsys.readouterr().out
    assert "Skipping" in caplog.text


def test_test_prefixed_skipped_by_default(monkeypatch, capsys) -> None:
    fixture = FIXTURES / "test_prefixed"
    monkeypatch.chdir(fixture)
    monkeypatch.syspath_prepend(str(fixture))
    run(skip_tests=True)
    out = capsys.readouterr().out
    assert "testpkg" not in out
    assert "realpkg" in out


def test_test_prefixed_included_when_requested(monkeypatch, capsys) -> None:
    fixture = FIXTURES / "test_prefixed"
    monkeypatch.chdir(fixture)
    monkeypatch.syspath_prepend(str(fixture))
    run(skip_tests=False)
    out = capsys.readouterr().out
    assert "testpkg" in out
    assert "realpkg" in out
