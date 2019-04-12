# PyPDF Automation
PyPDF Automation is a simple library that connects to an Gmail account, and monitors that account for an incoming email containing a PDF.
Once the PDF is found PyPDF will extract all the text that the user specifies and use RegEx to find the word preceding the text you 
are looking for. Once found, PyPDF will extract the number of characters specified **after** the word. Then PyPDF will export what it has
found into a JSON file for another application to further process the information.

PyPDF Automation also uses OCR to digitally process text within images. PyPDF Automation uses the Apache Tika library to scrape the PDF
accurately. 

### Notes

You must enable less secure apps in the gmail account. For this reason, I highly recommend not using this library with a important secure email.
Instead, create a new email address, and send the PDF to that.

You must also have these dependencies installed in your OS:
- Image majik - https://www.imagemagick.org/script/download.php
- Tesseract - https://github.com/tesseract-ocr/tesseract/wiki/Downloads
- Ghost Script - https://www.ghostscript.com/download/gsdnld.html

**Please make sure Tesseract is a system path variable and has the name of tesseract**

Image Majik and Ghost Script should install themselves with system variables and the appropriate names.
