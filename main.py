import math
from multiprocessing import freeze_support

freeze_support()
# These unused imports are necessary for moviepy to be imported properly when making exe
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import AudioClip
from moviepy.editor import concatenate_videoclips, concatenate_audioclips, TextClip, CompositeVideoClip
from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
from moviepy.video.fx.gamma_corr import gamma_corr
from moviepy.video.fx.headblur import headblur
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mask_and import mask_and
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.mask_or import mask_or
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.painting import painting
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.scroll import scroll
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.supersample import supersample
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize

from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import PyQt5.QtCore
from pytube import YouTube
from pytube import Search
from pytube import Playlist
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QRadioButton, QFileDialog, \
    QProgressBar, QMessageBox, QTextEdit, QLineEdit
from PyQt5 import uic, QtGui
import os
from sys import platform
import subprocess
import func
import ssl
import csv
from sys import platform as _platform

ssl._create_default_https_context = ssl._create_unverified_context
global_csv_file_path = ''



class Worker2(QObject):  # Second Thread for commit
    finished = pyqtSignal()
    progress_bar_multi = pyqtSignal(int)  # for Progress bar on multi page
    pb_max = pyqtSignal(int)
    progress_multi = pyqtSignal(str)  # for label on multi page
    download_count_label = pyqtSignal(str)  # for label on multi page


    def run(self):
        try:
            global global_csv_file_path

            download_location = mainuiwindow.download_location.text()
            #################### Youtube URL detection and download #####################
            list_of_urls_ = func.read_urls_from_search_box(mainuiwindow.link_multi.toPlainText())
            if list_of_urls_:
                self.pb_max.emit(len(list_of_urls_))
                self.progress_multi.emit(f'Found {len(list_of_urls_)} youtube urls, Downloading...')
                for link in list_of_urls_:
                    down_inf = youtube_single_download(link, download_location)
                    self.progress_multi.emit(f'Downloaded - {down_inf[0]}')
                    self.progress_bar_multi.emit(mainuiwindow.progress_bar_multi.value() + 1)

                self.progress_bar_multi.emit(0)
                self.finished.emit()
                return
            ########## if there isn't any youtube link then its a text list ###########

            ################## youtube SERACH
            songs = mainuiwindow.link_multi.toPlainText().split("\n")
            songs = list(filter(None, songs)) #filter empty
            self.pb_max.emit(len(songs))
            # p = round(100 / len(songs))
            # progress_split = 100 / int(len(songs))
            # progress_split_ = 0
            video_list = []
            for song in songs:
                # Get clenliness on every loop, should be able to hot swap
                if mainuiwindow.select_audio.isChecked():
                    mainuiwindow.radio_button_state = "official audio"
                elif mainuiwindow.select_raw_audio.isChecked():
                    mainuiwindow.radio_button_state = "raw audio"
                elif mainuiwindow.select_clean_audio.isChecked():
                    mainuiwindow.radio_button_state = "clean audio"
                # Get clenliness on every loop, should be able to hot swap


                if song == '':
                    continue
                self.progress_multi.emit(f'Searching for - {song}')
                s = Search(f'{song} {mainuiwindow.radio_button_state}')
                for obj in s.results[:2]:
                    x = str(obj)
                    video_id = x[x.rfind('=') + 1:].strip('>')
                    video_url = f'https://www.youtube.com/watch?v={video_id}'
                    video_list.append(video_url)

                ############## DOWNLOAD
                yt = YouTube(video_list[0])
                stream = yt.streams.get_audio_only()
                self.progress_multi.emit(f'Downloading...{yt.title}')
                file_path = stream.download(output_path=download_location)
                # download_info = [yt.title, file_path, yt.vid_info]
                try:
                    self.progress_multi.emit(f'...converting, renaming and adding IDTags to - {yt.title}')
                    func.convert_rename_add_tags(file_path)
                except Exception as ex:
                    print(ex)
                self.progress_multi.emit(f'Downloaded - {yt.title}')
                # progress_split_ = progress_split_ + round(progress_split)
                # self.progress_bar_multi.emit(progress_split_)
                self.progress_bar_multi.emit(mainuiwindow.progress_bar_multi.value() + 1)
                self.progress_multi.emit('Download complete')
                video_list.clear()
        except Exception as e:
            print(e)
        self.progress_multi.emit(f'All downloads complete, ready for more!')
        self.progress_bar_multi.emit(0)
        self.finished.emit()

