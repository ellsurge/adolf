# Adolf

A Python script that uses `aria2c` to download files from a list of links stored in `links.txt`. The script monitors `links.txt` for changes and automatically triggers downloads when updated. It also ensures that `links.txt` is closed when the script is terminated.

---

## 🚀 Features

- 📂 **Automated Downloads**: Automatically downloads files listed in `links.txt` using `aria2c`.
- 🔄 **Live Monitoring**: Watches `links.txt` for changes and triggers downloads when updated.
- ✍️ **Easy Editing**: Opens `links.txt` for editing and ensures it is closed when the script exits.
- 🎨 **Enhanced Readability**: Includes colored logs for better clarity.
- 🛠️ **Standalone Executable**: Can be compiled into a single executable with `aria2c` bundled.

---

## 📌 Requirements

- Python **3.7** or higher
- `aria2c` binary
- Python libraries:
  - `watchdog`
  - `colorama`
  - `psutil`

Install the required libraries using:

```bash
pip install watchdog colorama psutil
```

---

## 📖 Usage

### 1️⃣ Prepare the `links.txt` File

- The script will create a `links.txt` file if it doesn’t exist.
- Add your download links to the file, **one per line**.

### 2️⃣ Run the Script

Run the script using Python:

```bash
python script.py
```

- The script will open `links.txt` in your default text editor (e.g., Notepad on Windows).
- Add or modify links in `links.txt`, save the file, and the script will automatically start downloading the files.

### 3️⃣ Stop the Script

- Press **Ctrl + C** in the terminal to stop the script.
- The script will **automatically close** `links.txt` if it is open in Notepad.

---

## 🛠️ Compiling into a Single Executable

To compile the script into a single executable with `aria2c` bundled:

### 📥 Download `aria2c`

- Download the `aria2c` binary for your platform from the [official aria2 releases](https://github.com/aria2/aria2/releases).
- Place `aria2c.exe` in the same directory as `script.py`.

### 🔧 Install PyInstaller

Install PyInstaller using pip:

```bash
pip install pyinstaller
```

### 🏗️ Compile the Script

Run the following command to create a single executable:

```bash
pyinstaller --onefile --add-binary "aria2c.exe;." script.py
```

- This will create an executable in the `dist` folder.

### 🚀 Run the Executable

- Move the executable to your desired location and run it.
- The executable will work **without requiring Python or `aria2c` to be installed separately**.

---

✅ **Now you're ready to automate your downloads efficiently with `Adolf`!**
