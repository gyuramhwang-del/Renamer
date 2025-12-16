"""Utility to write the names of files inside a directory to a text file.

The module exposes helpers for listing files and a small CLI for convenience.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def list_files(
    source_dir: Path, *, recursive: bool = False, include_hidden: bool = False
) -> List[str]:
    """Return sorted file names inside *source_dir*.

    Args:
        source_dir: The directory to scan for files.
        recursive: When ``True``, include files in all subdirectories.
        include_hidden: When ``True``, include files and subdirectories whose names
            start with ``.``.

    Raises:
        ValueError: If *source_dir* does not exist or is not a directory.
    """

    if not source_dir.exists():
        raise ValueError(f"Source directory '{source_dir}' does not exist.")
    if not source_dir.is_dir():
        raise ValueError(f"Source path '{source_dir}' is not a directory.")

    if recursive:
        entries: Iterable[Path] = (
            path for path in source_dir.rglob("*") if path.is_file()
        )
    else:
        entries = (path for path in source_dir.iterdir() if path.is_file())

    filenames: List[str] = []
    for path in entries:
        relative = path.relative_to(source_dir)
        if not include_hidden and any(part.startswith(".") for part in relative.parts):
            continue
        filenames.append(relative.as_posix())

    return sorted(filenames)


def write_file_list(
    source_dir: Path,
    output_file: Path,
    *,
    recursive: bool = False,
    include_hidden: bool = False,
) -> None:
    """Write the names of files inside *source_dir* to *output_file*.

    The output file is created (with parent directories) if it does not exist and
    is overwritten if it already exists.
    """

    filenames = list_files(source_dir, recursive=recursive, include_hidden=include_hidden)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(filenames), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a text file that lists the names of files in the provided directory."
        )
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Directory whose files will be listed.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("filenames.txt"),
        help="Path of the text file to write (default: filenames.txt).",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Include files in all subdirectories.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and folders (names starting with '.').",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical interface instead of the CLI.",
    )
    return parser


class FileListGUI:
    """Simple GUI for exporting directory file names."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("파일 목록 생성기")
        self.root.geometry("520x260")
        self.root.resizable(False, False)

        self.source_var = tk.StringVar()
        self.output_var = tk.StringVar(value="filenames.txt")
        self.recursive_var = tk.BooleanVar(value=False)
        self.hidden_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="대상 폴더를 선택하고 옵션을 설정하세요.")

        self._build_layout()

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            main,
            text="폴더 내 파일 이름을 텍스트로 저장",
            font=("Helvetica", 14, "bold"),
        )
        title.pack(anchor=tk.W, pady=(0, 12))

        self._add_path_field(
            main,
            label="대상 폴더",
            variable=self.source_var,
            browse_command=self._choose_source,
            is_directory=True,
        )
        self._add_path_field(
            main,
            label="출력 파일",
            variable=self.output_var,
            browse_command=self._choose_output,
            is_directory=False,
        )

        options = ttk.Frame(main)
        options.pack(fill=tk.X, pady=(12, 8))
        ttk.Checkbutton(options, text="하위 폴더 포함", variable=self.recursive_var).pack(
            side=tk.LEFT, padx=(0, 16)
        )
        ttk.Checkbutton(options, text="숨김 파일 포함", variable=self.hidden_var).pack(
            side=tk.LEFT
        )

        action_row = ttk.Frame(main)
        action_row.pack(fill=tk.X, pady=(4, 8))
        ttk.Button(action_row, text="파일 목록 생성", command=self._generate).pack(
            side=tk.RIGHT
        )

        status = ttk.Label(main, textvariable=self.status_var, foreground="#0d6efd")
        status.pack(anchor=tk.W, pady=(8, 0))

    def _add_path_field(
        self,
        parent: ttk.Frame,
        *,
        label: str,
        variable: tk.StringVar,
        browse_command,
        is_directory: bool,
    ) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=4)

        ttk.Label(row, text=label, width=10).pack(side=tk.LEFT)

        entry = ttk.Entry(row, textvariable=variable)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 8))

        button_text = "폴더 선택" if is_directory else "경로 선택"
        ttk.Button(row, text=button_text, command=browse_command).pack(side=tk.RIGHT)

    def _choose_source(self) -> None:
        directory = filedialog.askdirectory(title="대상 폴더 선택")
        if directory:
            self.source_var.set(directory)

    def _choose_output(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="출력 파일 경로",  # type: ignore[arg-type]
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=Path(self.output_var.get()).name or "filenames.txt",
        )
        if file_path:
            self.output_var.set(file_path)

    def _generate(self) -> None:
        source = Path(self.source_var.get()).expanduser()
        output = Path(self.output_var.get()).expanduser()

        if not self.source_var.get().strip():
            messagebox.showwarning("대상 없음", "대상 폴더를 선택하세요.")
            return
        if not self.output_var.get().strip():
            messagebox.showwarning("출력 없음", "출력 파일 경로를 입력하세요.")
            return

        try:
            filenames = list_files(
                source,
                recursive=self.recursive_var.get(),
                include_hidden=self.hidden_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("경로 오류", str(exc))
            self.status_var.set("경로를 다시 확인해주세요.")
            return

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(filenames), encoding="utf-8")

        self.status_var.set(f"총 {len(filenames)}개 파일 이름을 저장했습니다.")
        messagebox.showinfo("완료", f"파일 목록을 저장했습니다:\n{output}")

    def run(self) -> None:
        self.root.mainloop()


def launch_gui() -> None:
    """Start the Tkinter-based graphical interface."""

    app = FileListGUI()
    app.run()


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui or args.source is None:
        launch_gui()
        return 0

    try:
        write_file_list(
            args.source,
            args.output,
            recursive=args.recursive,
            include_hidden=args.include_hidden,
        )
    except ValueError as exc:  # argparse expects SystemExit on errors
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
