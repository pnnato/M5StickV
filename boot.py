import audio
import gc
import image
import lcd
import sensor
import sys
import time
import utime
import uos
import os
import KPU as kpu
from fpioa_manager import *
from machine import I2C
from Maix import I2S, GPIO
from machine import Timer, PWM
#
# initialize
#
lcd.init(freq=15000000)
lcd.rotation(2)

fm.register(board_info.LED_W, fm.fpioa.GPIO3)

led_w=GPIO(GPIO.GPIO3,GPIO.OUT)
led_w.value(1)


fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output

fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

wav_dev = I2S(I2S.DEVICE_0)

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!


clock = time.clock()
difference = 946652400      #Difference between 1970 and 2000
now = 1582677793          ##Always need update Epoch


def getTime(now):
    currentTime = utime.localtime(now - difference)
    return currentTime

def input_datetime(isButtonPressedA,get_year, get_month, get_day,get_hour,get_min,get_sec):
    sendValue = 0
    while(True):
        lcd.draw_string(25,55,"Y:%04d   M:%02d/12   D:%02d/31"%(get_year,get_month,get_day),lcd.RED, lcd.BLACK)
        lcd.draw_string(25,75,"H:%02d/23  m:%02d/59"%(get_hour,get_min),lcd.RED, lcd.BLACK)
        if but_b.value() == 0 and isButtonPressedB == 0:
            if isButtonPressedA == 0:
                get_month = get_month + 1
                sendValue = get_month
                if get_month == 13:
                    get_month = 1
                isButtonPressedB = 1
            elif isButtonPressedA == 1:
                get_day = get_day + 1
                sendValue = get_day
                if get_day == 32:
                    get_day = 1
                isButtonPressedB = 1
            elif isButtonPressedA == 2:
                get_hour = get_hour + 1
                sendValue = get_hour
                if get_hour == 24:
                    get_hour = 0
                isButtonPressedB = 1
            elif isButtonPressedA == 3:
                get_min = get_min + 5
                sendValue = get_min
                if get_min == 60:
                    get_min = 0
                isButtonPressedB = 1

        if but_a.value() == 0:
            isButtonPressedA = isButtonPressedA + 1
            print("Press A: " + str(isButtonPressedA))
            time.sleep(1)
            lcd.draw_string(0,0,"Ok", lcd.WHITE, lcd.BLACK)
            return isButtonPressedA, sendValue
            #break
        if but_b.value() == 1:
            isButtonPressedB = 0

def findMaxIDinDir(dirname):
    larNum = -1
    try:
        dirList = uos.listdir(dirname)
        for fileName in dirList:
            currNum = int(fileName)
            if currNum > larNum:
                larNum = currNum
        return larNum
    except:
        print("No file")
        return 0

def findMaxIDinFilename(dirPath):
    latestTime = 0
    try:
        fileList = uos.listdir(dirPath)
        for fileName in fileList:
            currNum = int(fileName.split(".jpg")[0])
            if currNum > latestTime:
                latestTime = currNum
        return latestTime
    except:
        return 0

def findLastFileName(lastDir, lastTime):
    t = (int(str(lastDir)[0:4]),int(str(lastDir)[4:6]), int(str(lastDir)[6:8]), int(lastTime[0:2]), int(lastTime[2:4]),int(lastTime[4:6]),0,362)

    local_time = utime.mktime(t)
    return local_time

def fileFormatCheck(year,month,mday,hour,minute,second, weekday, yesterday):
    if(month < 10):
        month_edit = "0" + str(month)
    else:
        month_edit = str(month)

    if(mday < 10):
        mday_edit = "0" + str(mday)
    else:
        mday_edit = str(mday)

    if(hour < 10):
        hour_edit = "0" + str(hour)
    else:
        hour_edit = str(hour)

    if(minute < 10):
        minute_edit = "0" + str(minute)
    else:
        minute_edit = str(minute)

    if(second < 10):
        second_edit = "0" + str(second)
    else:
        second_edit = str(second)

    file_date = str(year) + month_edit +  mday_edit
    file_time = hour_edit + minute_edit + second_edit
    return file_date, file_time

def play_sound(filename):
    try:
        player = audio.Audio(path = filename)
        player.volume(10)
        wav_info = player.play_process(wav_dev)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        spk_sd.value(1)
        while True:
            ret = player.play()
            if ret == None:
                break
            elif ret==0:
                break
        player.finish()
        spk_sd.value(0)
    except:
        pass

def initialize_camera():
    err_counter = 0
    while 1:
        try:
            sensor.reset() #Reset sensor may failed, let's try some times
            break
        except:
            err_counter = err_counter + 1
            if err_counter == 20:
                lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Sensor Init Failed", lcd.WHITE, lcd.RED)
            time.sleep(0.1)
            continue

    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.VGA)
    sensor.set_windowing((640,480))
    sensor.skip_frames(time=2000)
    sensor.run(1)

try:
    img = image.Image("/sd/tomatoScreen2.jpg")
    lcd.display(img)
except:
    lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Cannot find start.jpg", lcd.WHITE, lcd.RED)

time.sleep(2)

initialize_camera()

currentDirectory = 1
currentImage = 1