class Worker3(QObject):  # third Thread spotify process
    finished = pyqtSignal()
    progress_bar_multi = pyqtSignal(int)  # for Progress bar on multi page
    progress_multi = pyqtSignal(str)  # for label on multi page
    download_count_label = pyqtSignal(str)  # for label on multi page
    pb_max = pyqtSignal(int)

    def run(self):
        try:
            global global_csv_file_path
            tags = []
            with open(global_csv_file_path[0], encoding="utf8") as file:
                reader = csv.reader(file)
                _ = next(reader)
                songs_in_csv = sum(1 for row in reader)
                file.close()

            ''' open the csv, search for these values in the header to get the 
            index so even if they change it up in the future it still might work'''
            with open(global_csv_file_path[0], encoding="utf8") as f:
                reader = csv.reader(f)
                header = next(reader)  # gets the first line / skips
                artist_name_index = header.index('Artist Name(s)')
                song_name_index = header.index('Track Name')
                album_name_index = header.index('Album Name')
                genre_index = header.index('Artist Genres')
                album_release_date_index = header.index('Album Release Date')
                energy_index = header.index('Energy')
                mode_index = header.index('Mode')  # not using since i don't understand the number system they use
                tempo_index = header.index('Tempo')
                song_count = 0
                video_list = []
                print(songs_in_csv)
                self.pb_max.emit(songs_in_csv)
                download_location = mainuiwindow.download_location.text()

                for song in reader:
                    # Get cleanliness on every loop, should be able to hot swap
                    if mainuiwindow.select_audio.isChecked():
                        mainuiwindow.radio_button_state = "official audio"
                    elif mainuiwindow.select_raw_audio.isChecked():
                        mainuiwindow.radio_button_state = "raw audio"
                    elif mainuiwindow.select_clean_audio.isChecked():
                        mainuiwindow.radio_button_state = "clean audio"
                    # Get clenliness on every loop, should be able to hot swap


                    song_count = song_count + 1
                    self.download_count_label.emit(f'Downloading song {song_count} of {songs_in_csv}')
                    '''these are the tags from the csv file'''
                    tags.append(song[artist_name_index])
                    tags.append(song[song_name_index])
                    tags.append(song[album_name_index])
                    tags.append(song[genre_index])
                    tags.append(song[album_release_date_index])
                    tags.append(song[energy_index])
                    tags.append(song[mode_index])
                    tags.append(song[tempo_index])
                    self.progress_multi.emit(f'Searching for {song[artist_name_index]} by {song[song_name_index]}')
                    s = Search(f'{song[artist_name_index]} - {song[song_name_index]} {mainuiwindow.radio_button_state}')
                    if not s.results: # if you draw blank rap on the board
                        continue # skip this song
                    for obj in s.results[:1]:
                        x = str(obj)
                        video_id = x[x.rfind('=') + 1:].strip('>')
                        video_url = f'https://www.youtube.com/watch?v={video_id}'
                        video_list.append(video_url)
                    '''i can remove this but i'm fine with storing 
                         link to two search result, might use it someday'''

                    ############## DOWNLOAD function
                    yt = YouTube(video_list[0])
                    stream = yt.streams.get_audio_only()
                    self.progress_multi.emit(f'Downloading...{yt.title}')
                    file_path = stream.download(output_path=download_location)
                    # download_info = [yt.title, file_path, yt.vid_info]

                    try:
                        self.progress_multi.emit(f'...converting, renaming and adding IDTags to - {yt.title}')
                        func.convert_rename_add_tags(file_path, tags=tags)
                        tags.clear()
                        video_list.clear()
                    except Exception as ex:
                        print(ex)
                    self.progress_bar_multi.emit(mainuiwindow.progress_bar_multi.value() + 1)

            self.progress_multi.emit(f'All downloads complete, ready for more!')
            self.download_count_label.emit(f'Ready To Download')
            self.progress_bar_multi.emit(0)
            self.finished.emit()
        except Exception as e2:
            print(e2)
            self.progress_multi.emit(str(e2) + ' MAYBE NOT CSV FILE OR THE CSV DON\'T HAVE THE RIGHT INFO')
            self.finished.emit()


