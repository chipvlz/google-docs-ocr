# Google Docs OCR V3.0.4 #

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

1 - Download Python 3.9 or latest version
https://www.python.org/downloads/windows/

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
2 - Download Credentials.json
how to get the file "Credentials.json" Watch this video
https://www.youtube.com/watch?v=sQPmefCATbA

If you already have file "Credentials.json" or "Credentials.json" &  "token.json" 
Put them into the folder Program 

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

3 - Download VideoSubFinder
https://www.videohelp.com/software/VideoSubFinder

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

4 - Install pip library
Go to Folder Support

# # # # # # # # # # # # Settings Config  # # # # # # # # # # # #

5 - Open a file  Config.ini Then edit

- folder_id = "Get the folder ID from your Google Drive account (https://drive.google.com)"
Example : https://drive.google.com/drive/u/0/folders/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

- - - - - - - - - - - - - -  

- path_vsf = "The path in which the program is located (VideoSubFinderWXW.exe)"

- - - - - - - - - - - - - -  

- cmd_vsf = "Command-line VideoSubFinder"

-ccti : Create Cleared Text Images
-uc : Uses CUDA GPU instead of CPU . Only supports after graphics card
-s :  start time, default = 0:00:00:000 (in format hour:min:sec:milisec)
-e : end time, default = video length

- - - - - - - - - - - - - -  

- ocr_text = "The folder of images that will be ocr to convert them to text. (RGBImages or TXTImages)" 
RGBImages : Original Images without cleared
TXTImages :  Images with cleared Text

- - If you want to convert images to text without cleared, choose This is it settings : 
ocr_text = RGBImages
cmd_vsf = -s 0:00:00:000

- - If you want to convert Images with cleared Text, choose This is it settings : 
ocr_text = TXTImages
cmd_vsf = -ccti

- - If you want to keep both folders together "RGBImages" and "TXTImages" , choose This is it settings : 
ocr_text = RGBImages
cmd_vsf = -ccti

- - - - - - - - - - - - - -  
If you want delete raw_texts choose True or False
- delete_raw_texts = "True or False"

If you want delete texts choose True or False
- delete_texts = "True or False"

If you want Compress file raw_texts choose True or False
- nen_raw_texts = "True or False (Compress file raw_texts)" 

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

6 -  Run "Google_Docs_OCR.bat" 

# # # # # # # # # # # # Settings Position  # # # # # # # # # # # #

7 - You can compare the text position of the video by the images in the folder "Example"

There are 5 options to adjust the subtitle Position.

Position 1
example : https://i.imgur.com/szY9MaW.jpeg

Position 2
example : https://i.imgur.com/gFoMoF3.jpeg

Position 3
example : https://i.imgur.com/Pmw4gyT.jpeg

Position 4
example : https://i.imgur.com/nu9XgNQ.jpeg

Custom
This option is to manually adjust the position text. go to Program and run VideoSubFinder open any video 
Then set the subtitle position. and save Settings .cfg  Then open it a file in the Notepad++ 
Find these lines and copy the settings.

- bottom_video_image_percent_end = 0
- top_video_image_percent_end = 0
- left_video_image_percent_end = 0
- right_video_image_percent_end = 0

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

8 - Click on Start and login with google account (only for first time) If you don't have a file "token.json"




