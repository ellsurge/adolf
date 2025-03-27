import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, Style, init
import psutil
import sys

# Initialize colorama
init(autoreset=True)

LINK_FILE = 'links.txt'

if getattr(sys, 'frozen', False):
    # If running as a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # If running as a script
    base_path = os.getcwd()

ARIA2_COMMAND = [
    os.path.join(base_path, 'aria2c.exe'),
    '--max-connection-per-server=16',
    '--split=16',
    '--continue=true',
    '--max-download-limit=0',
    '--dir=downloads',
]

def download_links():
    if os.path.exists(LINK_FILE):
        try:
            result = subprocess.run(ARIA2_COMMAND + ['--input-file=' + LINK_FILE], check=True)
            if result.returncode == 0:
                print(Fore.GREEN + "All downloads completed successfully.")
            else:
                print(Fore.YELLOW + "Some downloads may have failed. Check aria2c logs for details.")
        except subprocess.CalledProcessError as e:
            print(Fore.YELLOW + f"Error downloading some links. Check aria2c logs for details.")
    else:
        print(Fore.RED + f'{LINK_FILE} does not exist. Please create it and add links.')

def open_links_file():
    if not os.path.exists(LINK_FILE):
        with open(LINK_FILE, 'w', encoding='utf-8') as f:
            f.write('# Add your links here\n')
    print(Fore.BLUE + f"Opening {LINK_FILE}...")
    os.startfile(LINK_FILE)

def close_links_file():
    """Close the links.txt file if it is open in Notepad."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'notepad' in proc.info['name'].lower():
                proc.terminate()
                print(Fore.LIGHTRED_EX + "Closed links.txt.")
        except psutil.NoSuchProcess:
            continue

class LinkFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(LINK_FILE):
            print(Fore.CYAN + 'Detected changes in links.txt, downloading new links...')
            download_links()

def main():
    open_links_file()
    event_handler = LinkFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.getcwd(), recursive=False)
    observer.start()

    print(Fore.MAGENTA + "Monitoring links.txt for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.LIGHTRED_EX + "Stopping the observer...")
        observer.stop()
        close_links_file()
    observer.join()

if __name__ == '__main__':
    main()
