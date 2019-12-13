import subprocess
import sys
from os import path
from subprocess import check_output
from threading import Thread
import time

from mp3_tagger import MP3File



folder_path = sys.argv[1]
target_path = sys.argv[2]

file_names = check_output(['ls', folder_path]).decode('utf-8')
stripped_file_names = file_names.strip().split('\n')

EXTENSIONS = ['.mp3']

def filter_mp3_files(file_name):
    """
        filter audio format ending with .mp3 only.
        other formats are not supported.
    """
    for ext in EXTENSIONS:
        if file_name.endswith(ext):
            return True
    return False

processed_file_names = list(filter(filter_mp3_files, stripped_file_names))

def time_it(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print("Total time taken : {} to move {} files ".format((end-start), len(processed_file_names)))
    return wrapper


music = {}

def categorize_songs():
    """
        extracts artist, song from ID3TagV2, ID3TagV1.
        creates a dictionary with all the meta data.
    """
    for name in processed_file_names:
        full_path = folder_path + "/" + name
        mp3 = MP3File(full_path)
        
        try:
            tags = mp3.get_tags()   
            
            id3tags = tags.get('ID3TagV2', 'ID3TagV1')
            artist = id3tags.get('artist')
            song = id3tags.get('song')

            song_obj = {'filename': full_path, 'song': song}

            if artist:
                if artist not in music:
                    music[artist] = [ song_obj ]
                else:
                    music[artist].append(song_obj)
            else:
                if 'Untitled' not in music:
                    music['Untitled'] = [song_obj]
                else:
                    music['Untitled'].append(song_obj)
        
        except Exception as e:
            pass

def create_dir(dir_name):
    dir_name = dir_name.replace("\u0000","").replace(" ","_")
    dir_name = target_path + "/" + dir_name
    if not path.exists(dir_name):
        subprocess.run(['mkdir', "{}".format(dir_name)])
    return dir_name

def move_file(source, target):
    subprocess.run(['cp', "{}".format(source), "{}".format(target)])

@time_it
def sort():
    for artist, songs in music.items():
        target_folder = create_dir(artist)
        for song in songs:
            file_path = song['filename']
            move_file(file_path, target_folder)

if __name__ == '__main__':
    """
        Currently supported for mp3 formats only.
    """
    
    if not path.exists(sys.argv[2]):
        subprocess.run(['mkdir', "{}".format(sys.argv[2])])
    categorize_songs()
    t1 = Thread(target=sort)
    t1.start()