if "sd" not in os.listdir("/"):
    lcd.draw_string(lcd.width()//2-96,lcd.height()//2-4, "Error: Cannot read SD Card", lcd.WHITE, lcd.RED)

try:
    os.mkdir("/sd/train")
except Exception as e:
    pass

try:
    lastDir = findMaxIDinDir("/sd/train")
    dirPath = "/sd/train/" + str(lastDir)

    lastTime = findMaxIDinFilename(dirPath)         #lastTime (int)
    format_lastTime = '%.6d' % lastTime             #Fix: error date format not re-save but cont record
    currentImage = findLastFileName(lastDir, format_lastTime)  #format_lastTime (String)
    print("Continue record on: " + str(currentImage))
except:
    currentImage = 0
    print("New record on: " + str(currentImage))
    pass

isButtonPressedA = 0
isButtonPressedB = 0
get_year = 2020
get_month = 0
get_day = 0
get_hour = 0
get_min = 0
get_sec = 15
isCheckInput = 0

try:
    while(True):
        img = sensor.snapshot()
        img.mean_pool(3,3)
        lcd.display(img)
        #get currentImage by input new date
        if but_b.value() == 0 and isButtonPressedB == 0:
            lcd.clear()
            time.sleep(3)
            while(isCheckInput == 0):
                if isButtonPressedA == 0:
                    isButtonPressedA,get_month = input_datetime(isButtonPressedA,get_year, get_month, get_day,get_hour,get_min,get_sec)
                    time.sleep(1)
                    lcd.clear()
                if isButtonPressedA == 1:
                    isButtonPressedA, get_day = input_datetime(isButtonPressedA,get_year, get_month, get_day,get_hour,get_min,get_sec)
                    time.sleep(1)
                    lcd.clear()
                if isButtonPressedA == 2:
                    isButtonPressedA, get_hour = input_datetime(isButtonPressedA,get_year, get_month, get_day,get_hour,get_min,get_sec)
                    time.sleep(1)
                    lcd.clear()
                if isButtonPressedA == 3:
                    isButtonPressedA, get_min = input_datetime(isButtonPressedA,get_year, get_month, get_day,get_hour,get_min,get_sec)
                    time.sleep(1)
                    lcd.clear()
                if isButtonPressedA == 4:
                    #print(get_year,get_month,get_day,get_hour,get_min,get_sec)
                    isButtonPressedA = 0
                    isCheckInput = 1
                    break

            img = sensor.snapshot()
            img.mean_pool(3,3)
            disp_img=img.copy()
            disp_img.draw_rectangle(0,20,320,1,color=(0,144,255),thickness=10)
            disp_img.draw_string(25,15,"%04d/%02d/%02d %02d:%02d:%02d"%(get_year,get_month,get_day,get_hour,get_min,get_sec),color=(255,255,255),scale=1)
            lcd.display(disp_img)
            currentImage = utime.mktime((get_year,get_month,get_day,get_hour,get_min,get_sec,0,362))
            print("Start at input date: ", currentImage)
            print("Check input: ", isCheckInput)
            time.sleep(3)

        #get currentImage from last file
        if but_a.value() == 0 and isButtonPressedA == 0:
            time.sleep(5)
            while(isButtonPressedB == 0):
                clock.tick()
                if(currentImage == 0):
                    print("Case 1")
                    getCurrentTime = getTime(now)
                    year,month,mday,hour,minute,second, weekday, yesterday = getCurrentTime
                    file_date, file_time = fileFormatCheck(year,month,mday,hour,minute,second, weekday, yesterday)
                    now = now + 600
                else:
                    if isCheckInput != 1:
                        currentImage = currentImage + 600
                        getCurrentTime = utime.localtime(currentImage)
                        print("Case 2")
                    else:
                        print("Case 3")
                        isCheckInput = 0
                        getCurrentTime = utime.localtime(currentImage)
                    #print(getCurrentTime)
                    year,month,mday,hour,minute,second, weekday, yesterday = getCurrentTime
                    file_date, file_time = fileFormatCheck(year,month,mday,hour,minute,second, weekday, yesterday)

                if str(currentDirectory) != file_date:
                    try:
                        os.mkdir("/sd/train/" + str(file_date))
                    except:
                        pass

                ## Add Light for Night time Fix: 20191025
                #if 165959 < int(file_time) < 235959 or 0 <= int(file_time) < 60000:
                led_w.value(0)  #turn on
                img = sensor.snapshot()
                currentDirectory = file_date
                img.save("/sd/train/" + str(currentDirectory) + "/" + str(file_time) + ".jpg", quality=85)
                img.mean_pool(3,3)
                lcd.display(img)
                play_sound("/sd/kacha.wav")
                led_w.value(1)  #turn off

                if but_b.value() == 0 and isButtonPressedB == 0:
                    isButtonPressedB = 1
                    print("Pause", isButtonPressedB)
                    try:
                        lastDir = findMaxIDinDir("/sd/train")
                        lastTime = findMaxIDinFilename("/sd/train/" + str(lastDir))
                        format_lastTime = '%.6d' % lastTime
                        currentImage = findLastFileName(lastDir, format_lastTime)
                        print("Continue record on: " + str(currentImage))
                    except:
                        currentImage = 0
                        pass
                    #sensor.run(1)
                    break

                #sensor.run(0)
                time.sleep(600)
                #sensor.run(1)

            isButtonPressedB = 1

        if but_a.value() == 1:
            isButtonPressedA = 0

        if but_b.value() == 1:
            led_w.value(1)  #turn off
            isButtonPressedB = 0


except KeyboardInterrupt:
    pass
