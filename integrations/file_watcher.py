"""File system watcher for monitoring directories."""

import os
import queue
import threading
from pathlib import Path
from typing import List, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from integrations.base import BaseIntegration


class NewFileHandler(FileSystemEventHandler):
    """Handler for new file events."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        """Initialize file handler.

        Args:
            callback: Function to call when new file is detected
        """
        self.callback = callback
        self.processed_files = set()

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation event.

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        file_path = event.src_path
        if file_path in self.processed_files:
            return

        # Wait a moment for file to be fully written
        if os.path.exists(file_path):
            self.processed_files.add(file_path)
            self.callback(file_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification event.

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        file_path = event.src_path
        # Only process if not already processed
        if file_path not in self.processed_files and os.path.exists(file_path):
            self.processed_files.add(file_path)
            self.callback(file_path)


class FileWatcher(BaseIntegration):
    """File system watcher integration."""

    def __init__(self, watch_directories: List[str], callback: Callable[[str], None]) -> None:
        """Initialize file watcher.

        Args:
            watch_directories: List of directories to watch
            callback: Function to call when new file is detected
        """
        super().__init__("FileWatcher")
        self.watch_directories = [Path(d) for d in watch_directories if os.path.exists(d)]
        self.callback = callback
        self.observer: Optional[Observer] = None
        self.handler: Optional[NewFileHandler] = None
        self.file_queue: queue.Queue = queue.Queue()

    def authenticate(self) -> bool:
        """File watcher doesn't require authentication.

        Returns:
            Always True
        """
        return True

    def sync(self) -> Dict[str, Any]:
        """Start watching directories.

        Returns:
            Dictionary with sync results
        """
        if not self.watch_directories:
            return {
                "success": False,
                "error": "No valid watch directories configured",
            }

        try:
            self.handler = NewFileHandler(self._queue_file)
            self.observer = Observer()

            for directory in self.watch_directories:
                self.observer.schedule(self.handler, str(directory), recursive=True)
                print(f"Watching directory: {directory}")

            self.observer.start()
            self.reset_error_count()

            return {
                "success": True,
                "watched_directories": [str(d) for d in self.watch_directories],
            }
        except Exception as e:
            self.handle_error(e)
            return {
                "success": False,
                "error": str(e),
            }

    def _queue_file(self, file_path: str) -> None:
        """Queue file for processing.

        Args:
            file_path: Path to file
        """
        self.file_queue.put(file_path)
        if self.callback:
            self.callback(file_path)

    def stop(self) -> None:
        """Stop watching directories."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def get_queued_files(self) -> List[str]:
        """Get all queued files and clear queue.

        Returns:
            List of file paths
        """
        files = []
        while not self.file_queue.empty():
            try:
                files.append(self.file_queue.get_nowait())
            except queue.Empty:
                break
        return files

