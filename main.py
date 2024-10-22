
import csv
from pynput import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

abbreviations = {}
typed = []
is_replacing = False
is_active = False  
def load_abbreviations(filename):
    global abbreviations
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print("CSV Headers:", reader.fieldnames)
            for row in reader:
                if 'abbreviation' in row and 'replacement' in row:
                    abbrev = row['abbreviation'].strip('"')
                    replacement = row['replacement'].strip('"')
                    abbreviations[abbrev] = replacement
                else:
                    print("Row does not contain expected keys:", row)
            print(abbreviations)
    except Exception as e:
        print(f"Error loading abbreviations: {e}")

class PalFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.pal'):
            global is_active
            is_active = True  

def on_press(key):
    global typed, is_replacing, is_active
    try:
        if is_replacing or not is_active:
            return  
        
        if hasattr(key, 'char') and key.char is not None:
            typed.append(key.char)  
        elif key == keyboard.Key.backspace and typed:
            typed.pop()

        for abbrev, replacement in abbreviations.items():
            if ''.join(typed[-len(abbrev):]) == abbrev:
                is_replacing = True
                for _ in range(len(abbrev)):
                    subprocess.call(['xdotool', 'key', 'BackSpace'])
                subprocess.call(['xdotool', 'type', replacement])
                typed = []  
                is_replacing = False
                break  

    except Exception as e:
        print(f"Error: {e}")

def on_release(key):
    if key == keyboard.Key.esc:
        pass
load_abbreviations('sheet.csv')

path_to_watch = "."  
event_handler = PalFileHandler()
observer = Observer()
observer.schedule(event_handler, path_to_watch, recursive=False)
observer.start()

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except KeyboardInterrupt:
    observer.stop()
finally:
    observer.stop()
    observer.join()
