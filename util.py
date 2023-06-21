import sys
import os
import pickle
import tkinter as tk
from tkinter import messagebox
import face_recognition


def get_button(window, text, color, command, fg='white'):
    button = tk.Button(
        window,
        text=text,
        activebackground="black",
        activeforeground="white",
        fg=fg,
        bg=color,
        command=command,
        height=1,
        width=20,
        font=('Helvetica bold', 20)
    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("sans-serif", 21), justify="left")
    return label


def get_entry_text(window):
    inputtxt = tk.Text(window, height=1, width=19, font=("Arial", 20))
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)


def persistent_load(persid):
    if persid == 'PickleBufferWrapper':
        return pickle._pickle.PickleBufferWrapper
    elif persid == 'NG':
        return None  # or any suitable default value

    raise pickle.UnpicklingError(f"Unsupported persistent load instruction: {persid}")




def recognize(img, db_path):
    # it is assumed there will be at most 1 match in the db

    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted(os.listdir(db_path))

    match = False
    j = 0
    while not match and j < len(db_dir):
        path_ = os.path.join(db_path, db_dir[j])

        with open(path_, 'rb') as file:
            data = file.read()

        # Redirect standard output to null device
        sys.stdout = open(os.devnull, 'w')

        # Load pickle data
        try:
            embeddings = pickle.loads(data)
            match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        except pickle.UnpicklingError:
            # Handle the error appropriately
            embeddings = None

        # Restore standard output
        sys.stdout = sys.__stdout__

        j += 1

    if match:
        return db_dir[j - 1][:-7]
    else:
        return 'unknown_person'


