# Standard library imports
import os
import re
import time
import threading
import math
import tempfile

# Third-party library imports
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext

from mutagen.mp3 import MP3
import PyPDF2
from gtts import gTTS
import speech_recognition as sr
import pygame
import pygame.mixer as pym
import ttkbootstrap as ttk
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import pdfplumber

from ui import setup_ui

# Initialize Pygame
pym.init()
pygame.mixer.init()

# Global variables
results = []
temp_file_path = None
selected_language = 'en'

# Function to handle language selection
def change_language(event):
    global selected_language
    selected_language = language_dict[language_var.get()]
    print(f"Language selected: {selected_language}")

def cleanup_temp_file():
    global temp_file_path
    if temp_file_path and os.path.exists(temp_file_path):
        # Stop any music playback
        pym.music.stop()
        # Unload the music
        pym.music.unload()
        # Wait for a short time to ensure music is unloaded
        time.sleep(0.5)
        # Now delete the file
        os.remove(temp_file_path)

# Function to extract text and format from page elements
def text_extraction(element):
    line_text = element.get_text()
    
    # Find formats of the text
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            for character in text_line:
                if isinstance(character, LTChar):
                    line_formats.append(character.fontname)
                    line_formats.append(character.size)
    
    format_per_line = list(set(line_formats))
    return line_text, format_per_line

# Function to convert text to speech and save it as an MP3
def speak_text(text, pdf_name):
    global temp_file_path

    tts = gTTS(text=text, lang=selected_language)

    # Extract the base name of the PDF file
    base_name = os.path.splitext(os.path.basename(pdf_name))[0]

    # Create a temporary file name for the MP3 file
    temp_file_name = f"{base_name}.mp3"

    # Get the directory path for temporary files
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory

    # Create the full path for the temporary MP3 file
    temp_file_path = os.path.join(temp_dir, temp_file_name)

    # Save the speech to the temporary file
    tts.save(temp_file_path)
    print(f"MP3 file saved at: {temp_file_path}")
    return temp_file_path

# Function to extract text from PDF and convert it to MP3
def text_to_mp3(pdf_path):
    # Create a pdf reader object
    pdfFileObj = open(pdf_path, 'rb')
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)
    
    # Initialize a variable to store text from all pages
    full_text = ''

    # We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        print("Processing Page:", pagenum)
        
        # Initialize the variables needed for the text extraction from the page
        pageObj = pdfReaded.pages[pagenum]
        page_text = []

        # Extract elements on the page
        page_elements = [(element.y1, element) for element in page._objs]
        page_elements.sort(key=lambda a: a[0], reverse=True)

        # Iterate over the elements to extract text and format
        for i, component in enumerate(page_elements):
            element = component[1]
            if isinstance(element, LTTextContainer):
                line_text, _ = text_extraction(element)
                page_text.append(line_text)

        # Append the text from the current page
        full_text += ' '.join(page_text) + '\n'

    # Clean up the text by removing unwanted characters (optional)
    full_text = re.sub(r'\|', '', full_text)
    # Clean up the extracted text by replacing multiple newlines with a single space
    full_text = " ".join(full_text.splitlines()).strip()
    print(f"Extracted Text: {full_text}...")  # Preview the first 500 characters

    display_text_in_gui(full_text)
    # Convert the text to speech using gTTS
    mp3_file_path = speak_text(full_text, pdf_path)

    pdfFileObj.close()

    return mp3_file_path  # Return the path to the generated mp3 file

running = True
playlist = []
current_song = 0
current_song_name = ""
playing = False
stopped = True
autoplay = True
id_ = None
muted = False
total_time = 0
converted_total_time = 0

import speech_recognition as sr

recognizer = sr.Recognizer()

