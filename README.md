
# Adolf

A Python script that uses `aria2c` to download files from a list of links stored in `links.txt`.  
The script monitors `links.txt` for changes and automatically triggers downloads when updated.  
It supports **Windows, macOS, and Linux**.

---

## 🚀 Features

- 📂 **Automated Downloads**: Automatically downloads files listed in `links.txt` using `aria2c`.
- 🔄 **Live Monitoring**: Watches `links.txt` for changes and triggers downloads when updated.
- ✍️ **Easy Editing**: Opens `links.txt` in your system’s default text editor.
- 🎨 **Enhanced Readability**: Includes colored logs for better clarity.
- 🛠️ **Cross-Platform Support**: Works on **Windows, macOS, and Linux** (handles differences automatically).
- 🔍 **PATH Fallback**: If a local `aria2c` binary is missing, the script will look for `aria2c` installed in your system’s PATH.

---

## 📌 Requirements

- Python **3.7** or higher
- `aria2c` binary:
  - **Windows**: Place `aria2c.exe` in the script folder or install globally.
  - **macOS/Linux**: Install via system package manager (`brew install aria2` or `sudo apt install aria2`) or place `aria2c` next to the script.
- Python libraries:
  - `watchdog`
  - `colorama`
  - `psutil`

Install the required libraries using:

```bash
pip install watchdog colorama psutil
````

---

## 📖 Usage

### 1️⃣ Prepare the `links.txt` File

* The script will create a `links.txt` file if it doesn’t exist.
* Add your download links to the file, **one per line**.

### 2️⃣ Run the Script

Run the script using Python:

```bash
python script.py
```

* On **Windows**, the file opens in **Notepad**.
* On **macOS**, the file opens in **TextEdit**.
* On **Linux**, it uses your system’s default editor via `xdg-open`.

Whenever you add or modify links and save the file, the script will automatically start downloading.

### 3️⃣ Stop the Script

* Press **Ctrl + C** in the terminal to stop the script.
* The script will try to close the editor automatically:

  * Closes **Notepad** on Windows.
  * Closes **TextEdit** on macOS.
  * Skips auto-close on Linux (you can close it manually).

---

## 🛠️ Compiling into a Single Executable

You can compile the script into a standalone executable with PyInstaller.

### 📥 Download or Install `aria2c`

* **Windows**: Download the `aria2c.exe` binary and place it in the same folder as the script.
* **macOS/Linux**: Install via Homebrew or APT (`brew install aria2`, `sudo apt install aria2`).

  * Alternatively, place a local `aria2c` binary in the script folder.

### 🔧 Install PyInstaller

```bash
pip install pyinstaller
```

### 🏗️ Compile the Script

Run:

```bash
# Windows
pyinstaller --onefile --add-binary "aria2c.exe;." script.py

# macOS/Linux (if bundling local aria2c)
pyinstaller --onefile --add-binary "aria2c:." script.py
```

* The executable will be available in the `dist/` folder.
* If you didn’t bundle `aria2c`, make sure it’s available in your PATH.

### 🚀 Run the Executable

```bash
./dist/script   # macOS/Linux
dist\script.exe # Windows
```

---

## ⚡ Changes from Original Windows-Only Script

* ✅ Replaced `os.startfile` (Windows-only) with cross-platform open:

  * `open` (macOS)
  * `xdg-open` (Linux)
  * `os.startfile` (Windows)
* ✅ Added **PATH fallback** for `aria2c` if not bundled.
* ✅ Added **macOS TextEdit support** for auto-closing.
* ✅ Hardened watchdog monitoring with absolute path matching & debounce.
* ✅ Clean error messages if dependencies (`watchdog`, `colorama`, `psutil`) are missing.

---

✅ Now you’re ready to automate your downloads with **Adolf** on any OS!

```

---

Do you also want me to add a **step-by-step guide for installing aria2c on macOS/Linux** (brew/apt/yum) inside the README, or keep it short like this?
```
