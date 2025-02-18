# WITHOUT GUI
import os
import shutil
import time
import logging
import colorlog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()

# Directories
source_dir = os.getenv('SOURCE_DIR')
dest_dir_sfx = os.getenv('DEST_DIR_SFX')
dest_dir_music = os.getenv('DEST_DIR_MUSIC')
dest_dir_video = os.getenv('DEST_DIR_VIDEO')
dest_dir_image = os.getenv('DEST_DIR_IMAGE')
dest_dir_documents = os.getenv('DEST_DIR_DOCUMENTS')

os.makedirs(dest_dir_sfx, exist_ok=True)
os.makedirs(dest_dir_music, exist_ok=True)
os.makedirs(dest_dir_video, exist_ok=True)
os.makedirs(dest_dir_image, exist_ok=True)
os.makedirs(dest_dir_documents, exist_ok=True)


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

# Configure colored logging using colorlog

log_colors={
        'DEBUG': 'bold_green',        # Debug logs in green
        'INFO': 'blue',          # Info logs in blue
        'WARNING': 'yellow',     # Warning logs in yellow
        'ERROR': 'red',          # Error logs in red
        'CRITICAL': 'bold_red',  # Critical logs in bold red
    }


log_format = "%(asctime)s - %(log_color)s%(message)s"
log_handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(log_format, log_colors=log_colors)
log_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

def makeUnique(path):
    """Ensure unique filename if file already exists"""
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{filename} ({counter}){extension}"
        counter += 1
    logger.info(f"Created unique path: {path}")
    return path

def is_file_complete(file_path):
    """Check if the file is still downloading by comparing its size over time"""
    initial_size = os.path.getsize(file_path)
    time.sleep(2)  
    final_size = os.path.getsize(file_path)
    if initial_size == final_size:
        logger.debug(f"File completed downloading: {file_path}")
        return True
    else:
        logger.error(f"File still downloading: {file_path}")
        return False

def move(dest, entry, name):
    """Move file to the destination folder"""
    new_path = os.path.join(dest, name)
    if os.path.exists(new_path):
        logger.info(f"already a file name {name}")
        new_path = makeUnique(new_path)

    try:
        shutil.move(entry.path, new_path)
    except shutil.Error as e:
        logger.error(f"Error moving file {entry.name}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error moving file {entry.name}: {e}")

class MoverHandler(FileSystemEventHandler):
    def check_audio_files(self, entry, name):  # * Checks all Audio Files
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 2_000_000 or "SFX" in name:  # ? 2Megabytes
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_music
                move(dest, entry, name)
                logging.info(f"Moved audio file: {name}")
    
    def check_video_files(self, entry, name):  # * Checks all Video Files
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move(dest_dir_video, entry, name)
                logging.debug(f"Moved video file: {name}")

    def check_image_files(self, entry, name):  # * Checks all Image Files
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                move(dest_dir_image, entry, name)
                logging.debug(f"Moved image file: {name}")

    def check_document_files(self, entry, name):  # * Checks all Document Files
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                move(dest_dir_documents, entry, name)
                logging.debug(f"Moved document file: {name}")
    

    def on_modified(self, event):
        """Triggered when files are modified"""
        time.sleep(1)  # Delay to prevent moving incomplete files
        logger.warning("Directory modified, checking files...")
        
        with os.scandir(source_dir) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue  # Skip folders
                
                name = entry.name
                dest = None
                self.check_audio_files(entry, name)
                self.check_document_files(entry, name)
                self.check_image_files(entry, name)
                self.check_video_files(entry, name)

if __name__ == "__main__":
    observer = Observer()
    event_handler = MoverHandler()
    observer.schedule(event_handler, source_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