def voice_control():
    global recognizer
    print("Voice control function called.")
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, 0.5)  # Adjust for ambient noise
            print("Listening for a command...")
            try:
                audio = recognizer.listen(source, timeout=5)  # Adjust the timeout as needed
                print("Audio captured.")
                command = recognizer.recognize_google(audio).lower()
                print("You said: " + command)
                if "play" in command:
                    play_pdf()
                elif "stop" in command:
                    pause_pdf()
                elif "next" in command:
                    nextbtn()
                elif "previous" in command:
                    prevbtn()
                elif "mute" in command:
                    toggle_mute()
                elif "forward" in command:
                    fast_forward()
                elif "backward" in command:
                    fast_backward()
                elif "rewind" in command:  # Rewind functionality
                    rewind()
                else:
                    print("Command not recognized.")
            except sr.UnknownValueError:
                print("Google could not understand the audio.")
            except sr.RequestError as e:
                print(f"Error with Google recognition: {e}")
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected within the timeout period.")
    except OSError as e:
        print(f"Microphone error: {e}")
    except Exception as e:
        print(f"Unexpected error in voice control: {e}")

def start_voice_recognition():
    global running
    while running:  # Check the running flag
        voice_control()
        check_status()
        print(stopped)
        print("is playing:",playing)
        print("current time:",slider_progress.get())
        print("total time:",math.floor(total_time))

def find_index(string, string_list):
    try:
        index = string_list.index(string)
        return index
    except ValueError:
        return None

def rewind(event=None):
    global stopped, playing, total_time, converted_total_time, current_song_name
    try:
        playlist_index = find_index(current_song_name, playlist)
    except Exception as e:
        print(f"Error: No PDF is playing - {str(e)}")
    else:
        if playing:
            slider_progress.set(0)  # Reset slider to the beginning
            lbl_currenttime['text'] = "00:00"  # Reset timestamp to the beginning
            pym.music.rewind()
            pym.music.play(loops=0)
            play_time()  # Restart the logic for updating slider and timestamp
        elif not stopped:
            rewindsong(playlist_index)
        else:
            playsong(playlist_index)
        
            

def fast_forward():
    try:
        current_time = slider_progress.get()
        new_time = min(current_time + 10, total_time)  # Fast forward by 10 seconds
        slider_progress.set(new_time)  # Update slider position
        lbl_currenttime['text'] = time.strftime('%M:%S', time.gmtime(new_time))  # Update timestamp
        pym.music.play(loops=0, start=new_time)
        play_pdf()
    except Exception as e:
        print(f"Error: {str(e)}")

def fast_backward():
    try:
        current_time = slider_progress.get()
        new_time = max(current_time - 10, 0)  # Rewind by 10 seconds
        slider_progress.set(new_time)  # Update slider position
        lbl_currenttime['text'] = time.strftime('%M:%S', time.gmtime(new_time))  # Update timestamp
        pym.music.play(loops=0, start=new_time)
        play_pdf()
    except Exception as e:
        print(f"Error: {str(e)}")

def openfolder(x=None):
    folder_path = str(filedialog.askdirectory(title='Choose Folder'))
    if folder_path=="":
        return
    mp3_files = []
    for i in os.listdir(folder_path):
        if i.endswith('pdf'):
            mp3_files.append(f'{folder_path}/{i}')
        
    openandplay(mp3_files)

def openfiles(x=None):
    new_song =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),))
    print(new_song)
    if new_song:
        openandplay(new_song)

def openandplay(new_song):
    global playlist
    new_songs = text_to_mp3(new_song)
    if new_songs==[]:
        pass
    elif playlist == []:
        playlist.append(new_songs)
        playsong(0)
        print(playlist)
    else:
        create_new_playlist = messagebox.askyesno('MATA', 'Do you want to create a new list?\nIf NO, PDF will be added to queue.')
        if create_new_playlist==True:
            playlist.clear()
            playlist.append(new_songs)
            lbl_currenttime.after_cancel(id_)
            playsong(0)
        else:
            playlist.append(new_songs)
            if len(playlist)>1:
                lbl_upnexttitle['text'] = os.path.basename(playlist[current_song+1])

    print(playlist)

