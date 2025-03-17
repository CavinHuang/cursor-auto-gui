import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable

class FileWatcher:
    def __init__(self, path: str, callback: Callable[[str], None]):
        self.path = path
        self.callback = callback
        self.observer = Observer()
        self.event_handler = FileChangeHandler(callback)

    def start(self):
        """启动文件监听"""
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()

    def stop(self):
        """停止文件监听"""
        self.observer.stop()
        self.observer.join()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        # 过滤非Python文件和缓存文件
        if not event.src_path.endswith('.py') or '__pycache__' in event.src_path:
            return

        # 防止重复触发
        current_time = time.time()
        if event.src_path in self.last_modified:
            if current_time - self.last_modified[event.src_path] < 1:
                return

        self.last_modified[event.src_path] = current_time
        self.callback(event.src_path)