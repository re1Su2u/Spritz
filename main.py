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

# OCR obtaining
tools = pyocr.get_available_tools()
tool = tools[0]

# OCR setting
builder = pyocr.builders.TextBuilder(tesseract_layout=6)

RESIZE_RATIO = 1 # Reduction ratio regulation

start_flag = False

# Event when starting to drag
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
    
    # Store coordinates into global variables
    start_x, start_y = event.x, event.y


# Event while dragging
def rect_drawing(event):
    # If a cursor goes out of range while dragging
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
    # Obtain a rect1's coordinate reverted scale
    start_x, start_y, end_x, end_y = [
        round(n * RESIZE_RATIO) for n in canvas1.coords('rect1')
    ]

    cropImag = img.crop(box=(start_x, start_y, end_x, end_y))

    now_date=datetime.now().strftime('%Y%m%d')
    current_dir=os.getcwd()
    tmp_dir=os.path.join(current_dir, now_date, 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    # Image file name
    png_file_name=os.path.join(tmp_dir, now_date+'.png')

    # Save an image
    cropImag.save(png_file_name)
    # Open an image
    reading = Image.open(png_file_name)

    # Image processing
    img_g = reading.convert('L') # Gray convertion
    enhancer = ImageEnhance.Contrast(img_g) # Increase contrast
    img_con = enhancer.enhance(2.0) # Increase contrast

    readText = tool.image_to_string(img_con, lang='eng', builder=builder)
    list = readText.split(' ')

    # Select language
    lang = pyautogui.confirm(text='Which langauage will you read?', title="Language Select", buttons=['EN', 'JP'])

    if lang == 'JP':
        # Read japanese texts on image by OCR, then extract as strings
        readText = tool.image_to_string(img_con, lang='jpn', builder=builder)
        # Delete half spaces
        readText = readText.replace(' ', '')

    # Copy on clipboard
    # tk_main.clipboard_append(readText)

    # Diplay strings by spritz
    display_spritz(list)

    continue_flg = pyautogui.confirm(text="Next?", title="Continue confirm", buttons=["Yes", "No"])

    if continue_flg == "No":
        tk_main.quit()

# Extract and show strings on dialog
def display_spritz(list):
    tk_sub = tkinter.Tk()
    canvas2 = tkinter.Canvas(tk_sub,
                            # bg="white",
                            width=100,
                            height=100)
    canvas2.pack()
    string = tkinter.Label(canvas2, text="", fg="black", anchor=tkinter.CENTER)
    string.pack()

    for i in range(len(list)):
        # pyautogui.alert(list[i])
        string.config(text=list[i])
        string.pack()
        tk_sub.after(100)



# Main process
if __name__ == '__main__':
    count_loop = 0

    pyautogui.alert(text='Choose the window to screenshot, then press "OK"', title='Window Select', button='OK')

    # Create a main window instance
    tk_main = tkinter.Tk()
    # Always display a tkinter window at topmost
    # tk_main.attributes('-topmost', True) 

    # Obtain a screenshot from main display
    img = pyautogui.screenshot()
    # Resize an image
    img_resized = img.resize(size=(int(img.width / RESIZE_RATIO),
                                    int(img.height / RESIZE_RATIO)),
                            resample=Image.BILINEAR)

    # Convert an image for tkinter
    img_tk = ImageTk.PhotoImage(img_resized)

    # Draw a canvas widget
    canvas1 = tkinter.Canvas(tk_main,
                            bg='black',
                            width=img_resized.width,
                            height=img_resized.height)
    
    # Draw an image obtained in Canvas widget
    canvas1.create_image(0, 0, image=img_tk, anchor=tkinter.NW)

    # Set events 
    canvas1.pack()
    canvas1.bind('<ButtonPress-1>', start_point_get)
    canvas1.bind('<Button1-Motion>', rect_drawing)
    canvas1.bind('<ButtonRelease-1>', release_action)

    count_loop+=1
    tk_main.mainloop()