def playsong(n):
    global stopped, playing, total_time, converted_total_time, current_song_name
    current_song_name = playlist[current_song]
    lbl_currentlyplayingtitle['text'] = os.path.basename(playlist[n])
    try:
        lbl_upnexttitle['text'] = os.path.basename(playlist[n+1])
    except IndexError:
        lbl_upnexttitle['text'] = os.path.basename(playlist[0])

    playing = True
    stopped = False
    btn_playpause['text'] = "Stop"
    lbl_currenttime['text'] = "00:00"
    slider_progress['value'] = 0

    print(current_song_name)

    total_time = MP3(current_song_name).info.length
    converted_total_time = time.strftime('%M:%S', time.gmtime(total_time))
    lbl_totaltime['text'] = converted_total_time
    slider_progress['to'] = total_time

    pym.music.load(playlist[n])
    pym.music.play(loops=0)
    play_time()

def check_status():
    global playing, stopped
    # This checks if the music has stopped playing
    if not pym.music.get_busy():
        playing = False
        print("Song finished playing")
        if int(slider_progress.get()) >= int((total_time)):
            stopped = True


def rewindsong(n):
        
    playbtn()
    pym.music.play(loops=0)
    playing = True
    pym.music.load(playlist[n])
    lbl_currenttime['text'] = "00:00"
    btn_playpause['text'] = "Stop"
    slider_progress.set(0)
    print(current_song_name)



def playbtn(x=None):
    global playing
    if playlist==[] and stopped==True:
        pass
    elif playlist!=[] and stopped==True:
        playsong(current_song)
    elif playlist!=[] and stopped==False:
        if playing==False:
            btn_playpause['text'] = "Stop"
            playing = True
            pym.music.unpause()
        else:
            btn_playpause['text'] = "Play"
            playing = False
            pym.music.pause()

def play_pdf():
    global playing
    if playlist == [] and stopped == True:
        pass
    elif playlist != [] and stopped == True:
        play_pdf(current_song)
    elif playlist != [] and stopped == False:
        btn_playpause['text'] = "Stop"
        playing = True
        pym.music.unpause()

def pause_pdf():
    global playing
    if playlist != [] and stopped == False:
        btn_playpause['text'] = "Play"  # Update button text to "Play"
        playing = False
        pym.music.pause()

def nextbtn(x=None):
    global current_song, current_song_name
    if stopped==True or len(playlist)==1:
        pass
    else:
        lbl_currenttime.after_cancel(id_)
        try:
            current_song += 1
            current_song_name = playlist[current_song]
            playsong(current_song)
        except IndexError:
            current_song = 0
            playsong(current_song)
            current_song_name = playlist[current_song]
        try:    
            lst_playlist.selection_clear(0, END)
            lst_playlist.selection_set(current_song)
        except:
            pass

def prevbtn(x=None):
    global current_song, current_song_name
    if stopped==True or len(playlist)==1:
        pass
    else:
        lbl_currenttime.after_cancel(id_)
        try:
            current_song -= 1
            current_song_name = playlist[current_song]
            playsong(current_song)
        except IndexError:
            current_song = -1
            current_song_name = playlist[current_song]
            playsong(current_song)
        try:    
            lst_playlist.selection_clear(0, END)
            lst_playlist.selection_set(current_song)
        except:
            pass

def stop(x=None):
    global stopped, playing
    playing = False
    stopped = True
    btn_playpause['text'] = "Play"  # Update button text to "Play"
    lbl_currentlyplayingtitle['text'] = '\n'
    lbl_upnexttitle['text'] = '\n'
    lbl_currenttime['text'] = '00:00'
    lbl_totaltime['text'] = '00:00'
    slider_progress['value'] = 0
    pym.music.stop()

