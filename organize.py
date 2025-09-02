# organize.py
# Category-based file organizer with dry-run + undo + safe renaming.

import argparse, os, shutil, sys
from datetime import datetime
from pathlib import Path

# ---------- Customize your categories here ----------
CATEGORIES = {
    "images": {"jpg","jpeg","png","gif","webp","bmp","tiff","heic"},
    "docs": {"pdf","doc","docx","txt","md","rtf"},
    "slides": {"ppt","pptx","key"},
    "spreadsheets": {"xls","xlsx","csv","ods"},
    "archives": {"zip","rar","7z","tar","gz"},
    "audio": {"mp3","wav","aac","flac","m4a","ogg"},
    "video": {"mp4","mov","mkv","avi","wmv","webm"},
    "code": {"py","ipynb","js","ts","html","css","java","c","cpp","rs","go","sh","ps1"},
}
OTHER_BUCKET = "other"        # unknown extensions
NOEXT_BUCKET = "no_extension" # files without a dot/extension

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def safe_destination(dst_folder: Path, filename: str) -> Path:
    """If dst/file exists, append ' (2)', ' (3)', ... before the extension."""
    base = Path(filename).stem
    ext = Path(filename).suffix  # includes dot, e.g. ".pdf"
    candidate = dst_folder / filename
    k = 2
    while candidate.exists():
        candidate = dst_folder / f"{base} ({k}){ext}"
        k += 1
    return candidate

def pick_bucket(ext: str) -> str:
    if not ext:
        return NOEXT_BUCKET
    ext = ext.lower().lstrip(".")
    for bucket, exts in CATEGORIES.items():
        if ext in exts:
            return bucket
    return OTHER_BUCKET

def move_file(src: Path, dst: Path, dry_run: bool, log_f):
    if dry_run:
        print(f"[cyan]DRY-RUN[/cyan] would move: {src} -> {dst}")
        return
    ensure_dir(dst.parent)
    shutil.move(str(src), str(dst))
    if log_f:
        log_f.write(f"{src}||{dst}\n")
    print(f"[green]moved[/green]: {src.name} -> {dst.parent.name}/{dst.name}")

def organize(folder: Path, dry_run: bool = False, include_subdirs: bool = False):
    folder = folder.resolve()
    if not folder.is_dir():
        print(f"[red]Not a directory:[/red] {folder}")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = folder / f"_organize_log_{ts}.txt"
    log_f = None if dry_run else open(log_path, "w", encoding="utf-8")

    processed = 0
    iterator = folder.rglob("*") if include_subdirs else folder.iterdir()

    for p in iterator:
        # Skip directories and our own logs
        if p.is_dir():
            continue
        if p.name.startswith("_organize_log_"):
            continue
        # If not recursing, only move files directly under the target folder
        if not include_subdirs and p.parent != folder:
            continue

        ext = p.suffix
        bucket = pick_bucket(ext)
        dst_folder = folder / bucket
        dst = safe_destination(dst_folder, p.name)
        move_file(p, dst, dry_run, log_f)
        processed += 1

    if log_f:
        log_f.close()
        print(f"[bold]log saved:[/bold] {log_path}")
    print(f"[bold]{processed} files processed.[/bold]")

def undo(log_file: Path, dry_run: bool = False):
    if not log_file.exists():
        print(f"[red]Log file not found:[/red] {log_file}")
        sys.exit(1)
    moves = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            src, dst = line.strip().split("||")
            moves.append((Path(src), Path(dst)))

    # Reverse the moves for a clean rollback
    for src, dst in reversed(moves):
        if dst.exists():
            target = safe_destination(src.parent, dst.name) if src.exists() else src
            if dry_run:
                print(f"[cyan]DRY-RUN[/cyan] would undo: {dst} -> {target}")
            else:
                ensure_dir(target.parent)
                shutil.move(str(dst), str(target))
                print(f"[yellow]undid[/yellow]: {dst} -> {target}")
        else:
            print(f"[red]missing[/red]: {dst} (skipping)")

def main():
    ap = argparse.ArgumentParser(description="Organize files into category folders by extension.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Organize files")
    p_run.add_argument("folder", type=Path, help="Folder to organize")
    p_run.add_argument("--dry-run", action="store_true", help="Preview only (no changes)")
    p_run.add_argument("--recurse", action="store_true", help="Include subfolders (preview first!)")

    p_undo = sub.add_parser("undo", help="Undo a previous run using its log file")
    p_undo.add_argument("logfile", type=Path, help="Path to _organize_log_*.txt")
    p_undo.add_argument("--dry-run", action="store_true", help="Preview undo without moving files")

    args = ap.parse_args()

    if args.cmd == "run":
        organize(args.folder, dry_run=args.dry_run, include_subdirs=args.recurse)
    else:
        undo(args.logfile, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
 