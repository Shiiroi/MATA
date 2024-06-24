from tkinter import *
import PyPDF2
import pyttsx3
import pygame
from gtts import gTTS
import speech_recognition as sr
from tkinter import filedialog
from tkinter import messagebox
import ttkbootstrap as ttk
import pygame.mixer as pym

from operator import length_hint
from pyexpat import model
from mutagen.mp3 import MP3
import time, os
import threading


import re

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import pdfplumber

import os

import tempfile


pym.init()
pygame.mixer.init()

results = []

import tempfile

temp_file_path = None

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


def speak_text(text, pdf_name):
    global temp_file_path

    # Create a gTTS object
    tts = gTTS(text=text, lang='tl')


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
    print(temp_file_path)
    return temp_file_path


# def speak_text(text,name):
#     # Create a gTTS object
#     tts = gTTS(text=text, lang='en')

#     # Save the speech to an audio file
#     tts.save(name + ".mp3")
#     print(name + ".mp3")
#     return name + ".mp3"

def text_extraction(element):
    # Extracting the text from the in line text element
    line_text = element.get_text()
    
    # Find the formats of the text
    # Initialize the list with all the formats appeared in the line of text
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # Iterating through each character in the line of text
            for character in text_line:
                if isinstance(character, LTChar):
                    # Append the font name of the character
                    line_formats.append(character.fontname)
                    # Append the font size of the character
                    line_formats.append(character.size)
    # Find the unique font sizes and names in the line
    format_per_line = list(set(line_formats))
    
    # Return a tuple with the text in each line along with its format
    return (line_text, format_per_line)
# Extracting tables from the page

def text_to_mp3(pdf_path):
    # Create a pdf file object
    pdfFileObj = open(pdf_path, 'rb')
# Create a pdf reader object
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)
# Create the dictionary to extract text from each image
    text_per_page = {}
# Create a boolean variable for image detection
    image_flag = False

# We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        print("Processing Page:", pagenum)
        # Initialize the variables needed for the text extraction from the page
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        line_format = []
        page_content = []
        # Initialize the number of the examined tables
        table_in_page= -1
        # Open the pdf file
        pdf = pdfplumber.open(pdf_path)


    # Find all the elements
    page_elements = [(element.y1, element) for element in page._objs]
    # Sort all the element as they appear in the page 
    page_elements.sort(key=lambda a: a[0], reverse=True)


    # Find the elements that composed a page
    for i,component in enumerate(page_elements):
        # Extract the element of the page layout
        element = component[1]

            # Check if the element is text element
        if isinstance(element, LTTextContainer):
            # Use the function to extract the text and format for each text element
            (line_text, format_per_line) = text_extraction(element)
            # Append the text of each line to the page text
            page_text.append(line_text)
            # Append the format for each line containing text
            line_format.append(format_per_line)
            page_content.append(line_text)


    # Create the key of the dictionary
    dctkey = 'Page_'+str(pagenum)
    # Add the list of list as value of the page key
    text_per_page[dctkey]= [page_text, line_format,]
    # Close the pdf file object
    pdfFileObj.close()
    # Delete the additional files created if image is detected
    if image_flag:
        os.remove('cropped_image.pdf')
        os.remove('PDF_image.png')
    # Display the content of the page
    result = ''
    for page_key in text_per_page.keys():
        # result += ''.join(text_per_page[page_key][4])  # Concatenate text content from each page
        # Display the content of the page
        result = ''
        for page_key in text_per_page.keys():
            # Concatenate text content from each line on the page
            for line_text in text_per_page[page_key][0]:
                result += line_text


    mp3_file_path = r"C:\Users\Vince Roi\Desktop"
    result = re.sub(r'\|', '', result)

    print(result)


    results.append(result)


    file_name = os.path.basename(pdf_path)
    return speak_text(result,file_name)


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
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source,0.5)  # Adjust for ambient noise
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
            print("Error with Google recognition: {0}".format(e))
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected within the timeout period.")
            pass  # Handle timeout (no speech detected within the timeout period)

def start_voice_recognition():
    global running
    while running:  # Check the running flag
        voice_control()

def find_index(string, string_list):
    try:
        index = string_list.index(string)
        return index
    except ValueError:
        return None

def rewind():
    try:
        playlist_index = find_index(current_song_name, playlist)
        if not stopped:
            slider_progress.set(0)
            pym.music.rewind()
            pym.music.play(loops=0)
        elif playlist_index is not None:
            playsong(playlist_index)
        else:
            slider_progress.set(0)
            pym.music.rewind()
            pym.music.play(loops=0)
            current_time = slider_progress.get()
            new_time = min(current_time, total_time) 
            slider_progress.set(new_time)
            pym.music.play(loops=0, start=new_time)
    except Exception as e:
        print(f"Error: No PDF is playing - {str(e)}")


def fast_forward():
    try:
        current_time = slider_progress.get()
        new_time = min(current_time + 10, total_time)  # Fast forward by 10 seconds
        slider_progress.set(new_time)
        pym.music.play(loops=0, start=new_time)
    except:
        print("Error: No PDF is playing")

def fast_backward():
    try:
        current_time = slider_progress.get()
        new_time = max(current_time - 10, 0)  # Rewind by 10 seconds
        slider_progress.set(new_time)
        pym.music.play(loops=0, start=new_time)
    except:
        print("Error: No PDF is playing")
        
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
        btn_playpause['text'] = "Play"
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
    btn_playpause['text'] = "Play"
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