def toggle_autoplay():
    global autoplay
    if autoplay==False:
        btn_autoplay['text'] = 'Autoplay: ON'
        autoplay = True
    else:
        btn_autoplay['text'] = 'Autoplay: OFF'
        autoplay = False

def play_time():
    global id_
    converted_current_time = time.strftime('%M:%S', time.gmtime(int(slider_progress.get())))

    if stopped:
        return
    
    if int(slider_progress.get())==int(total_time):
        if autoplay==True:
            nextbtn()
            return
        else:
            stop()
    elif playing==True:
        next_time = int(slider_progress.get()) + 1
        slider_progress['value'] = next_time
        lbl_currenttime['text'] = converted_current_time
    else:
        pass

    id_ = lbl_currenttime.after(1000, play_time)
    
def play_time_rewind():
    global id_
    converted_current_time = time.strftime('%M:%S', time.gmtime(int(slider_progress.get())))
    if int(slider_progress.get())==int(total_time):
        if autoplay==True:
            nextbtn()
            return
        else:
            stop()
    elif playing==True:
        next_time = int(slider_progress.get()) + 1
        slider_progress['value'] = next_time
        lbl_currenttime['text'] = converted_current_time
    else:
        pass

    id_ = lbl_currenttime.after(1000, play_time)    
    
def slider(event):
    if not stopped:
        pym.music.play(loops=0, start=slider_progress.get())


def toggle_mute(x=None):
    global muted
    if muted==False:
        btn_volume['text'] = "Unmute"
        pym.music.set_volume(0.0)
        muted = True
    else:
        btn_volume['text'] = "Mute"
        pym.music.set_volume(slider_volume.get()/100)
        muted = False

def set_volume(x=0):
    if muted==True:
        return
    pym.music.set_volume(slider_volume.get()/100)

def pl_play_song():
    global current_song, current_song_name
    s = lst_playlist.curselection()[0]
    if s==current_song:
        messagebox.showinfo("MATA", "This pdf is already playing.")
    else:
        current_song = s 
        current_song_name = playlist[current_song]   
        lbl_currenttime.after_cancel(id_)
        playsong(s)

def update_playlistbox():
    lst_playlist.delete(0, END)
    for i in playlist:
        lst_playlist.insert(END, os.path.basename(i))

def pl_shift_up():
    global playlist
    s = lst_playlist.curselection()[0]
    if playlist[s]==current_song_name:
        messagebox.showerror("MATA", "This PDF is currently playing.\nThis cannot be shifted.")
    else:
        playlist[s], playlist[s-1] = playlist[s-1], playlist[s]
        update_playlistbox()
        if s==0:
            lst_playlist.selection_set(len(playlist)-1) 
        else:
            lst_playlist.selection_set(s-1) 

def pl_shift_down():
    global playlist
    s = lst_playlist.curselection()[0]
    if playlist[s]==current_song_name:
        messagebox.showerror("MATA", "This PDF is currently playing.\nThis cannot be shifted.")
    else:
        try:
            playlist[s], playlist[s+1] = playlist[s+1], playlist[s]
            update_playlistbox()
            lst_playlist.selection_set(s+1)  
        except IndexError:
            sd = playlist.pop()
            playlist = [sd]+playlist
            update_playlistbox()
            lst_playlist.selection_set(0)

def pl_delete_song():
    global playlist
    s = lst_playlist.curselection()[0]
    if playlist[s]==current_song_name:
        messagebox.showerror("MATA", "This PDF is currently playing.\nThis cannot be deleted.")
    else:
        playlist.pop(s)
        update_playlistbox()
        lst_playlist.selection_set(s)

