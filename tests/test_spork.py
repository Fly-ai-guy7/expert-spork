import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import spork  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_store(tmp_path, monkeypatch):
    monkeypatch.setenv("SPORK_FILE", str(tmp_path / "spork.json"))
    yield


def test_add_assigns_sequential_ids():
    assert spork.add("first") == 1
    assert spork.add("second") == 2
    assert spork.add("third") == 3


def test_list_returns_empty_when_no_tasks():
    assert spork.list_tasks() == []


def test_mark_done_sets_flag_and_returns_true():
    spork.add("task")
    assert spork.mark_done(1) is True
    assert spork.list_tasks()[0]["done"] is True


def test_mark_done_missing_id_returns_false():
    assert spork.mark_done(42) is False


def test_remove_drops_task():
    spork.add("to remove")
    assert spork.remove(1) is True
    assert spork.list_tasks() == []


def test_remove_missing_id_returns_false():
    assert spork.remove(42) is False


def test_clear_done_removes_only_completed():
    spork.add("keep")
    spork.add("complete")
    spork.mark_done(2)
    assert spork.clear_done() == 1
    tasks = spork.list_tasks()
    assert [t["text"] for t in tasks] == ["keep"]


def test_list_sorts_by_priority_then_id():
    spork.add("medium-1")
    spork.add("low-1", priority="low")
    spork.add("high-1", priority="high")
    spork.add("medium-2")
    spork.add("high-2", priority="high")
    order = [t["text"] for t in spork.list_tasks()]
    assert order == ["high-1", "high-2", "medium-1", "medium-2", "low-1"]


def test_add_rejects_unknown_priority():
    with pytest.raises(ValueError):
        spork.add("bad", priority="urgent")


def test_cli_add_and_list(tmp_path, monkeypatch):
    env = {"SPORK_FILE": str(tmp_path / "cli.json"), "PATH": "/usr/bin:/bin"}
    script = str(Path(__file__).resolve().parents[1] / "spork.py")
    subprocess.run([sys.executable, script, "add", "buy", "milk"], env=env, check=True)
    result = subprocess.run(
        [sys.executable, script, "list"], env=env, capture_output=True, text=True, check=True
    )
    assert "buy milk" in result.stdout
