import os
import tkinter
import pyocr
import pyautogui
import configparser
from datetime import datetime
from PIL import Image, ImageEnhance, ImageTk

iniFile=configparser.ConfigParser()
iniFile.read('resources/appConfig.ini', 'UTF-8')

# path setting
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

RESIZE_RATIO = 1 #reduction ratio regulation

# event when starting drag
def start_point_get(event):
    global start_x, start_y # declare for writing global variables
    canvas1.delete('rect1') # delete if 'rect1' already exists

    # draw a rectangle on canvas1
    canvas1.create_rectangle(event.x,
                            event.y,
                            event.x + 1,
                            event.y + 1,
                            outline='red',
                            tag='rect1')
    
    # store coordinate into global variables
    start_x, start_y = event.x, event.y


# event while dragging
def rect_drawing(event):
    # if cursor goes out of range while dragging
    if event.x < 0:
        end_x = 0
    else:
        end_x = min(img_resized.width, event.x)
    
    if event.y < 0:
        end_y = 0
    else:
        end_y = min(img_resized.height, event.y)

    # redraw rect1 
    canvas1.coords('rect1', start_x, start_y, end_x, end_y)


# event when releasing
def release_action(event):
    # obtain rect1's coordinate reverted scale
    start_x, start_y, end_x, end_y = [
        round(n * RESIZE_RATIO) for n in canvas1.coords('rect1')
    ]

    cropImag = img.crop(box=(start_x, start_y, end_x, end_y))

    nowDate=datetime.now().strftime('%Y%m%d')
    fileName=datetime.now().strftime('%Y%m%d%H%M%S')
    currentDirectory=os.getcwd()
    workDir=os.path.join(currentDirectory, nowDate)
    tempDir=os.path.join(currentDirectory, nowDate, 'tmp')
    os.makedirs(tempDir, exist_ok=True)
    # image file name
    pngFileName=os.path.join(tempDir, nowDate+'.png')

    # save image
    cropImag.save(pngFileName)
    # open image
    reading = Image.open(pngFileName)

    # image processing
    img_g = reading.convert('L') # Gray convertion
    enhancer = ImageEnhance.Contrast(img_g) # increase contrast
    img_con = enhancer.enhance(2.0) # increase contrast

    lan = pyautogui.confirm(text='Which langauage?', title="Language Select", buttons=['EN', 'JP'])

    readText = tool.image_to_string(img_con, lang='eng', builder=builder)
    list = readText.split(' ')

    pyautogui.alert(list[0])

    if lan == 'JP':
        # read japanese texts on image by OCR, then extract as string
        readText = tool.image_to_string(img_con, lang='jpn', builder=builder)
        # delete half space 
        readText = readText.replace(' ', '')

    # print("This is a text => \n"+readText)

    # copy on clipboard
    root.clipboard_append(readText)

    # output as text file  (separate into Japasene and English)
    # textFileJp=os.path.join(workDir, fileName+'jp.txt')
    # textFileEn=os.path.join(workDir, fileName+'.txt')
    # with open(textFileJp, mode='w') as f:
    #     f.write(readText)

    # with open(textFileEn, mode='w') as f:
    #     f.write(readText)

    # display on dialog
    # pyautogui.alert(readText)

    display_spritz(list)


def display_spritz(list):
    for i in range(len(list)):
        pyautogui.alert(list[i])


# main process
if __name__ == '__main__':
    cntloop = 0
    if cntloop == 0:
        pyautogui.alert(text='Ready to read?', title='', button='OK')

    # obtain screenshot from main display
    img = pyautogui.screenshot()
    # resize image
    img_resized = img.resize(size=(int(img.width / RESIZE_RATIO),
                                    int(img.height / RESIZE_RATIO)),
                            resample=Image.BILINEAR)
    
    root = tkinter.Tk()
    # always display tkinter window at topmost
    # root.attributes('-topmost', True) 

    # convert image for tkinter
    img_tk = ImageTk.PhotoImage(img_resized)

    # draw Canvas widget
    canvas1 = tkinter.Canvas(root,
                            bg='black',
                            width=img_resized.width,
                            height=img_resized.height)
    
    # draw image obtained in Canvas widget
    canvas1.create_image(0, 0, image=img_tk, anchor=tkinter.NW)

    # set events 
    canvas1.pack()
    canvas1.bind('<ButtonPress-1>', start_point_get)
    canvas1.bind('<Button1-Motion>', rect_drawing)
    canvas1.bind('<ButtonRelease-1>', release_action)
    cntloop += 1
    
    if cntloop > 0:
        loop = pyautogui.confirm(text='One more?', title='', buttons=['Yes', 'No'])
        if loop == 'Yes':
            root.mainloop()