def show_playlist():
    global lst_playlist
    if playlist==[]:
        messagebox.showerror("MATA", "List is empty. Add some PDF first")
    else:
        playlist_window = Toplevel()
        playlist_window.title("MATA - PDFs")
        playlist_window.resizable(0,0)

        lst_playlist = Listbox(playlist_window,activestyle="underline", background="black", fg='pink', selectmode=SINGLE, width=80, selectbackground='pink', selectforeground='black')
        lst_playlist.grid(column=0, padx=10, pady=10, row=0)

        frm_buttons = Frame(playlist_window, height=200, width=200)
        frm_buttons.grid(column=1, row=0)
        btn_shiftup = Button(frm_buttons, text='Shift Up', width=8, command=pl_shift_up)
        btn_shiftup.grid(column=0, padx=5, pady=5, row=0)
        btn_shiftdown = Button(frm_buttons, text='Shift Down', width=8, command=pl_shift_down)
        btn_shiftdown.grid(column=0, padx=5, pady=5, row=1)
        btn_play = Button(frm_buttons,text='Play Song', width=8, command=pl_play_song)
        btn_play.grid(column=0, padx=5, pady=5, row=2)
        btn_remove = Button(frm_buttons, text='Remove ', width=8, command=pl_delete_song)
        btn_remove.grid(column=0, padx=5, pady=5, row=3)

        update_playlistbox()
        lst_playlist.selection_set(current_song)   

        playlist_window.mainloop()

def close():
    cleanup_temp_file()
    global running
    running = False  # Set the running flag to False
    time.sleep(0.5)
    root.destroy()


def display_text_in_gui(extracted_text):
        # Clean up the extracted text by replacing multiple newlines with a single space
    cleaned_text = " ".join(extracted_text.splitlines()).strip()
    
    # Create a LabelFrame for extracted text
    lbl_extracted = ttk.LabelFrame(root, text="EXTRACTED TEXT", relief="ridge")
    lbl_extracted.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

    # Create a ScrolledText widget for displaying the extracted text
    text_widget = scrolledtext.ScrolledText(lbl_extracted, wrap=tk.WORD, width=60, height=15, font=("Helvetica", 12))
    text_widget.pack(padx=10, pady=10)

    # Insert the extracted text into the ScrolledText widget
    text_widget.insert(tk.END, extracted_text)

    # Disable the widget so it’s read-only
    text_widget.config(state=tk.DISABLED)



root = tk.Tk()  # Create an instance of Tk
root.title("MATA")  # Set the title of the window
root.geometry('700x700')
root.resizable(0, 0)
root.iconbitmap('icons/mata.ico')
style = ttk.Style("darkly")

root.bind('<space>', playbtn)
root.bind('m', toggle_mute)
root.bind('n', nextbtn)
root.bind('p', prevbtn)
root.bind('<Control-o>', openfiles)
root.bind('<Control-f>', openfolder)
root.bind('r',rewind)
root.bind('<Right>', lambda event: fast_forward())
root.bind('<Left>', lambda event: fast_backward())


# Create a daemon thread for voice recognition
voice_thread = threading.Thread(target=start_voice_recognition, daemon=True)

# Start the voice recognition thread
voice_thread.start()

# Use the setup_ui function to initialize the UI
ui_elements = setup_ui(root, playbtn, prevbtn, nextbtn, openfiles, toggle_autoplay, show_playlist, toggle_mute, set_volume, slider, fast_forward, fast_backward, rewind)

# Access UI elements
lbl_currentlyplayingtitle = ui_elements["lbl_currentlyplayingtitle"]
btn_playpause = ui_elements["btn_playpause"]
btn_autoplay = ui_elements["btn_autoplay"]
slider_progress = ui_elements["slider_progress"]
lbl_currenttime = ui_elements["lbl_currenttime"]
lbl_totaltime = ui_elements["lbl_totaltime"]
lbl_upnexttitle = ui_elements["lbl_upnexttitle"]
language_var = ui_elements["language_var"]
language_dict = ui_elements["language_dict"]

root.protocol("WM_DELETE_WINDOW", close)
root.mainloop()