#!/usr/bin/env python3
"""
Aria2 Download Manager with File Monitoring
Monitors links.txt for changes, automatically downloads using aria2c,
and manages the opening/closing of the links file editor.
"""
import os
import sys
import time
import platform
import subprocess
import shutil
import logging
import threading
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

# --- Defensive imports with helpful error messages ---
try:
    from watchdog.observers import Observer
    from watchdog.observers.api import BaseObserver
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
except ImportError as e:
    print("Missing dependency: watchdog. Install with: pip install watchdog")
    sys.exit(1)

try:
    from colorama import Fore, Style, init
except ImportError:
    print("Missing dependency: colorama. Install with: pip install colorama")
    sys.exit(1)

try:
    import psutil
except ImportError:
    print("Missing dependency: psutil. Install with: pip install psutil")
    sys.exit(1)
# ---------------------------------------------------

# Initialize colorama
init(autoreset=True)

# Configure logging: Set to WARNING to keep the console clean
logging.basicConfig(
    level=logging.WARNING, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_manager.log'),
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration constants using relative paths"""
    LINK_FILE: str = "links.txt"
    DOWNLOAD_DIR: str = "downloads"
    DEBOUNCE_SECONDS: float = 1.0
    
    @property
    def link_file_path(self) -> Path:
        """Get path to links file relative to the current working directory"""
        # Strict relative path for portability
        return Path(self.LINK_FILE)
    
    @property
    def download_dir_path(self) -> Path:
        """Get path to download directory relative to the current working directory"""
        # Strict relative path for portability
        return Path(self.DOWNLOAD_DIR)


class Aria2Manager:
    """Manages aria2c executable discovery and command execution"""
    
    def __init__(self, config: Config):
        self.config = config
        self._executable_path: Optional[Path] = None
        self._download_lock = threading.Lock()
        self._is_downloading = False
    
    def find_executable(self) -> Optional[Path]:
        """Find aria2c executable in system PATH"""
        if self._executable_path:
            return self._executable_path
        
        exe_name = "aria2c.exe" if platform.system() == "Windows" else "aria2c"
        system_path = shutil.which(exe_name)
        
        if system_path:
            self._executable_path = Path(system_path)
            return self._executable_path
        
        print(Fore.RED + f"✗ {exe_name} executable not found in PATH. Install aria2 or place it in a PATH directory.")
        return None
    
    def build_command(self, aria2_exe: Path, input_file: Path) -> List[str]:
        """
        Build minimal aria2c command with arguments
        """
        # Use the relative string names for aria2c
        return [
            str(aria2_exe),
            "--continue=true",
            f"--dir={self.config.DOWNLOAD_DIR}", 
            f"--input-file={self.config.LINK_FILE}", 
        ]
    
    def download_links(self, link_file: Path) -> bool:
        """
        Execute aria2c to download links from file (non-blocking in main thread)
        """
        if self._is_downloading:
            print(Fore.YELLOW + "⚠ Download already in progress, skipping...")
            return False
        
        # Check if file has any non-comment lines
        try:
            with open(link_file, 'r', encoding='utf-8') as f:
                has_links = any(line.strip() and not line.strip().startswith('#') 
                            for line in f)
            if not has_links:
                print(Fore.YELLOW + "⚠ No links found in file (only comments or empty lines)")
                return False
        except Exception as e:
            logger.error(f"Failed to read link file: {e}")
            return False
        
        aria2_exe = self.find_executable()
        if aria2_exe is None:
            return False
        
        cmd = self.build_command(aria2_exe, link_file)
        
        # Start download in a background thread
        thread = threading.Thread(target=self._run_download, args=(cmd,), daemon=True)
        thread.start()
        
        return True
    
    def _run_download(self, cmd: List[str]) -> None:
        """Run aria2c in a separate thread, piping output directly to the console."""
        with self._download_lock:
            self._is_downloading = True
            
        try:
            print(Fore.BLUE + "\n🚀 Starting aria2c download (Output below, press Ctrl+C to stop monitor):")
            
            result = subprocess.run(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
                check=False
            )
            
            returncode = result.returncode
            
            print("\n" + Fore.BLUE + "="*50)
            if returncode == 0:
                print(Fore.GREEN + "✓ Aria2c: All downloads completed successfully.")
            elif returncode == 28:
                print(Fore.YELLOW + "⚠ Aria2c exited with code 28 (I/O Error). Check disk space and folder permissions.")
            else:
                print(Fore.YELLOW + f"⚠ Aria2c exited with code {returncode}. Check the logs above for details.")
            print(Fore.BLUE + "="*50)
                
        except Exception as e:
            print(Fore.RED + f"✗ Unexpected error during download: {e}")
            logger.exception("Unexpected download error")
        finally:
            with self._download_lock:
                self._is_downloading = False
    
    def stop_download(self) -> None:
        """No-op as the application is hands-off."""
        pass


class FileOpener:
    """Handles opening and closing files in platform-specific editors"""
    
    @staticmethod
    def open_file(file_path: Path) -> bool:
        """
        Open file in default system editor (guarantees file creation first)
        """
        # 1. Create file if it doesn't exist
        if not file_path.exists():
            try:
                file_path.write_text("# Add your links here (one per line)\n", encoding="utf-8")
                logger.warning(f"Created new file: {file_path}")
            except OSError as e:
                print(Fore.RED + f"Failed to create {file_path.name}: {e}")
                logger.error(f"File creation failed: {e}")
                return False
        
        print(Fore.BLUE + f"Opening {file_path.name}...")
        
        system = platform.system()
        try:
            if system == "Windows":
                # Use os.startfile on Windows only
                if hasattr(os, 'startfile'):
                    os.startfile(str(file_path))  # type: ignore
                else:
                    subprocess.run(["cmd", "/c", "start", str(file_path)], check=False, creationflags=subprocess.DETACHED_PROCESS) # type: ignore
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)], check=False)
            else:  # Linux / other
                opener = shutil.which("xdg-open")
                if opener:
                    subprocess.run([opener, str(file_path)], check=False)
                else:
                    print(Fore.YELLOW + f"⚠ No xdg-open found. Open manually: {file_path}")
                    return False
            return True
        except Exception as e:
            print(Fore.YELLOW + f"⚠ Failed to open file automatically: {e}")
            print(f"   Open manually: {file_path}")
            logger.error(f"File open failed: {e}")
            return False
    
    @staticmethod
    def close_editor_processes() -> None:
        """
        Best-effort: terminate common GUI text editors
        """
        system = platform.system()
        # Add common text editors for cleanup
        target_editors = {
            "Windows": ["notepad", "wordpad"],
            "Darwin": ["TextEdit", "BBEdit", "Sublime Text", "code"],
            "Linux": ["gedit", "kate", "nano", "vi", "vim"] # Console editors won't typically be killed
        }.get(system, [])
        
        if not target_editors:
            return
        
        closed_count = 0
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                proc_name = proc.info.get("name", "")
                if any(editor.lower() in proc_name.lower() for editor in target_editors):
                    try:
                        proc.terminate()
                        proc.wait(timeout=1)
                        closed_count += 1
                    except psutil.TimeoutExpired:
                        proc.kill()
                    except Exception:
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if closed_count > 0:
            print(Fore.LIGHTRED_EX + f"✓ Closed {closed_count} editor process(es) on exit.")


class LinkFileHandler(FileSystemEventHandler):
    """Monitors link file for modifications and triggers downloads"""
    
    def __init__(self, target_path: Path, aria2_manager: Aria2Manager):
        super().__init__()
        self.target_path = target_path
        self.aria2_manager = aria2_manager
        self._last_modified: float = 0.0
        self._debounce_seconds: float = Config.DEBOUNCE_SECONDS
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events"""
        if event.is_directory:
            return
        
        try:
            event_path = Path(event.src_path)
        except Exception:
            return
        
        if event_path.name != self.target_path.name:
             return
        
        # Debounce
        now = time.time()
        if now - self._last_modified < self._debounce_seconds:
            return
        
        self._last_modified = now
        
        print(Fore.CYAN + f"\n{'='*50}")
        print(Fore.CYAN + "📝 Detected changes in links.txt. Launching aria2c...")
        print(Fore.CYAN + f"{'='*50}")
        
        self.aria2_manager.download_links(self.target_path)


class DownloadManager:
    """Main application class"""
    
    def __init__(self):
        self.config = Config()
        self.aria2_manager = Aria2Manager(self.config)
        self.file_opener = FileOpener() # Reinstated
        self.observer: Optional[BaseObserver] = None
    
    def run(self) -> int:
        """Main entry point for the download manager"""
        print(Fore.MAGENTA + Style.BRIGHT + "╔════════════════════════════════════════╗")
        print(Fore.MAGENTA + Style.BRIGHT + "║   Aria2 Watcher & Launcher             ║")
        print(Fore.MAGENTA + Style.BRIGHT + f"║   Monitoring: {self.config.LINK_FILE:<27}║")
        print(Fore.MAGENTA + Style.BRIGHT + "╚════════════════════════════════════════╝\n")
        
        link_file_path = self.config.link_file_path
        download_dir_path = self.config.download_dir_path
        
        # 1. Create Downloads Directory
        try:
            download_dir_path.mkdir(parents=True, exist_ok=True)
            print(Fore.YELLOW + f"⚠ Verified download directory: {download_dir_path.name}")
        except OSError as e:
            print(Fore.RED + f"✗ Failed to create download directory {download_dir_path.name}: {e}")
            return 1
        
        # 2. Open/Create links.txt (this guarantees creation)
        if not self.file_opener.open_file(link_file_path):
             print(Fore.RED + "✗ Critical error: Cannot open/create links.txt. Exiting.")
             return 1
        
        # 3. Initial Download Attempt (checks content)
        self.aria2_manager.download_links(link_file_path)
        
        # 4. Set up file monitoring
        try:
            event_handler = LinkFileHandler(
                link_file_path,
                self.aria2_manager
            )
            
            observer = Observer()
            self.observer = observer
            watch_dir = Path.cwd()
            observer.schedule(event_handler, path=str(watch_dir), recursive=False)
            observer.start()
            
            print(Fore.GREEN + f"\n✓ Monitoring {self.config.LINK_FILE} for changes...")
            print(Fore.YELLOW + "  Press Ctrl+C to stop the monitor (This will also close the text editor).\n")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
            
        except KeyboardInterrupt:
            print(Fore.LIGHTRED_EX + "\n\n⏹ Stopping download monitor...")
            return 0
        
        except Exception as e:
            print(Fore.RED + f"✗ Failed to start file monitoring: {e}")
            logger.exception("Failed to start observer")
            return 1
        
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up resources: observer and editor processes"""
        if self.observer is not None:
            try:
                self.observer.stop()
                self.observer.join(timeout=3)
            except Exception:
                pass
        
        # --- CRITICAL FIX 3: Close the editor on exit ---
        self.file_opener.close_editor_processes()
        
        print(Fore.GREEN + "✓ Cleanup complete. Goodbye!")


def main() -> int:
    """Entry point"""
    try:
        manager = DownloadManager()
        return manager.run()
    except Exception as e:
        print(Fore.RED + f"✗ Fatal error: {e}")
        logger.exception("Fatal error in main")
        return 1


if __name__ == "__main__":
    sys.exit(main())