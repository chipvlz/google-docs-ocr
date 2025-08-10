# Google Docs OCR V3.0.4 #

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

1 - تحميل وتتثبيث برنامج بايثون نسخة 3.9 او احدث اصدار
https://www.python.org/downloads/windows/

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
2 - تحميل ملف  Credentials.json
كيفة الحصول على ملف Credentials.json شاهد هذا الفيديو
https://www.youtube.com/watch?v=sQPmefCATbA

اذا لديك الملفين مسبقا Credentials.json و token.json
ضعهم في المجلد البرنامج

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

3 - تحميل ملف  VideoSubFinder
https://www.videohelp.com/software/VideoSubFinder

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

4 - تثبيث المكتبة Install pip library.bat
إذهب الى المجلد Support


# # # # # # # # # # # # إعدادات  Config # # # # # # # # # # # #
5 - افتح ملف Config.ini ثم قم بتعديله

- folder_id = "حصول على معرف المجلد من حساب جوجل درايف (https://drive.google.com)"
مثال : https://drive.google.com/drive/u/0/folders/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

- - - - - - - - - - - - - -  

- path_vsf  = "المسار الموجود فيه برنامج (VideoSubFinderWXW.exe)"

- - - - - - - - - - - - - -  
- cmd_vsf = "نافذة الأوامر VideoSubFinder"

-ccti : إنشاء صور نصية نظيفة
-uc : يستخدم وحدة معالجة الرسوميات CUDA بدلاً من وحدة المعالجة المركزية. يدعم فقط بعد بطاقة الرسوميات
-s  : التوقيت البداية الفيديو  =  0:00:00:000 
-e  : توقيت نهاية الفيديو

- - - - - - - - - - - - - -  

- ocr_text = إختر مجلد الصور التي سيتم تحويلها إلى نص (RGBImages أو TXTImages)
RGBImages : الصور الأصلية بدون تنظيف النص
TXTImages : الصور مع النص نظيف

- - اذا أردت تحويل الصور الى نص أصلية بالخلفية  بدون تنضيف النص اختر إعدادات التالية:
ocr_text = RGBImages
cmd_vsf = -s 0:00:00:000

- - اذا أردت تحويل الصور الى نص بدون الخلفية ونص نظيف اختر إعدادات التالية:
ocr_text = TXTImages
cmd_vsf = -ccti

- - اذا أردت إحتفاظ بالمجلدين معا "RGBImages" و "TXTImages"  اختر إعدادات التالية:
ocr_text = RGBImages
cmd_vsf = -ccti

- - - - - - - - - - - - - -  
اذا أردت حذف مجلد raw_texts اختر True أو False
-  delete_raw_texts = "True or False"

اذا أردت حذف مجلد texts اختر True أو False
-  delete_texts = "True or False"

اذا أردت ضغط مجلد نصوص raw_texts اختر True أو False
-  nen_raw_texts = "True or False (Compress file raw_texts)" 

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

6 - تشغيل  البرنامج "Google_Docs_OCR.bat" 

# # # # # # # # # # # # إعدادات وضعية الترجمة  # # # # # # # # # # # #


7 - هناك 5 خيارات لتعديل موضع الترجمة.

Position 1
مثال : https://i.imgur.com/szY9MaW.jpeg

Position 2
مثال : https://i.imgur.com/gFoMoF3.jpeg

Position 3
مثال : https://i.imgur.com/Pmw4gyT.jpeg

Position 4
مثال : https://i.imgur.com/nu9XgNQ.jpeg

Custom
هذا الخيار لتعديل موضع الترجمة يدويا. اذهب الىبرنامج  VideoSubFinder وافتح اي فيديو
ثم اضبط وضعية الترجمة واحفظ الاعدادات بصيغة .cfg ثم افتح ملف في Notepad++
ابحث عن هذه الاسطر وانسخ الاعدادات.

- bottom_video_image_percent_end = 0
- top_video_image_percent_end = 0
- left_video_image_percent_end = 0
- right_video_image_percent_end = 0

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  
8 - اضغط على  Start وسجل بحساب جوجل خاص بك فقط مرة واحدة . اذ لديك ملف "token.json" مسبقا  لن تحتاج عملية التسجيل