def youtube_single_download(link, op):  # Using this for links still
    if link == '':
        return
    yt = YouTube(link)
    yt.streams.filter(only_audio=True)
    stream = yt.streams.get_audio_only()
    file_path = stream.download(output_path=op)
    download_info = [yt.title, file_path, yt.vid_info]
    try:
        func.convert_rename_add_tags(file_path)
    except Exception as ex:
        print(str(e))
    return download_info


class MainUiWindow(QMainWindow):
    def __init__(self):
        super(MainUiWindow, self).__init__()
        ui_loc = func.resource_path("MainUiWindow_redesign.ui")
        uic.loadUi(ui_loc, self)
        self.thread3 = None
        self.worker3 = None
        self.thread2 = None
        self.worker2 = None

        self.update_label_multi = self.findChild(QLabel, "update_label_multi")
        self.update_count_label_multi = self.findChild(QLabel, "update_count_label_multi")
        self.open_folder_multi = self.findChild(QPushButton, "open_folder_multi")
        self.spotify_button = self.findChild(QPushButton, "spotify_button")
        self.link_multi = self.findChild(QTextEdit, "link_multi")
        self.download_location = self.findChild(QLineEdit, "download_location")
        self.select_audio = self.findChild(QRadioButton, "select_audio")
        self.select_raw_audio = self.findChild(QRadioButton, "select_raw_audio")
        self.select_clean_audio = self.findChild(QRadioButton, "select_clean_audio")
        self.download_list_button = self.findChild(QPushButton, "download_list_button")
        self.change_location_button_multi = self.findChild(QPushButton, "change_location_button_multi")
        self.progress_bar_multi = self.findChild(QProgressBar, "progress_bar_multi")


        # Actions
        self.progress_bar_multi.setMaximum(100)
        self.download_location.setText(f'{func.get_os_downloads_folder()}/Youtube/Multi')
        self.download_list_button.clicked.connect(self.download_list_clicked)
        self.open_folder_multi.clicked.connect(lambda: self.open_folder_clicked())
        self.change_location_button_multi.clicked.connect(lambda: self.download_location_picker())
        self.spotify_button.clicked.connect(lambda: self.csv_file_picker())
        self.link_multi.textChanged.connect(lambda: self.disable_spotify_on_text())

        '''do on text enter disable spotify button
        The QTextEdit textChanged signal has a different signature to the 
        QLineEdit textChanged signal, in that it doesn't pass the text 
        that was changed. This is because QTextEdit supports rich-text 
        (i.e. html) as well as plain-text, so you need to explicitly request 
        the content-type you want:

        self.IP.textChanged.connect(self.textSonDurum)
    
        def textSonDurum(self):
        print("Text changed...>>> " + self.IP.toPlainText())'''

    def disable_spotify_on_text(self):
        if not self.link_multi.toPlainText():
            self.spotify_button.setEnabled(True)
        else:
            self.spotify_button.setEnabled(False)

    def reportProgress_multi(self, s):
        self.update_label_multi.setText(s)

    def report_count_Progress_multi(self, s):
        self.update_count_label_multi.setText(s)

    def report_progress_bar_multi(self, s):
        self.progress_bar_multi.setValue(s)

    def setPB_Max(self, s):
        print('progress bar max value before change ', self.progress_bar_multi.maximum())
        self.progress_bar_multi.setMaximum(s)
        print('progress bar max value after change ', self.progress_bar_multi.maximum())


    def download_location_picker(self):
        user_location = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.download_location.setText(user_location)
        return user_location

    def csv_file_picker(self):
        global global_csv_file_path
        global_csv_file_path = QFileDialog.getOpenFileName(self)
        print(global_csv_file_path)
        if not global_csv_file_path[0]:
            return
        self.spotify_button_clicked()
        return


    #########################This triggers the Worker2 Thread#######################
    def download_list_clicked(self):  # thread 2
        if mainuiwindow.link_multi.toPlainText() == '':
            QMessageBox.about(self, "List Empty", "Please add song names or links to the list")
            return

        self.thread2 = QThread()
        self.worker2 = Worker2()
        self.worker2.moveToThread(self.thread2)
        self.thread2.started.connect(self.worker2.run)
        self.worker2.finished.connect(self.thread2.quit)
        self.worker2.finished.connect(self.worker2.deleteLater)
        self.thread2.finished.connect(self.thread2.deleteLater)
        self.worker2.progress_multi.connect(self.reportProgress_multi)
        self.worker2.progress_bar_multi.connect(self.report_progress_bar_multi)
        self.worker2.pb_max.connect(self.setPB_Max)

        self.worker2.download_count_label.connect(self.report_count_Progress_multi)

        self.thread2.start()
        # Final resets
        self.download_list_button.setEnabled(False)
        self.link_multi.setEnabled(False)
        self.spotify_button.setEnabled(False)
        self.thread2.finished.connect(
            lambda: self.download_list_button.setEnabled(True)
        )
        self.thread2.finished.connect(
            lambda: self.link_multi.clear()
        )
        self.thread2.finished.connect(
            lambda: self.link_multi.setEnabled(True)
        )
        self.thread2.finished.connect(
            lambda: self.spotify_button.setEnabled(True)
        )


    ################################################

    #########################This triggers the Worker2 Thread#######################
    def spotify_button_clicked(self):  # Spotify process

        self.thread3 = QThread()
        self.worker3 = Worker3()
        self.worker3.moveToThread(self.thread3)
        self.thread3.started.connect(self.worker3.run)
        self.worker3.finished.connect(self.thread3.quit)
        self.worker3.finished.connect(self.worker3.deleteLater)
        self.thread3.finished.connect(self.thread3.deleteLater)
        self.worker3.progress_multi.connect(self.reportProgress_multi)
        self.worker3.download_count_label.connect(self.report_count_Progress_multi)
        self.worker3.progress_bar_multi.connect(self.report_progress_bar_multi)
        self.worker3.pb_max.connect(self.setPB_Max)
        self.thread3.start()
        # Final resets
        self.download_list_button.setEnabled(False)
        self.link_multi.setEnabled(False)
        self.spotify_button.setEnabled(False)
        self.thread3.finished.connect(
            lambda: self.download_list_button.setEnabled(True)
        )
        self.thread3.finished.connect(
            lambda: self.spotify_button.setEnabled(True)
        )
        self.thread3.finished.connect(
            lambda: self.link_multi.setEnabled(True)
        )

    ################################################

    def open_folder_clicked(self):
        path = self.download_location.text()

        if platform == "win32":
            try:
                os.startfile(path)
            except Exception as e:
                print(e)

        elif platform == "darwin":
            try:
                subprocess.Popen(["open", path])
            except Exception as e:
                print(e)
        else:
            try:
                print(platform)
                subprocess.Popen(["xdg-open", path])
            except Exception as e:
                print(e)
    ''' This will handle playlist when i'm ready to impliment'''
    # def download_youtube_playlist(self):
    #     print('playlist func ran')
    #     pl = input('Paste playlist here >')
    #     playlist = Playlist(pl)
    #     print('*' * 40)
    #     print(f'Playlist contains {len(playlist)} items')
    #     print('*' * 40)
    #     for url in playlist[:3]:
    #         func.youtube_single_download(url)
    ''' This def download_youtube_playlist(self): will handle playlist when i'm ready to impliment'''

    # def download_list_of_songs_from_file(self, list_of_songs):
    #     print('playlist from file func ran')
    #     self.update_label.setText('Getting list of songs from file')
    #     self.update_label.setText(f'File contains {len(list_of_songs)} songs')
    #     for song in list_of_songs:
    #         self.update_label.setText(f'Currently downloading song - {song}')
    #         self.func.youtube_single_download(song)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainuiwindow = MainUiWindow()
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icon.ico"), QtGui.QIcon.Selected, QtGui.QIcon.On)
    mainuiwindow.setWindowIcon(icon)
    mainuiwindow.setFixedWidth(800)
    mainuiwindow.setFixedHeight(400)
    mainuiwindow.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(e)


def spotify_downloader():
    return None
