from pathlib import Path

import pytest

import renamer


def create_files(base: Path, structure: dict[str, str | dict]):
    """Recursively create files from a mapping for testing."""
    base.mkdir(parents=True, exist_ok=True)
    for name, content in structure.items():
        path = base / name
        if isinstance(content, dict):
            path.mkdir()
            create_files(path, content)
        else:
            path.write_text(content)


def test_list_files_non_recursive(tmp_path: Path):
    create_files(
        tmp_path,
        {
            "a.txt": "A",
            "b.md": "B",
            "nested": {
                "c.txt": "C",
            },
        },
    )

    assert renamer.list_files(tmp_path) == ["a.txt", "b.md"]


def test_list_files_recursive(tmp_path: Path):
    create_files(
        tmp_path,
        {
            "a.txt": "A",
            "nested": {
                "b.md": "B",
                "deep": {"c.log": "C"},
            },
        },
    )

    assert renamer.list_files(tmp_path, recursive=True) == [
        "a.txt",
        "nested/b.md",
        "nested/deep/c.log",
    ]


def test_excludes_hidden_by_default(tmp_path: Path):
    create_files(
        tmp_path,
        {
            ".hidden.txt": "H",
            "visible.txt": "V",
            ".folder": {"inside.txt": "I"},
            "folder": {".hidden2": "H2", "ok.txt": "O"},
        },
    )

    assert renamer.list_files(tmp_path, recursive=True) == ["folder/ok.txt", "visible.txt"]


def test_include_hidden_when_requested(tmp_path: Path):
    create_files(tmp_path, {".hidden.txt": "H"})

    assert renamer.list_files(tmp_path, include_hidden=True) == [".hidden.txt"]


def test_invalid_directory_raises(tmp_path: Path):
    missing_dir = tmp_path / "nope"
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")

    with pytest.raises(ValueError):
        renamer.list_files(missing_dir)
    with pytest.raises(ValueError):
        renamer.list_files(file_path)


def test_write_file_list_creates_output(tmp_path: Path):
    create_files(tmp_path / "src", {"a.txt": "A", "b.txt": "B"})
    output = tmp_path / "out" / "names.txt"

    renamer.write_file_list(tmp_path / "src", output)

    assert output.exists()
    assert output.read_text().splitlines() == ["a.txt", "b.txt"]
