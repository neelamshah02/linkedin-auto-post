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


def test_build_prompt_injects_notes_and_past_posts():
    from generate_post import build_prompt
    template = "PAST:\n{past_posts}\n\nNOTES:\n{notes}"
    result = build_prompt(template, "- learned X", ["--- 2026-04-22.txt ---\nold post"])
    assert "- learned X" in result
    assert "old post" in result


def test_build_prompt_no_past_posts():
    from generate_post import build_prompt
    template = "PAST:\n{past_posts}\n\nNOTES:\n{notes}"
    result = build_prompt(template, "- learned X", [])
    assert "No past posts yet" in result
    assert "- learned X" in result


def test_build_html_email_contains_post_and_date():
    from generate_post import build_html_email
    html = build_html_email("My post content", "2026-05-07")
    assert "My post content" in html
    assert "2026-05-07" in html
    assert "0077b5" in html


def test_build_html_email_escapes_html_chars():
    from generate_post import build_html_email
    html = build_html_email("<script>alert('xss')</script>", "2026-05-07")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_archive_post_writes_file(tmp_path):
    from generate_post import archive_post
    out = archive_post("My post text", tmp_path / "past_posts", "2026-05-07")
    assert out == tmp_path / "past_posts" / "2026-05-07.txt"
    assert out.read_text() == "My post text"


def test_archive_post_creates_dir_if_missing(tmp_path):
    from generate_post import archive_post
    out = archive_post("My post text", tmp_path / "new_dir", "2026-05-07")
    assert out.exists()
