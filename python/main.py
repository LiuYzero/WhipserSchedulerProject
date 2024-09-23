# This is a sample Python script.
# -*-coding:utf-8-*-
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import subprocess
import time

import whisper
import shutil
import os
import psycopg2
import pyautogui as pag

basePath = "D:/x/WhipserSchedulerProject/"

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def work():
    downlaod_videos()

    # filenames = list_mp4_file()
    # for filename in filenames:
    #     print (filename)
    #     init_temp(basePath + filename)
    #     video2audio()
    #     audio2captionsV2()
    #     save2db(filename)
    #     clean_temp()

def downlaod_videos():
    find_one_video("https://space.bilibili.com/1447361032/video")
    download_one_video()


def find_one_video(url):
    open_chrome_tab(url)
    location_play = pag_locate_pic('pics/play_pic.png')
    pag_click(location_play[0]+location_play[2]/2,location_play[1]+location_play[3]/2-200)
    time.sleep(5)

def open_chrome_tab(url):
    powershell_commands = [
        "cd D:/x/WhipserSchedulerProject/python/application;./Chrome.lnk "+url
    ]
    print(powershell_commands)

    for cmd in powershell_commands:
        result = subprocess.run(["powershell","-Command", cmd],capture_output=True, text=True)
        print(f"Command:{cmd}\n")
        print(result.stdout)
        print("="*50)
    time.sleep(5)

def download_one_video():
    if(download_link_pic()):
        return True
    else:
        if(downloader_pic()):
            download_link_pic()
            return True
    return False



    # location_pick_up = pag_locate_pic('pics/pick_up_pic.png')

def downloader_pic():
    location_downloader = pag_locate_pic('pics/downloader_pic.png')
    if (location_downloader[0] != 0):
        print("find downloader")
        pag_click(location_downloader[0] + location_downloader[2] / 2,
                  location_downloader[1] + location_downloader[3] / 2)
        time.sleep(3)
        return True
    return False

def download_link_pic():
    location_download_link = pag_locate_pic('pics/download_link_pic.png')
    if (location_download_link[0] != 0):
        pag_click(location_download_link[0] + location_download_link[2] / 2 + 40,
                  location_download_link[1] + location_download_link[3] / 2)
        return True
    return False

def pag_click(x,y):
    pag.moveTo(x,y)
    time.sleep(1)
    pag.click()
    time.sleep(1)


def pag_locate_pic(pic):
    """"
    download_link(896,1194)
    """
    try:
        box =  pag.locateOnScreen(pic)
        print (box)
        return (box[0],box[1],box[2],box[3])
    except Exception as e:
        print ((0,0,0,0))
        return (0,0,0,0)

def list_mp4_file():
    mp4_files = []
    for filename in os.listdir(basePath):
        if(filename.endswith(".mp4")):
            mp4_files.append(filename)
    return mp4_files

def init_temp(video_path):
    clean_temp()
    temp_path = basePath+"temp"
    os.makedirs(temp_path)
    shutil.move(video_path, temp_path+"/sample.mp4")

def clean_temp():
    try:
        shutil.rmtree(basePath+"temp")
    except Exception as e:
        print (e)



def video2audio():
    tempPath = basePath+"temp"
    powershell_commands = [
        "cd "+tempPath+";ffmpeg -i sample.mp4 sample.mp3"
    ]
    print(powershell_commands)

    for cmd in powershell_commands:
        result = subprocess.run(["powershell","-Command", cmd],capture_output=True, text=True)
        print(f"Command:{cmd}\n")
        print(result.stdout)
        print("="*50)

def audio2catpions():
    model = whisper.load_model("base")
    result = model.transcribe(basePath+"temp/sample.mp3", language="Chinese")
    captions = segment_format(result)
    write2file(captions)


def audio2captionsV2():
    tempPath = basePath + "temp"
    powershell_commands = [
        "cd "+tempPath+";whisper --model medium --language Chinese sample.mp3"
    ]
    print (powershell_commands)

    for cmd in powershell_commands:
        filePath = basePath+"temp/whisper_captions.txt"
        with open(filePath,"w", encoding="utf-8") as f:
            result = subprocess.run(["powershell","-Command", cmd],capture_output=False, text=True, stdout=f, stderr=None,encoding="utf-8", errors='ignore')
            print(f"Command:{cmd}\n")
            print(result.stdout)
            print("="*50)
def segment_format(result):
    captions = []
    for segment in result['segments']:
        start_str = time_format(segment['start'])
        end_str = time_format(segment['end'])
        content = segment['text']
        caption = "[%s---%s]%s" % (start_str, end_str, content)
        print (caption)
        captions.append(caption)
    return captions

def time_format(seconds_str):
    milliseconds=int(str(seconds_str).split('.')[1][0:1])
    seconds = int(seconds_str)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    time_format_str = "%02d:%02d:%02d.%02d" % (hours, minutes, seconds,milliseconds)
    return time_format_str

def write2file(captions):
    filePath = basePath + "temp/whisper_captions.txt"
    with open(filePath,"w", encoding="utf-8") as whisper_captions:
        for caption in captions:
            whisper_captions.write(caption+"\n")

def save2db(filename):
    captions = []
    filePath = basePath + "temp/whisper_captions.txt"
    with open(filePath,"r", encoding="utf-8") as caption_file:
       for line in caption_file:
           captions.append(line.replace("\n",""))
    conn = None
    try:
        conn = psycopg2.connect(database='db_paas', user='paas', password='paas', host='192.168.1.110', port='5432')
        cur = conn.cursor()
        for caption in captions:
            if caption:
                if caption.find("'") == -1:
                    tmpsql = "INSERT INTO public.video_caption(video, caption) VALUES ('%s','%s');" % (filename, caption)
                    print (tmpsql)
                    cur.execute(tmpsql)
        cur.close()
    except psycopg2.DatabaseError as e:
        print (e)
        None
    finally:
        if conn:
            conn.commit()
            conn.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    work()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
