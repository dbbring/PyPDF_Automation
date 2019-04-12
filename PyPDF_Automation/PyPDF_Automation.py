
# Tesseract must be part of System Path Variables as name: tesseract
# ImagieMajik and Ghost scrip should make its own System Enviroment Variable
# Image majik - https://www.imagemagick.org/script/download.php
# Tesseract - https://github.com/tesseract-ocr/tesseract/wiki/Downloads
# Ghost Script - https://www.ghostscript.com/download/gsdnld.html

from tika import parser as tikaParser
from PIL import Image as PI 
from wand.image import Image
from wand.color import Color
import pyocr
import pyocr.builders
import json
import os
import re
import imaplib
import email
import time

# Grab our Config Settings
with open('config.json', 'r') as configFile:
    config = json.load(configFile)

# Connect to Gmail
m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
m.login(config["emailAddress"], config["emailPassword"])


while True:
    print("Checking For New Emails....")
    m.select('inbox')
    result, data = m.uid('search', None, "(UNSEEN)") 
    newEmailList = data[0]
    # If our unread email list has anything in it check it for our attachment file
    if(len(newEmailList) > 0):
        if result == 'OK':
            for num in data[0].split():
                result, data = m.uid('fetch', num, '(RFC822)')
                if result == 'OK':
                    email_message = email.message_from_bytes(data[0][1])   
                    if(email_message.is_multipart()):
                        # Walk though message contents looking for a pdf 
                        for part in email_message.walk():
                            if(part.get_content_type() == 'application/pdf'):
                                name = part.get_param('name')
                                # Make sure our PDF is what we are looking for
                                if(name == config["pdfToBeParsed"]):

                                    f = open(name, 'wb')
                                    f.write(part.get_payload(decode=True))
                                    f.close()
                                    print("PDF Attachment Successfully Downloaded")   
                                    
                                    pdf = tikaParser.from_file(config["pdfToBeParsed"], 'http://localhost:9998/tika')
                                    rawPDF = pdf["content"]
                                    # Find the text not in an image and grab its position in the doc
                                    startPoint = re.search(config["findTextNotInImage"], rawPDF).start() + len(config["findTextNotInImage"])
                                    # Find end point given user input
                                    endPoint = startPoint + config["amountOfCharsAfterTxt"]
                                    # Slice and dice doc
                                    finalTextInDoc = rawPDF[startPoint:endPoint]
                                    # Strip all white space
                                    finalTextInDoc = finalTextInDoc.replace(' ', '')
                                    finalTextInDoc = finalTextInDoc.replace('\n', '')
                                    finalTextInDoc = finalTextInDoc.strip()

                                    # Use with here so GC will take of memory leaks
                                    with Image(filename=config["pdfToBeParsed"], resolution=900) as img:
                                        # get image size and set our crop position
                                        width, height = img.size
                                        left = width//4
                                        top = (height//4) - 200
                                        right = 3 * width//4
                                        bottom = 3 * height//4
                                        # Crop Image, set to PNG, make sure we have a white background so our OCR can clearly see what it needs
                                        img.crop(left, top, right, bottom)
                                        img.format = 'png'
                                        img.background_color = Color('white')
                                        img.alpha_channel = 'remove'
                                        img.save(filename=config["tempFileLocation"])

                                    # Get Tesseract
                                    tools = pyocr.get_available_tools()
                                    tool = tools[0]
                                    # Set our lang to English
                                    langs = tool.get_available_languages()
                                    lang = langs[0]
                                    # Parse our Image and give us back a String
                                    rawText = tool.image_to_string(PI.open(config["tempFileLocation"]), lang = lang, builder = pyocr.builders.TextBuilder())
                                    # Thanks to cropping, our code is within the first 10 Chars
                                    finalText = rawText[:10]
                                    # Clean it up just incase we have whitespace
                                    finalText = finalText.replace(' ','')
                                    finalText = finalText.replace('\n', '')
                                    finalText = finalText.strip()

                                    # JSONify it and get it out the door!
                                    jsonExport = {config["findTextNotInImage"]: finalTextInDoc, "text" : finalText}
                                    with open(config["exportJsonLocation"], 'w') as json_file:
                                      json.dump(jsonExport, json_file)

                                    # Janitor to isle umm 10101011? Clean up after ourselves...
                                    os.remove(config["tempFileLocation"])

    # Keep watching for new emails... 
    time.sleep(int(config["emailInterval"]))


















