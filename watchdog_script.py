from os import getenv,makedirs,path, scandir
import shutil
import threading
import time
import logging
from tkinter import messagebox

import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()

# Directories
source_dir = getenv('SOURCE_DIR')
dest_dir_sfx = getenv('DEST_DIR_SFX')
dest_dir_music = getenv('DEST_DIR_MUSIC')
dest_dir_video = getenv('DEST_DIR_VIDEO')
dest_dir_image = getenv('DEST_DIR_IMAGE')
dest_dir_documents = getenv('DEST_DIR_DOCUMENTS')

makedirs(dest_dir_sfx, exist_ok=True)
makedirs(dest_dir_music, exist_ok=True)
makedirs(dest_dir_video, exist_ok=True)
makedirs(dest_dir_image, exist_ok=True)
makedirs(dest_dir_documents, exist_ok=True)


#Configure extentions
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
# ? supported Video types
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
# ? supported Audio types
audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
# ? supported Document types
document_extensions = [".doc", ".docx", ".odt",
                    ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", "txt"]

text_box= None

def create_window():
    # Create a root window
    root = tk.Tk()
    root.title("File Mover")
    root.geometry("500x300")  # Set the window size
    global text_box
    
    # Create a label for instructions
    label = tk.Label(root, text="Welcome to the File Mover! \nClick 'Start' to begin.", font=("Arial", 14))
    label.pack(pady=20)
    
    text_box = tk.Text(root, width=60, height=10, wrap=tk.WORD, font=("Arial", 12))
    text_box.pack(pady=10)
    
    # Start Button
    start_button = tk.Button(root, text="Start", command=start_moving, font=("Arial", 12), width=15)
    start_button.pack(pady=10)

    # Exit Button
    exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12), width=15)
    exit_button.pack(pady=10)

    root.mainloop()








def insert_text( message, color="lime"):
    text_box.tag_configure(color, foreground=color)  # Define color if not already
    text_box.insert(tk.END, message + "\n", color)  # Apply color
    text_box.yview(tk.END)


def makeUnique(path):
    """Ensure unique filename if file already exists"""
    filename, extension = path.splitext(path)
    counter = 1
    while path.exists(path):
        path = f"{filename} ({counter}){extension}"
        counter += 1
    message = f"Created unique path: {path}"
    insert_text(message, color="blue")
    return path

def is_file_complete(file_path):
    """Check if the file is still downloading by comparing its size over time"""
    initial_size = path.getsize(file_path)
    time.sleep(2)  
    final_size = path.getsize(file_path)
    if initial_size == final_size:
        message= f"File completed downloading: {file_path}"
        insert_text(message)
        return True
    else:
        message= f"File still downloading: {file_path}"
        insert_text(message, color="yellow")
        return False

def move(dest, entry, name):
    """Move file to the destination folder"""
    new_path = path.join(dest, name)
    if path.exists(new_path):
        message= f"already a file name {name}"
        insert_text(message, color="yellow")
        
        new_path = makeUnique(new_path)

    try:
        shutil.move(entry.path, new_path)
    except shutil.Error as e:
        message= f"Error moving file {entry.name}: {e}"
        insert_text(message, color="red")
    except Exception as e:
        message=f"Unexpected error moving file {entry.name}: {e}"
        insert_text(message, color="red")

class MoverHandler(FileSystemEventHandler):
    def check_audio_files(self, entry, name):  # * Checks all Audio Files
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 2_000_000 or "SFX" in name:  # ? 2Megabytes
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_music
                move(dest, entry, name)
                message= f"Moved audio file: {name}"
                insert_text(message)
                return True
        return False
                
                
    
    def check_video_files(self, entry, name):  # * Checks all Video Files
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move(dest_dir_video, entry, name)
                message=f"Moved video file: {name}"
                insert_text(message )
                return True
        return False

    def check_image_files(self, entry, name):  # * Checks all Image Files
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                move(dest_dir_image, entry, name)
                message=f"Moved image file: {name}"
                insert_text(message )
                return True
        return False

    def check_document_files(self, entry, name):  # * Checks all Document Files
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                move(dest_dir_documents, entry, name)
                message=f"Moved document file: {name}"
                insert_text(message )
                return True
        return False
    

    def on_modified(self, event):
        """Triggered when files are modified"""
        time.sleep(1)  # Delay to prevent moving incomplete files
        
        
        
        with scandir(source_dir) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue  # Skip folders
                
                
                name = entry.name

                
                if self.check_audio_files(entry, name):
                    continue
                if self.check_document_files(entry, name):
                    continue
                if self.check_image_files(entry, name):
                    continue
                if self.check_video_files(entry, name):
                    continue
            



def start_moving():
    messagebox.showinfo("Started", "The file moving process has started!")
    insert_text("The file moving process has started...\n")
    
    observer = Observer()
    event_handler = MoverHandler()
    observer.schedule(event_handler, source_dir, recursive=True)
    
    def start_observer():
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    
    # Run the observer in a separate thread
    observer_thread = threading.Thread(target=start_observer)
    observer_thread.daemon = True
    observer_thread.start()

if __name__ == "__main__":
    create_window()
    
