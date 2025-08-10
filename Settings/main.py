from __future__ import print_function
import httplib2
import os
import io
import threading
import time

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
from pathlib import Path

import pathlib
import shutil
import concurrent.futures
import configparser
import datetime
import subprocess
import re
from glob import glob

import tkinter as tk
from tkinter import messagebox, ttk, filedialog

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
# Code is based on https://tanaikech.github.io/2017/05/02/ocr-using-google-drive-api/
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
# Configuration
SCOPES = "https://www.googleapis.com/auth/drive"
CLIENT_SECRET_FILE = "../credentials.json"
APPLICATION_NAME = "Drive API Python Quickstart"
THREADS = 20
folder_id = ""
path_VSF = ""
OCR_Text = ""
cmd_vsf = ""
srt_file_list = {}

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = os.path.join("./", '../token.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

# Declaration progress_lock  global
progress_lock = threading.Lock()
stop_flag = False
log_file_path = None  # Global variable stores log file name



def stop_processing():
    global stop_flag
    stop_flag = False  # Set stop process flag
    start_button.config(state=tk.NORMAL)  # Re-enable the Start button
    stop_button.config(state=tk.DISABLED)  # Turn off the Stop button when stopped
    VSF_button.config(state=tk.NORMAL)  # Re-enable the VideoSubFinder button
    log_message("The process has been stopped..")







#config = configparser.ConfigParser()
#config.read(r"config.ini")
#folder_id = str(config["settings"]["path_VSF"])

# rite configuration to file
def save_config(folder_id, path_VSF, OCR_Text, cmd_vsf, delete_raw_texts, delete_texts, nen_raw_texts ):
    config = configparser.ConfigParser()
    config["settings"] = {
        "folder_id": folder_id,
        "path_VSF": path_VSF,
        "OCR_Text": OCR_Text,
        "cmd_vsf": cmd_vsf,
        "delete_raw_texts": str(delete_raw_texts),
        "delete_texts": str(delete_texts),
        "nen_raw_texts": str(nen_raw_texts),
    }

    with open("Settings.ini ", "w") as configfile:
        config.write(configfile)


# Read configuration from file when program starts
def load_config():
    config = configparser.ConfigParser()
    config.read("Settings.ini ")

    if "settings" in config:
        folder_id = config["settings"].get("folder_id", "")
        path_VSF = config.get('settings','path_VSF')
        OCR_Text = config.get('settings','OCR_Text')
        cmd_vsf = config.get('settings','cmd_vsf')
        delete_raw_texts = config.getboolean(
            "settings", "delete_raw_texts", fallback=False
        )
        delete_texts = config.getboolean("settings", "delete_texts", fallback=False)
        nen_raw_texts = config.getboolean("settings", "nen_raw_texts", fallback=False)
        return folder_id, path_VSF, OCR_Text, cmd_vsf, delete_raw_texts, delete_texts, nen_raw_texts
    else:
        return "", False, False


# Image scanning and uploading function
def ocr_image(image, line, credentials, current_directory, progress_callback):
    global stop_flag
    tries = 0
    while True:
        if stop_flag:
            print("Process stopped.")
            log_message("The process has been stopped..")
            return
        try:
            http = credentials.authorize(httplib2.Http())
            service = discovery.build("drive", "v3", http=http)
            imgfile = str(image.absolute())
            imgname = str(image.name)
            raw_txtfile = f"{current_directory}/raw_texts/{imgname[:-5]}.txt"
            txtfile = f"{current_directory}/texts/{imgname[:-5]}.txt"

            mime = "application/vnd.google-apps.document"

            res = (
                service.files()
                .create(
                    body={"name": imgname, "mimeType": mime, "parents": [folder_id]},
                    media_body=MediaFileUpload(imgfile, mimetype=mime, resumable=True),
                )
                .execute()
            )

            print(f"{imgname} Done.")
            log_message(f"Complete processing: {imgname}")

            downloader = MediaIoBaseDownload(
                io.FileIO(raw_txtfile, "wb"),
                service.files().export_media(fileId=res["id"], mimeType="text/plain"),
            )
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            service.files().delete(fileId=res["id"]).execute()

            # Content Processing raw text
            with open(raw_txtfile, "r", encoding="utf-8") as raw_text_file:
                text_content = raw_text_file.read()

            text_content = text_content.split("\n")
            text_content = "\n".join(text_content[2:])

            with open(txtfile, "w", encoding="utf-8") as text_file:
                text_file.write(text_content)

            try:
                start_hour = imgname.split("_")[0][:2]
                start_min = imgname.split("_")[1][:2]
                start_sec = imgname.split("_")[2][:2]
                start_micro = imgname.split("_")[3][:3]

                end_hour = imgname.split("__")[1].split("_")[0][:2]
                end_min = imgname.split("__")[1].split("_")[1][:2]
                end_sec = imgname.split("__")[1].split("_")[2][:2]
                end_micro = imgname.split("__")[1].split("_")[3][:3]

            except IndexError:
                print(
                    f"Error processing {imgname}: Filename format is incorrect. Please ensure the correct format is used."
                )
                return

            start_time = f"{start_hour}:{start_min}:{start_sec},{start_micro}"
            end_time = f"{end_hour}:{end_min}:{end_sec},{end_micro}"
            srt_file_list[line] = [
                f"{line}\n",
                f"{start_time} --> {end_time}\n",
                f"{text_content}\n\n",
                "",
            ]

            progress_callback()
            break
        except:
            tries += 1
            if tries > 5:
                raise
            continue

# Main function handles interface
def start_processing(
    file_sub,
    images_dirr,
    delete_raw_texts,
    delete_texts,
    nen_raw_texts,
    progress_callback,
):

    global total_images, completed_scans, stop_flag

    completed_scans = 0
    total_images = 0





    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build("drive", "v3", http=http)

    current_directory = Path(Path.cwd())
    # images_dir = Path(f'{current_directory}/{images_dirr}')
    images_dir = Path(images_dirr)
    raw_texts_dir = Path(f"{current_directory}/raw_texts")
    texts_dir = Path(f"{current_directory}/texts")

    # Edit the subtitle file name (use the path and add .srt at the end)
    subtitle_path = Path(file_sub)
    if subtitle_path.suffix != ".srt":
        subtitle_path = subtitle_path.with_suffix(".srt")

    srt_file = open(subtitle_path, "a", encoding="utf-8")

    # Check for existence of images folder
    if not images_dir.exists():

        print(
            f"Directory not found: {images_dir}"
        )  # Print if directory does not exist

        log_message(f"Error: Directory {images_dir} does not exist.")

        messagebox.showerror(
            "Error",
            f"The image directory '{images_dir}' does not exist.\Please check the path again.",
        )

        return

    if not raw_texts_dir.exists():
        raw_texts_dir.mkdir()
    if not texts_dir.exists():
        texts_dir.mkdir()

    images = []
    for extension in ("*.jpeg", "*.jpg", "*.png", "*.bmp", "*.gif"):
        images.extend(list(Path(images_dirr).rglob(extension)))
        # images.extend(list(Path(f'{current_directory}/{images_dirr}').rglob(extension)))

    total_images = len(images)

    # Write total number of images to log_text
    log_message(f"Total number of images found in folder '{images_dirr}': {total_images}")

    if total_images == 0:

        messagebox.showerror(
            "Error",
            f"Directory '{images_dirr}' does not contain valid images.\n"
            "Please check the format: JPEG, PNG, BMP, GIF.",
        )

        log_message(f"Error: Directory '{images_dirr}' does not contain valid images.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        future_to_image = {
            executor.submit(
                ocr_image,
                image,
                index + 1,
                credentials,
                current_directory,
                progress_callback,
            ): image
            for index, image in enumerate(images)
        }

        for future in concurrent.futures.as_completed(future_to_image):
            if stop_flag:
                break
            try:
                future.result()
            except Exception as exc:
                print(f"{future_to_image[future]} generated an exception: {exc}")
            else:
                with progress_lock:
                    completed_scans += 1
                    progress_callback()

    if stop_flag:
        log_message("The process has been stopped..")
        messagebox.showinfo("Stop", "The process has stopped.")
        return

    # Write lines SRT
    for i in sorted(srt_file_list):
        srt_file.writelines(srt_file_list[i])
    srt_file.close()

    # If the user chooses to compress the folder raw_texts
    if nen_raw_texts:
        try:
            zip_file_path = shutil.make_archive(
                str(file_sub), "zip", str(raw_texts_dir)
            )
            new_zip_file_path = zip_file_path.replace(".srt.zip", ".zip")
            os.rename(zip_file_path, new_zip_file_path)
            print(f"Compressed folder {raw_texts_dir}")
            log_message(f"Compressed folder: {raw_texts_dir}")
        except Exception as e:
            print(f"Error while avoiding folder {raw_texts_dir}: {e}")
            messagebox.showerror("Error", f"Failed to compress folder {raw_texts_dir}: {e}")

    # If the user chooses to delete the folder
    if delete_raw_texts:
        try:
            shutil.rmtree(raw_texts_dir)
            print(f"Deleted folder {raw_texts_dir}")
            log_message(f"Deleted folder: {raw_texts_dir}")
        except Exception as e:
            print(f"Error while deleting folder raw_texts: {e}")
            log_message(f"Error: {e}")
            messagebox.showerror("Error", f"Cannot delete folder raw_texts: {e}")
    if delete_texts:
        try:
            shutil.rmtree(texts_dir)
            print(f"Deleted folder {texts_dir}")
            log_message(f"Deleted folder: {texts_dir}")
        except Exception as e:
            print(f"Error while deleting folder texts: {e}")
            messagebox.showerror("Lỗi", f"Cannot delete folder texts: {e}")

    messagebox.showinfo(
        "Complete", f"Scan completed {total_images} image."
    )
    start_button.config(state=tk.NORMAL)
    VSF_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    log_message(f"Complete processing {total_images} image.")


# Function to update crop value based on selected profile
def update_crop_values(event):
    selected_profile = profile_combobox.get()
    if selected_profile == "Position sub 1":
        crop_top_var.set("0.169261")
        crop_bottom_var.set("0.00589391")
        crop_left_var.set("0")
        crop_right_var.set("1")
        set_entries_state("readonly")
    elif selected_profile == "Position sub 2":
        crop_top_var.set("0.305211")
        crop_bottom_var.set("0.0545906")
        crop_left_var.set("0")
        crop_right_var.set("1")
        set_entries_state("readonly")
    elif selected_profile == "Position sub 3":
        crop_top_var.set("0.186104")
        crop_bottom_var.set("0.0198511")
        crop_left_var.set("0")
        crop_right_var.set("1")
        set_entries_state("readonly")
    elif selected_profile == "Position sub 4":
        crop_top_var.set("0.24558")
        crop_bottom_var.set("0.0746562")
        crop_left_var.set("0.174393")
        crop_right_var.set("0.83223")
        set_entries_state("readonly")
    elif selected_profile == "custom":
        set_entries_state("normal")
    else:
        crop_top_var.set("0")
        crop_bottom_var.set("0")
        crop_left_var.set("0")
        crop_right_var.set("0")
        set_entries_state("readonly")


# Function to change the state of input cells
def set_entries_state(state):
    entry_crop_top.config(state=state)
    entry_crop_bottom.config(state=state)
    entry_crop_left.config(state=state)
    entry_crop_right.config(state=state)


# The function checks that the input is only numbers and dots.
def validate_float_input(action, value):
    if action != "1":  # No need to add characters
        return True
    return value.replace(".", "", 1).isdigit()


# Start GUI
def on_start_button_click():
    global stop_flag, log_file_path
    stop_flag = False  # Reset flag when starting new process
    file_sub = subtitle_entry.get()
    images_dirr = images_entry.get()

    delete_raw_texts = (
        delete_raw_texts_var.get()
    )  # Make sure this variable is declared first
    delete_texts = delete_texts_var.get()
    nen_raw_texts = nen_raw_texts_var.get()

    # Check input information
    if not file_sub or not images_dirr:
        log_message("Please enter complete information...")
        messagebox.showwarning("Warning", "Please enter complete information.")
        return

    save_config(
        folder_id, path_VSF, OCR_Text, cmd_vsf, delete_raw_texts, delete_texts, nen_raw_texts
    )  # Save configuration on start

    # Name the log file based on the subtitle file name
    log_file_path = file_sub if file_sub.endswith(".srt") else f"{file_sub}.srt"
    log_file_path = log_file_path.replace(".srt", ".log")  # Change the extension to .log

    # Write new starting line to log file
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write("=== STARTING NEW SESSION ===\n")

    log_message("Start processing...")

    # Disable Start button, enable Stop button
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    VSF_button.config(state=tk.DISABLED)
    # Activate the Stop button when the process starts
    progress_bar["value"] = 0

    threading.Thread(
        target=start_processing,
        args=(
            file_sub,
            images_dirr,
            delete_raw_texts,
            delete_texts,
            nen_raw_texts,
            progress_callback,
        ),
    ).start()


# Progress bar function
def progress_callback():
    progress_bar["value"] = (completed_scans / total_images) * 100
    root.update_idletasks()


# Function to select folder containing images
def choose_images_directory(entry_images_dir):
    images_dirr = filedialog.askdirectory(title="Select the folder containing the images")
    if images_dirr:  # Check if user has selected folder
        entry_images_dir.delete(0, tk.END)
        entry_images_dir.insert(0, images_dirr)
        log_message(f"Selected folder path: {images_dirr}")  # Debug
    else:
        log_message("No folder selected.")


# Logging function to file
def log_message(message):
    global log_text, log_file_path  # Make sure to use global variables
    log_text.config(state="normal")  # Allows temporary editing
    log_text.insert(tk.END, message + "\n")  # Add new notification
    log_text.see(tk.END)  # Scroll down to the bottom
    log_text.config(state="disabled")  # Lock to avoid editing

    # Log to file
    if log_file_path:
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")


# Add checkbox to delete raw_texts folder after completion
def create_gui():
    global root, entry_subtitle, subtitle_entry, entry_images_dir, progress_bar, start_button, delete_raw_texts_var, delete_texts_var, nen_raw_texts_var, log_text

    # Add Text widget to display log
    log_frame = tk.Frame(root)
    log_frame.pack(pady=(0, 5), fill="both", expand=True)
    log_text = tk.Text(
        log_frame, height=5, wrap="word", state="disabled", bg="#0C0C0C", fg="#CCCCCC"
    )
    log_text.pack(fill="both", expand=True, padx=5, pady=5)


# Function to select where to save subtitle file
def choose_subtitle_file(entry_subtitle):
    subtitle_file = filedialog.asksaveasfilename(
        defaultextension=".srt",
        filetypes=[("SRT files", "*.srt")],
        title="Save subtitle file",
    )
    if subtitle_file:
        entry_subtitle.delete(0, tk.END)
        entry_subtitle.insert(0, subtitle_file)
        log_message(f"Where to save the subtitles: {subtitle_file}")
    else:
        log_message("SAVE SUBTITLES IS REQUIRED.")



def choose_video_file(
    entry_video, entry_crop_left, entry_crop_right, entry_crop_top, entry_crop_bottom, subtitle_entry, progress_bar, root, log_message
):
    video_file = filedialog.askopenfilename(
        filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")],
        title="Select video to process",
    )
    if not video_file:
        log_message("No videos selected.")
        return

    entry_video.delete(0, tk.END)
    entry_video.insert(0, video_file)
    log_message(f"Selected video: {video_file}")




    subtitle_file = "../Subtitle_Output/output_subtitle.srt"
    subtitle_entry.delete(0, tk.END)
    subtitle_entry.insert(0, subtitle_file)

    try:
        crop_left = float(entry_crop_left.get())
        crop_right = float(entry_crop_right.get())
        crop_top = float(entry_crop_top.get())
        crop_bottom = float(entry_crop_bottom.get())
    except ValueError:
        log_message("Input error: Please enter correct numeric values ​​for crop parameters.")
        messagebox.showerror("Input error", "Please enter correct numeric values ​​for crop parameters.")
        return

    videosubfinder_path = (path_VSF)  # Make sure this path is correct
   

    if not os.path.exists(videosubfinder_path):
        log_message(f"Error: VideoSubFinder not found at: {videosubfinder_path}")
        messagebox.showerror("Error", f"VideoSubFinder not found at: {videosubfinder_path}")
        return



    output_file = "../Video_Output"
    

   
    command = [
        f"{videosubfinder_path}",
        "-c", "-r", (cmd_vsf),
        "-i", video_file,
        "-o", output_file,
        "-te", str(crop_top),        "-be", str(crop_bottom),
        "-le", str(crop_left),
        "-re", str(crop_right),
    ]

    try:
        log_message(f"Running command VideoSubFinder: {' '.join(command)}")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break

            if line:
                line = line.strip()
                log_message(line)

                match = re.search(r"%(\d+)", line) #Search for % followed by number
                if match:
                    try:
                        percentage = int(match.group(1))
                        progress_bar["value"] = percentage
                        root.update_idletasks()
                    except ValueError:
                        log_message("Percentage conversion error")

            time.sleep(0.05) #Reduce sleep time for faster updates while still saving CPU.

        stderr_output = process.stderr.read()
        if stderr_output:
            log_message(f"Error VideoSuoutput_filebFinder: {stderr_output}")
            messagebox.showerror("Error", f"Video processing failed: {stderr_output}")

        returncode = process.wait()
        #if returncode != 0:
            #log_message(f"VideoSubFinder exited with code: {returncode}")
            #messagebox.showerror("Error", f"VideoSubFinder exited with code: {returncode}")
            #return # Stop the function if there is an error

        log_message("Video processing is complete..")



            

        
        Video_Output_folder = output_file
        txt_images_folder = os.path.join(Video_Output_folder , (OCR_Text))



        if os.path.exists(txt_images_folder):
            images_entry.delete(0, "end")
            images_entry.insert(0, txt_images_folder)
        else:
            log_message("Error: (OCR_Text) directory does not exist.")
            messagebox.showerror("Error", "(OCR_Text)( directory does not exist.")
        
    except FileNotFoundError:
        log_message(f"Error: File not found: {videosubfinder_path}")
        messagebox.showerror("Error", f"VideoSubFinder not found at: {videosubfinder_path}")
    except Exception as e:
        log_message(f"System error: {e}")
        messagebox.showerror("System error", f"Command cannot be executed: {e}")
        
# Program exit function
def on_exit():
    if messagebox.askokcancel(
        "Confirm exit", "Are you sure you want to exit the program??"
    ):
        log_message("The program has been closed..")  # Log when user exits
        root.destroy()  # Close program


# =============================================================================================
root = tk.Tk()
root.title("Google Docs OCR V3.0.4")
root.geometry("622x578")
root.resizable(False, False)
button_width = 20

# Subtitle name
subtitle_frame = tk.Frame(root)
subtitle_frame.pack(pady=5, fill="x")  # Set frame to contain widgets on the same row
tk.Label(subtitle_frame, text="Subtitle file name:").pack(side="left", padx=5)
subtitle_entry = tk.Entry(subtitle_frame, width=58)  # Reduce width size to fit
subtitle_entry.pack(side="left", padx=5)

tk.Button(
    subtitle_frame,
    text="Select where to save sub",
    width=button_width,
    command=lambda: choose_subtitle_file(subtitle_entry),
).pack(side="right", padx=5)

# Image folder
images_frame = tk.Frame(root)
images_frame.pack(pady=5, fill="x")  # Set frame to contain widgets on the same row
tk.Label(images_frame, text="Images folder:").pack(side="left", padx=5)
images_entry = tk.Entry(images_frame, width=59)  # Reduce the width of the Entry to fit the frame.
images_entry.pack(side="left", padx=5)

tk.Button(
    images_frame,
    text="Select images folder",
    width=button_width,
    command=lambda: choose_images_directory(images_entry),
).pack(side="right", padx=5)

# Video input frame
video_frame = tk.Frame(root)
video_frame.pack(
    pady=(0, 1), fill="x"
)  # Set frame to contain widgets on the same row
tk.Label(video_frame, text="File video:").pack(side="left", padx=5)

entry_video = tk.Entry(video_frame, width=59)  # Reduce the width of the Entry to fit the frame.
entry_video.pack(side="left", padx=5)

# Video crop options
crop_frame = tk.Frame(root)
crop_frame.pack(padx=10, pady=5, fill="x")

# Add labels and input fields to crop
crop_label = tk.Label(crop_frame, text="Crop (Top, Bottom, Left, Right):")
crop_label.pack(side="left", padx=5)

# Variables store crop values
crop_top_var = tk.StringVar(value="0")
crop_bottom_var = tk.StringVar(value="0")
crop_left_var = tk.StringVar(value="0")
crop_right_var = tk.StringVar(value="0")

validate_command = (root.register(validate_float_input), "%d", "%P")

entry_crop_top = tk.Entry(
    crop_frame,
    textvariable=crop_top_var,
    width=10,
    state="readonly",
    validate="key",
    validatecommand=validate_command,
)
entry_crop_top.pack(side="left", padx=2)

entry_crop_bottom = tk.Entry(
    crop_frame,
    textvariable=crop_bottom_var,
    width=10,
    state="readonly",
    validate="key",
    validatecommand=validate_command,
)
entry_crop_bottom.pack(side="left", padx=2)

entry_crop_left = tk.Entry(
    crop_frame,
    textvariable=crop_left_var,
    width=10,
    state="readonly",
    validate="key",
    validatecommand=validate_command,
)
entry_crop_left.pack(side="left", padx=2)

entry_crop_right = tk.Entry(
    crop_frame,
    textvariable=crop_right_var,
    width=10,
    state="readonly",
    validate="key",
    validatecommand=validate_command,
)
entry_crop_right.pack(side="left", padx=2)

# Add Combobox to select profile
profile_combobox = ttk.Combobox(
    crop_frame,
    values=["Position sub 1", "Position sub 2", "Position sub 3", "Position sub 4", "custom"],
    state="readonly",
)
profile_combobox.pack(side="left", padx=5)
profile_combobox.set("Position sub 1")  # Set default value
profile_combobox.bind("<<ComboboxSelected>>", update_crop_values)
update_crop_values(None)  # Call function with argument None

folder_id, path_VSF, OCR_Text, cmd_vsf, delete_raw_texts, delete_texts, nen_raw_texts = load_config()
# Checkbox Options
delete_raw_texts_var = tk.BooleanVar(value=True if delete_raw_texts else False)
delete_texts_var = tk.BooleanVar(value=True if delete_texts else False)
nen_raw_texts_var = tk.BooleanVar(value=True if nen_raw_texts else False)
delete_options_frame = tk.Frame(root)
delete_options_frame.pack(pady=(0, 1), fill="x")  # Set frame

# Checkbox for delete folder option raw_texts
tk.Checkbutton(
    delete_options_frame,
    text="Delete the raw_texts folder when done",
    variable=delete_raw_texts_var,
    anchor="w",
).pack(side="left", padx=5)

# Checkbox for option to delete texts folder
tk.Checkbutton(
    delete_options_frame,
    text="Delete the texts folder when done",
    variable=delete_texts_var,
    anchor="w",
).pack(side="left", padx=5)

# Checkbox for option to compress raw_texts folder
tk.Checkbutton(
    delete_options_frame,
    text="Compress raw_texts folder",
    variable=nen_raw_texts_var,
    anchor="w",
).pack(side="left", padx=5)

# Create a Frame containing Start and Stop buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=(0, 5))
# Add Start button to Frame
start_button = tk.Button(
    button_frame,
    text="Start",
    width=button_width,
    command=on_start_button_click,
    bg="#05ed75",
)
start_button.pack(side="left", padx=20)
# Add Stop button to Frame
stop_button = tk.Button(
    button_frame,
    text="Stop",
    width=button_width,
    command=stop_processing,
    state=tk.DISABLED,
)
stop_button.pack(side="left", padx=20)

VSF_button = tk.Button(
    video_frame,
    text="Run VideoSubFinder",
    width=button_width,
    command=lambda: choose_video_file(
        entry_video,
        entry_crop_left,
        entry_crop_right,
        entry_crop_top,
        entry_crop_bottom,
        subtitle_entry,
        progress_bar, #Add progress_bar
        root, #Add root
        log_message #Add log_message
    ),
)
VSF_button.pack(side="right", padx=5)

progress_bar = ttk.Progressbar(
    root, orient="horizontal", length=616, mode="determinate"
)
progress_bar.pack(pady=(1, 0))

if __name__ == "__main__":
    folder_id, path_VSF, OCR_Text, cmd_vsf, delete_raw_texts, delete_texts, nen_raw_texts = load_config()
    create_gui()
    log_message(
        "|====================IMPORTANT ATTENTION====================|\n\nPlease pre-configure API with your google account.\nThen download credentials.json and put it in the same program folder.. \n\n|===========================================================|\n\nprogrammer By  Telegram : blackdenhac & Youtube : MrGamesKingPro\n\n"
    )
    # Attach the window-close event to the validation function
    root.protocol("WM_DELETE_WINDOW", on_exit)
    root.mainloop()
