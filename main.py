import os
import tkinter
import pyocr
import pyautogui
import configparser
from datetime import datetime
from PIL import Image, ImageEnhance, ImageTk

iniFile=configparser.ConfigParser()
iniFile.read('resources/appConfig.ini', 'UTF-8')

# Path setting
# TESSERACT_PATH = iniFile.get('env', 'TESSERACT_PATH')
# TESSDATA_PATH = iniFile.get('env', 'TESSDATA_PATH')
TESSERACT_PATH = 'C:\Program Files\Tesseract-OCR'
TESSDATA_PATH = 'C:\Program Files\Tesseract-OCR\\tessdata'

os.environ['PATH'] += os.pathsep + TESSERACT_PATH
os.environ['TESSDATA_PREFIX'] = TESSDATA_PATH

# OCR obtained
tools = pyocr.get_available_tools()
tool = tools[0]

# OCR setting
builder = pyocr.builders.TextBuilder(tesseract_layout=6)

RESIZE_RATIO = 1 # Reduction ratio regulation

# Event when starting drag
def start_point_get(event):
    global start_x, start_y # Declare for writing global variables
    canvas1.delete('rect1') # Delete if 'rect1' already exists

    # Draw a rectangle on canvas1
    canvas1.create_rectangle(event.x,
                            event.y,
                            event.x + 1,
                            event.y + 1,
                            outline='red',
                            tag='rect1')
    
    # Store coordinate into global variables
    start_x, start_y = event.x, event.y


# Event while dragging
def rect_drawing(event):
    # If cursor goes out of range while dragging
    if event.x < 0:
        end_x = 0
    else:
        end_x = min(img_resized.width, event.x)
    
    if event.y < 0:
        end_y = 0
    else:
        end_y = min(img_resized.height, event.y)

    # Redraw rect1 
    canvas1.coords('rect1', start_x, start_y, end_x, end_y)


# Event when releasing
def release_action(event):
    # Obtain rect1's coordinate reverted scale
    start_x, start_y, end_x, end_y = [
        round(n * RESIZE_RATIO) for n in canvas1.coords('rect1')
    ]

    cropImag = img.crop(box=(start_x, start_y, end_x, end_y))

    nowDate=datetime.now().strftime('%Y%m%d')
    currentDirectory=os.getcwd()
    tempDir=os.path.join(currentDirectory, nowDate, 'tmp')
    os.makedirs(tempDir, exist_ok=True)
    # Image file name
    pngFileName=os.path.join(tempDir, nowDate+'.png')

    # Save image
    cropImag.save(pngFileName)
    # Open image
    reading = Image.open(pngFileName)

    # Image processing
    img_g = reading.convert('L') # Gray convertion
    enhancer = ImageEnhance.Contrast(img_g) # Increase contrast
    img_con = enhancer.enhance(2.0) # Increase contrast

    lang = pyautogui.confirm(text='Which langauage?', title="Language Select", buttons=['EN', 'JP'])

    readText = tool.image_to_string(img_con, lang='eng', builder=builder)
    list = readText.split(' ')

    if lang == 'JP':
        # Read japanese texts on image by OCR, then extract as strings
        readText = tool.image_to_string(img_con, lang='jpn', builder=builder)
        # Delete half space 
        readText = readText.replace(' ', '')

    # Copy on clipboard
    # root.clipboard_append(readText)

    # Diplay strings by spritz
    display_spritz(list)

# Extract and show strings on dialog
def display_spritz(list):
    for i in range(len(list)):
        pyautogui.alert(list[i])


# Main process
if __name__ == '__main__':
    checkloop = 0

    if checkloop == 0:
        pyautogui.alert(text='Start to read?', title='', button='OK')

    root = tkinter.Tk()
    # Always display tkinter window at topmost
    # root.attributes('-topmost', True) 
    
    if checkloop > 0:
        loop = pyautogui.confirm(text='Continue?', title='', buttons=['Yes', 'No'])
        if loop == 'No':
            root.quit()

    # Obtain screenshot from main display
    img = pyautogui.screenshot()
    # Resize image
    img_resized = img.resize(size=(int(img.width / RESIZE_RATIO),
                                    int(img.height / RESIZE_RATIO)),
                            resample=Image.BILINEAR)

    # Convert image for tkinter
    img_tk = ImageTk.PhotoImage(img_resized)

    # Draw Canvas widget
    canvas1 = tkinter.Canvas(root,
                            bg='black',
                            width=img_resized.width,
                            height=img_resized.height)
    
    # Draw image obtained in Canvas widget
    canvas1.create_image(0, 0, image=img_tk, anchor=tkinter.NW)


    # Set events 
    canvas1.pack()
    canvas1.bind('<ButtonPress-1>', start_point_get)
    canvas1.bind('<Button1-Motion>', rect_drawing)
    canvas1.bind('<ButtonRelease-1>', release_action)
    print(checkloop)

    checkloop+=1
    root.mainloop()