def show_shortcuts():

    help_window = Toplevel()
    help_window.resizable(False, False)
    help_window.title("MATA - Shortcuts")

    frm_heading = Frame(help_window)
    frm_heading.grid(column=0, padx=5, pady=5, row=0)
    lbl_heading = Label(frm_heading, font="{consolas} 24 {}", justify="center", text='Shortcut Keys')
    lbl_heading.grid(column=0, row=0)

    frm_shortcuts = Frame(help_window)
    frm_shortcuts.grid(column=0, row=1)
    lbl_funcheading = LabelFrame(frm_shortcuts, height=200, text='FUNCTION', width=200)
    lbl_funcheading.grid(column=1, ipadx=10, padx=10, pady=10, row=0)
    lbl_functions = Label(lbl_funcheading, font="{consolas} 12", justify="left", text='Open Files\nPlay/Stop\nNext\nPrevious\nMute/Unmute')
    lbl_functions.grid(column=0, padx=10, pady=10, row=0)

    lbl_keysheading = LabelFrame(frm_shortcuts)
    lbl_keysheading.grid(column=0, padx=10, pady=10, row=0)
    lbl_keysheading.configure(height=200, text='KEY', width=200)
    lbl_keys = Label(lbl_keysheading, font="{consolas} 12 {}", justify="center", text='O\nSpace\nN\nP\nX\nM')
    lbl_keys.grid(column=0, padx=10, pady=10, row=0)

    help_window.mainloop()

def close():
    cleanup_temp_file()
    global running
    running = False  # Set the running flag to False
    time.sleep(0.5)
    root.destroy()

def show_about():
    about_window = Toplevel()
    about_window.resizable(False, False)
    about_window.title("MATA Player - About")

    lbl_heading = Label(about_window, font=("", 24), text='About ', width=5)
    lbl_heading.grid(column=0, row=0)

# traditional approach
root = ttk.Window()  # Create an instance of ttk.Window
root.title("MATA")  # Set the title of the window
root.geometry('550x475')
root.resizable(0, 0)
root.iconbitmap('icons/mata.ico')
style = ttk.Style("darkly")

lbl_currentlyplaying = ttk.LabelFrame(root, text="CURRENTLY PLAYING",  relief=RIDGE)
lbl_currentlyplaying.grid(row=0, column=0, padx=3)
lbl_currentlyplayingtitle = ttk.Label(lbl_currentlyplaying, text='WELCOME TO MATA\n ', width=60, wraplength=480,anchor='center')
lbl_currentlyplayingtitle.grid(row=0, column=2)

frm_controls = ttk.Frame(root)
frm_controls.grid(row=1, column=0, pady=10)
btn_previous = ttk.Button(frm_controls, text="Previous", command=prevbtn)
btn_previous.grid(row=0, column=0, padx=10, pady=2)
btn_playpause = ttk.Button(frm_controls, text="Play", command=playbtn)
btn_playpause.grid(row=0, column=1, padx=10, pady=2)
btn_next = ttk.Button(frm_controls, text="Next", command=nextbtn)
btn_next.grid(row=0, column=2, padx=10, pady=2)
btn_open = ttk.Button(frm_controls, text="Choose File", command=openfiles)
btn_open.grid(row=0, column=4, padx=10, pady=2)

frm_adcontrols = ttk.Frame(root)
frm_adcontrols.grid(row=2, column=0)
btn_autoplay = ttk.Button(frm_adcontrols, text="Autoplay: ON", command=toggle_autoplay)
btn_autoplay.grid(row=0, column=0, pady=10, padx=5)
btn_playlist = ttk.Button(frm_adcontrols, text='Show Playlist', command=show_playlist)
btn_playlist.grid(row=0, column=1, pady=10, padx=5)

lbl_volume = ttk.LabelFrame(frm_adcontrols, text='VOLUME',  relief=RIDGE)
lbl_volume.grid(row=0, column=2, pady=10)
btn_volume = ttk.Button(lbl_volume, text='Mute', command=toggle_mute)
btn_volume.grid(row=0, column=0, padx=5, pady=3)
slider_volume = ttk.Scale(lbl_volume, from_=0, to=100, orient=HORIZONTAL, length=150, value=100, command=set_volume)
slider_volume.grid(row=0, column=1, padx=5, pady=3)

frm_progress = ttk.LabelFrame(root)
frm_progress.grid(row=3, column=0)
lbl_currenttime = ttk.Label(frm_progress, text="00:00")
lbl_currenttime.grid(row=0, column=0, padx=10)
slider_progress = ttk.Scale(frm_progress, from_=0, to=100, orient=HORIZONTAL, length=365, value=0, command=slider)
slider_progress.grid(row=0, column=1, pady=20)
lbl_totaltime = ttk.Label(frm_progress, text="00:00")
lbl_totaltime.grid(row=0, column=2, padx=10)

lbl_upnext = ttk.LabelFrame(root, text="UP NEXT",relief=RIDGE)
lbl_upnext.grid(row=4, column=0, padx=3, pady=10)
lbl_upnexttitle = ttk.Label(lbl_upnext, text='\n', font=('consolas', 10), width=60, wraplength=480, anchor='center')
lbl_upnexttitle.grid(row=0, column=2)

root.bind('<space>', playbtn)
root.bind('m', toggle_mute)
root.bind('n', nextbtn)
root.bind('p', prevbtn)
root.bind('<Control-o>', openfiles)
root.bind('<Control-f>', openfolder)
# Bind fast forward and backward functions to corresponding keys
root.bind('<Right>', lambda event: fast_forward())
root.bind('<Left>', lambda event: fast_backward())
# You can call the voice_control function whenever you want to listen for a command
# For example, you can bind it to a specific key, such as 'v' key:
# root.bind('v', lambda event: voice_control())


# Create a daemon thread for voice recognition
voice_thread = threading.Thread(target=start_voice_recognition, daemon=True)

# Start the voice recognition thread
voice_thread.start()

root.protocol("WM_DELETE_WINDOW", close)
root.mainloop()