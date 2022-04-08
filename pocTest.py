# ----------------------------------------------------------------------------
# Name:         POC Monolith
# Description:  Python Script to Automate XDR Threat Intel
# Author:       Spencer Brown
# URL:          
# Date:         4/08/2022
# ----------------------------------------------------------------------------

from pywinauto import Application, Desktop
import time
import os 
import psutil
import win32gui
import win32con
import io
import sys
import wmi
import re

def setUpOutlook():
    app=Application(backend="uia").start(r'C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE')
    #currentWindows=app.windows()
    time.sleep(2)
    dlg=app['Welcome to Microsoft Outlook 2016']
    dlg.Next.click_input()
    dlg=app['Opening - Microsoft Outlook']    
    dlg.NoRadioButton.click_input()
    dlg.Next.click_input()
    dlg.CheckBox.click()
    dlg.Finish.click_input()
    time.sleep(5)
    dlg=app['Accounts']
    dlg.CloseButton.click_input()
    time.sleep(3)
    dlg=app['Outlook Today - Outlook']
    time.sleep(5)
    dlg.AcceptButton.click_input()
    time.sleep(5)
    os.system('cmd /k "Powershell.exe -ExecutionPolicy Unrestricted -file C:\\Users\\spencer\\ProvisioningFiles\\scripts\\pstfile.ps1"')


def returnPID(process):
    process_name = process
    processID = None
    for proc in psutil.process_iter():
        if process_name in proc.name():
            processID = proc.pid
            return (processID)
            
def processRunCheck(processname):
    for proc in psutil.process_iter():
        try:
            if processname.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    return False;
            
def killProcess(process):
    ti = 0
    name = process
    print('The process I am seeking to kill is: ' + str(name))
    f = wmi.WMI()

    for process in f.Win32_Process():
        if process.name == name:
            process.Terminate()
            print('I have found, and killed ' + str(name))
            ti +=1
    if ti == 0:
        print('There are no running instances of ' + str(name))
        
def extractTitle(listitem):
    listitem = str(listitem)
    pattern = r"'(.*?[^\\])'"
    targetString = str(re.findall(pattern,listitem))
    targetString1 = targetString.replace("[","")
    targetString2 = targetString1.replace("]","")
    nameOfWindow = targetString2.replace("'","")
    print(nameOfWindow)

outlook = returnPID("OUTLOOK.EXE")


def connectEmailAttachment():
    app = Application(backend="uia").connect(process=outlook, visible_only=False)
    time.sleep(5) #Need time for the activate office dialogue to appear. 
    mainDLG= app['Outlook Today - Outlook'] #Main application is presented as 'Outlook Today - Outlook'
    mainDLG['2TreeItem'].click_input() #Clicking 2 subTree of Sophos profile - changes window name.
    time.sleep(5)
    twoDLG = app['2 - Sophos - Outlook'] #New window name
    time.sleep(5)
    twoDLG['DeltaFlightItinerary.docm85 KB1 of 1 attachmentsUse alt + down arrow to open the options menu'].click_input(double=True) #opens the attachment

#At this point, I'm running into a CIXA issue
#Deleting file located at "C:\Users\spencer\AppData\Local\Microsoft\Windows\INetCache\Content.Outlook\8DX0TGNT\DeltaFlightItinerary.docm" 
#Results in a Word cannot open the document: user does not have access privileges prompt to
#I take this to mean CIXA has taken over here
#Evidenced by detections in Central.

def startEmailAttachment():
    
    app = Application(backend="uia").start(r'C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\OUTLOOK')
    time.sleep(5) #Need time for the activate office dialogue to appear. 
    accountsDLG = app['Accounts']
    accountsDLG.CloseButton.click_input()
    mainDLG= app['Outlook Today - Outlook'] #Main application is presented as 'Outlook Today - Outlook'
    #mainDLG.print_control_identifiers()
    mainDLG['2TreeItem'].click_input() #Clicking 2 subTree of Sophos profile - changes window name.
    time.sleep(5)
    twoDLG = app['2 - Sophos - Outlook'] #New window name
    time.sleep(5)
    twoDLG['DeltaFlightItinerary.docm85 KB1 of 1 attachmentsUse alt + down arrow to open the options menu'].click_input(double=True) #opens the attachment

#At this point, I'm running into a CIXA issue
#Deleting file located at "C:\Users\spencer\AppData\Local\Microsoft\Windows\INetCache\Content.Outlook\8DX0TGNT\DeltaFlightItinerary.docm" 
#Results in a Word cannot open the document: user does not have access privileges prompt to
#I take this to mean CIXA has taken over here
#Evidenced by detections in Central.

def enableMacro():
    #Connects to open microsoft word winow using regex, since window name is dynamic.
    app = Application(backend="uia").connect(title_re='.*DeltaFlightItinerary')
    window = app.windows() #app.windows() returns a list object.
    wordWindow = str(extractTitle(window[0])) #Extract title from list, and convert to string
    print("I'm looking for the window..." + wordWindow)
    guiWindow = win32gui.FindWindow(None,wordWindow) #Find our window with win32gui
    win32gui.ShowWindow(guiWindow,win32con.SW_SHOWMAXIMIZED) #Maximize the window. 
    main_dlg = app[wordWindow]
    main_dlg.set_focus() #Make window visible for clicking inputs. 
    main_dlg.EnableEditingButton.click_input() #Enable editing, pivots to enable content
    time.sleep(3)
    main_dlg.EnableContentButton.click_input() #Enable content button

connectEmailAttachment()

#if __name__ == '__main__':
    #openEmailAttachment()
    #killProcess('WINWORD.EXE')

    #if (processRunCheck('outlook.exe') == False):
        #openEmailAttachment()
        #time.sleep(10)
        #enableMacro()
        
    #else:
        #print('Outlook is currently running.')
        #print('I am now going to kill the Outlook Process.')
        #killProcess('OUTLOOK.EXE')
        #time.sleep(10)
        #print('Outlook will now start.')
        #openEmailAttachment()
        #time.sleep(10)
        #enableMacro()
      
