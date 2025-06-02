# UI-related code for MATA application

import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk

def setup_ui(root, playbtn, prevbtn, nextbtn, openfiles, toggle_autoplay, show_playlist, toggle_mute, set_volume, slider, fast_forward, fast_backward, rewind):
    # Adjust the grid layout to center components
    root.grid_columnconfigure(0, weight=1)

    # Current Playing section
    lbl_currentlyplaying = ttk.LabelFrame(root, text="CURRENTLY PLAYING", relief="ridge")
    lbl_currentlyplaying.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    lbl_currentlyplayingtitle = ttk.Label(lbl_currentlyplaying, text='WELCOME TO MATA\n ', width=60, wraplength=480, anchor='center', justify='center')
    lbl_currentlyplayingtitle.grid(row=0, column=3)

    # Controls section
    frm_controls = ttk.Frame(root)
    frm_controls.grid(row=1, column=0, pady=10)
    btn_previous = ttk.Button(frm_controls, text="Previous", command=prevbtn)
    btn_previous.grid(row=0, column=0, padx=10, pady=2)
    btn_playpause = ttk.Button(frm_controls, text="Play", command=playbtn)
    btn_playpause.grid(row=0, column=1, padx=10, pady=2)
    btn_next = ttk.Button(frm_controls, text="Next", command=nextbtn)
    btn_next.grid(row=0, column=2, padx=10, pady=2)
    btn_open = ttk.Button(frm_controls, text="Choose File", command=openfiles)
    btn_open.grid(row=0, column=3, padx=10, pady=2)

    # Language selection
    language_var = tk.StringVar()  # To hold the selected language's display name
    language_dict = {'English': 'en', 'Tagalog': 'tl'}  # Mapping of displayed text to value

    language_options = ttk.Combobox(frm_controls, textvariable=language_var, values=list(language_dict.keys()), state='readonly', width=20)
    language_options.grid(row=0, column=4, padx=10, pady=2)
    language_options.bind('<<ComboboxSelected>>', lambda event: change_language(language_var, language_dict))
    language_options.current(0)  # Set the default selection to English

    # Autoplay and Playlist controls
    frm_adcontrols = ttk.Frame(root)
    frm_adcontrols.grid(row=2, column=0)
    btn_autoplay = ttk.Button(frm_adcontrols, text="Autoplay: ON", command=toggle_autoplay)
    btn_autoplay.grid(row=0, column=0, pady=10, padx=5)
    btn_playlist = ttk.Button(frm_adcontrols, text='Show Playlist', command=show_playlist)
    btn_playlist.grid(row=0, column=1, pady=10, padx=5)

    # Volume controls
    lbl_volume = ttk.LabelFrame(frm_adcontrols, text='VOLUME', relief="ridge")
    lbl_volume.grid(row=0, column=2, pady=10)
    btn_volume = ttk.Button(lbl_volume, text='Mute', command=toggle_mute)
    btn_volume.grid(row=0, column=0, padx=5, pady=3)
    slider_volume = ttk.Scale(lbl_volume, from_=0, to=100, orient=tk.HORIZONTAL, length=150, value=100, command=set_volume)
    slider_volume.grid(row=0, column=1, padx=5, pady=3)

    # Progress section
    frm_progress = ttk.LabelFrame(root)
    frm_progress.grid(row=3, column=0)
    lbl_currenttime = ttk.Label(frm_progress, text="00:00")
    lbl_currenttime.grid(row=0, column=0, padx=10)
    slider_progress = ttk.Scale(frm_progress, from_=0, to=100, orient=tk.HORIZONTAL, length=365, value=0, command=slider)
    slider_progress.grid(row=0, column=1, pady=20)
    lbl_totaltime = ttk.Label(frm_progress, text="00:00")
    lbl_totaltime.grid(row=0, column=2, padx=10)

    # Up Next section
    lbl_upnext = ttk.LabelFrame(root, text="UP NEXT", relief="ridge")
    lbl_upnext.grid(row=4, column=0, padx=10, pady=10)
    lbl_upnexttitle = ttk.Label(lbl_upnext, text='\n', font=('consolas', 10), width=60, wraplength=480, anchor='center')
    lbl_upnexttitle.grid(row=0, column=0)

    return {
        "lbl_currentlyplayingtitle": lbl_currentlyplayingtitle,
        "btn_playpause": btn_playpause,
        "btn_autoplay": btn_autoplay,
        "slider_progress": slider_progress,
        "lbl_currenttime": lbl_currenttime,
        "lbl_totaltime": lbl_totaltime,
        "lbl_upnexttitle": lbl_upnexttitle,
        "language_var": language_var,
        "language_dict": language_dict
    }

def change_language(language_var, language_dict):
    selected_language = language_dict[language_var.get()]
    print(f"Language selected: {selected_language}")
