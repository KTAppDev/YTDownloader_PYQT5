from moviepy.editor import *
from sys import platform
from pathlib import Path
import re

from mutagen.easyid3 import EasyID3


def set_id3_tag(file_path, title=None, artist=None, albumartist=None, album=None, genre=None, bpm=None, date=None,
                mood=None):
    tags = EasyID3(file_path)
    if title:
        tags['title'] = title
    if artist:
        tags['artist'] = artist
    if albumartist:
        tags['albumartist'] = albumartist
    if album:
        tags['album'] = album
    if genre:
        tags['genre'] = genre
    if bpm:
        tags['bpm'] = bpm
    if date:
        tags['date'] = date
    if mood:
        tags['mood'] = mood

    tags.save()


def convert_rename_add_tags(mp4_path, tags=None):
    remove_from_filename = [' [Audio HD]',
                            ' (Radio Mix)',
                            ' (Official Video)',
                            ' (lyrics)',
                            ' (Radio Edit)',
                            ' [High Quality]',
                            ' (Official Music Video)',
                            ' [Official Music Video]',
                            ' (OFFICIAL MUSIC VIDEO)',
                            ' (Audio)',
                            ' (Audio )',
                            ' (Promo Radio Edit)',
                            ' (Video Official)',
                            ' (Official HD Video)',
                            ' [Clean version]',
                            ' [clean]',
                            ' (Clean)',
                            ' (High Quality)',
                            ' (Official Lyric Video)',
                            ' (Lyric Video)',
                            ' [Official Video]',
                            ' (Clean Radio Edit)',
                            ' (Official lyrics video)',
                            ' (Official Audio)',
                            ' (Clean - Lyrics)',
                            ' (BEST Clean Version)',
                            ' (Lyric Video)',
                            ' (clean version)',
                            ' [visualizer]',
                            ' (Official Visualizer)',
                            ' (visualizer)',
                            ' [Official Visualizer]',
                            ' [Official HD Video]',
                            ' [Music Video]',
                            ' (Music Video)',
                            ' [music video]',
                            ' (music video)',
                            ' (BEST Clean Version)']
    mp4_file = mp4_path
    print(mp4_file)
    mp3_file = f'{mp4_path[:-4]}.mp3'
    print(mp3_file)
    for txt in remove_from_filename:  # This rename code is beastly
        if txt.lower() in mp3_file.lower():
            print('Found ' + txt)
            start = mp3_file.lower().find(txt.lower())
            stop = len(txt)
            mp3_file = mp3_file[0: start:] + mp3_file[start + stop:]
            print('new mp3 file name - ' + mp3_file)
    try:
        print('Reading this mp4 file - ' + mp4_file)
        videoclip = AudioFileClip(mp4_file)
        print('Writing to this mp3 file - ' + mp3_file)
        videoclip.write_audiofile(mp3_file)
        videoclip.close()
        print('Removing this mp4 file - ' + mp4_file)
        os.remove(mp4_path)
    except Exception as e:
        print(str(e) + '-This is from the convert function')
    if tags:
        try:
            set_id3_tag(file_path=mp3_file,
                        title=tags[1],
                        artist=tags[0],
                        bpm=tags[7],
                        date=tags[4],
                        genre=tags[3])
        except Exception as e:
            print(e)
    return 'Convert complete!'


def read_urls_from_search_box(search_box_contents):
    REXP2 = r'(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?'

    list_of_urls = []
    try:
        url = re.findall(REXP2, search_box_contents)
        # print(url)
        if not url:  # check if the current list is empty. this is insane to me right now lol, compared to how i was gonna check
            return []
        else:
            for vid_code in url:
                list_of_urls.append(f'https://www.youtube.com/watch?v={vid_code}')
    except Exception as e:
        print(e)
    return list_of_urls


def resource_path(
        relative_path):  # This function gets the absolute pathe of what ever you feed it, just so there is no location issue
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def ensure_dir_exist(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_os_downloads_folder():
    if platform == "linux" or platform == "linux2":
        return str(os.path.join(Path.home(), "Downloads"))
    elif platform == "darwin":
        return str(os.path.join(Path.home(), "Downloads"))
    elif platform == "win32":
        return str(os.path.expanduser("~\\Downloads"))
    else:
        print('err')


def get_songs_from_text(txt):
    with open(txt) as fp:
        Lines = fp.readlines()
        return Lines


if __name__ == "__main__":
    pass
