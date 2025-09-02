# File Organizer CLI 📂

A Python command-line tool that automatically organizes files into category-based folders (e.g., docs, images, code, audio, video).  
Supports **dry-run previews**, **undo functionality**, and **collision-safe renaming** to ensure reliable and repeatable runs.

---

## 🚀 Features
- Categorizes files into subfolders based on extension (e.g., `.pdf` → `docs`, `.jpg` → `images`, `.py` → `code`)
- **Dry-run mode** to preview actions without making changes
- **Undo support** via manifest logs to restore files to their original locations
- **Collision-safe renaming** (no accidental overwrites — duplicates renamed automatically)
- Clear, colored terminal summaries with [Rich](https://github.com/Textualize/rich)
- Processes **100+ files in under 1 second**

---

## ⚙️ Setup
Clone the repo:
```bash
git clone https://github.com/<your-username>/file-organizer-cli.git
cd file-organizer-cli
