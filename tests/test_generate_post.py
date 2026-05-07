import pytest
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_read_notes_returns_content(tmp_path):
    notes = tmp_path / "notes.md"
    notes.write_text("- learned something cool\n- built a thing")
    from generate_post import read_required_file
    assert read_required_file(notes) == "- learned something cool\n- built a thing"


def test_read_notes_exits_if_missing(tmp_path):
    from generate_post import read_required_file
    with pytest.raises(SystemExit):
        read_required_file(tmp_path / "nonexistent.md")


def test_read_notes_exits_if_empty(tmp_path):
    notes = tmp_path / "notes.md"
    notes.write_text("   \n  ")
    from generate_post import read_required_file
    with pytest.raises(SystemExit):
        read_required_file(notes)


def test_load_past_posts_returns_last_3(tmp_path):
    past = tmp_path / "past_posts"
    past.mkdir()
    for name in ["2026-04-01.txt", "2026-04-08.txt", "2026-04-15.txt", "2026-04-22.txt"]:
        (past / name).write_text(f"post content for {name}")
    from generate_post import load_past_posts
    result = load_past_posts(past)
    assert len(result) == 3
    assert "2026-04-22.txt" in result[0]
    assert "2026-04-15.txt" in result[1]
    assert "2026-04-08.txt" in result[2]


def test_load_past_posts_empty_dir(tmp_path):
    past = tmp_path / "past_posts"
    past.mkdir()
    from generate_post import load_past_posts
    result = load_past_posts(past)
    assert result == []


def test_load_past_posts_missing_dir(tmp_path):
    from generate_post import load_past_posts
    result = load_past_posts(tmp_path / "past_posts")
    assert result == []
