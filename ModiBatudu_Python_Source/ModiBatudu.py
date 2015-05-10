from easygui import *
import pprint
import os
import sys
import subprocess
import urllib.request
import datetime
import time
import xml.etree.ElementTree as ET
import pprint
import urllib.request

config_name = 'ModiBatudu_Config.xml' #Should Exist. 
log_file_name = 'ModiBatudu_Log.txt' #If Not Exists, will be created in the application path. 
mySettingsFileName = "ModiBatudu_LastAlertTime.txt"
#By default, wait (pause on screen) after finishing task, unless otherwise stated in config file. 
intWaitForUser = 1;

errHappened = False; 

#Given the File name, get the full path. 
#Check whether script file is running or executable is running and get accordingly. 
def getConfigFileFullPath( configFileName ):
	# determine if application is a script file or frozen exe
	if getattr(sys, 'frozen', False):
		application_path = os.path.dirname(sys.executable)
	elif __file__:
		application_path = os.path.dirname(__file__)

	config_path = os.path.join(application_path, configFileName)	   
	return config_path;

#Given a parameter name, get the parameter value from the config file XML Element Tree object. 
def getParamValue( xObjConfigXML, paramName, bitErrIfNotFound ):
	paramValue = xObjConfigXML.find(paramName);
	global log_file_name;
	global errHappened;
	if (paramValue is None):
		if (bitErrIfNotFound == True):
			errMe("Error looking for : " + paramName + "in Config File. Was not found...", "1", log_file_name, errHappened);
			return "ERR";
		else:
			return "";
	else:
		paramValueText = paramValue.text.strip();
		return paramValueText;
	
#Write log messages to file. 	
def errMe( strErrContext, strWaitOnError, strLogFileName, isAppendHere):
	try:
		print(strErrContext);
		if (isAppendHere == True): #File already opened before. Now open for append. 
			text_file = open(strLogFileName, "a")	
		else: #File not already opened before. Open now to write. 
			text_file = open(strLogFileName, "w")
		text_file.write("Log Date Time : " + str(datetime.datetime.now()) + ":::" + " Log Message : " + strErrContext)
		text_file.close()	
		if (strWaitOnError == "1"): #When error happens, wait for user to acknolwedge. 
			input("Press Enter to continue...");
	except:
		print("Errors happened, but unable to log them...");	
		
def exitMe():
	global intWaitForUser;
	if (intWaitForUser == 1):
		proc = input("Press any key to continue...")
		intWaitForUser = 0;		
	sys.exit()
		
def checkNetConn(xToCheckURL, xWordToFind, xIsAddRandom):		
	#Default values. 
	connStatus = 0;
	foundStatus = 0;
	foundWordCharIndex = -99999;
	
	if (xIsAddRandom == True):
		xToCheckURL = xToCheckURL + "?My_Nocache_UUID=" + str(uuid.uuid4());	#If set to 1, add random GUID to URL. 

	strPageContents = "";
	#Attempt to open the web page. 
	#If successful, get page contents. 
	try:
		objResponsePage = urllib.request.urlopen(xToCheckURL, None, 1);
		strPageContents = str(objResponsePage.read())	;
	except urllib.request.URLError:
		pass

	if (strPageContents != ""):
		connStatus = 1; #Internet connection was successful. 
		if (xWordToFind == ""):
			foundStatus = 1; 
			#Internet connection was successful. User did not specify any specific word to be found. 
			#So, connection success is enough to run the success-batch-file. 
		else:
			foundWordCharIndex = strPageContents.find(xWordToFind);
			if (foundWordCharIndex > 0):
				foundStatus = 1; #Internet connection successful. Required word was found on page. 
			else:
				foundStatus = 0; 
				#Internet connection successful, but required word was not found on page. Treat as failure. 
	else:
		connStatus = 0;
		foundStatus = 0;		
		
	return foundStatus;

#This class partially copy-pasted from easygui library demo. 
class Settings(EgStore):
	def __init__(self, filename):  # filename is required
		#-------------------------------------------------
		# Specify default/initial values for variables that
		# this particular application wants to remember.
		#-------------------------------------------------
		self.Last_Alert_TimeStamp_Num = ""

		#-------------------------------------------------
		# For subclasses of EgStore, these must be
		# the last two statements in  __init__
		#-------------------------------------------------
		self.filename = filename  # this is required
		self.restore()            # restore values from the storage file if possible

#-----------------------------------------------------------------------------------------		

FQconfig =  getConfigFileFullPath(config_name); #Get the full path of config file. 
log_file_name =  getConfigFileFullPath(log_file_name); #Get the full path of log file. 
settingsFile = getConfigFileFullPath(mySettingsFileName); #Used only to store Last Alert Time. 

if (os.path.isfile(FQconfig) == False): #If config file does not exist, report error. 
	errMe("Error: Config File Not found... Config file must be named as ModiBatudu_Config.xml and must lie in the same directory as the EXE or the script file...", "1", log_file_name, errHappened);
	errHappened = True;
	exitMe();
	
#If the Settings File used to store Last Alert Time is missing,  Create it in the application path. 
if (os.path.exists(settingsFile) == False):
	text_file = open(settingsFile, "a")
	text_file.write("")
	text_file.close()	
	settings = Settings(settingsFile)			
	settings.Last_Alert_TimeStamp_Num = time.time();	
	settings.store()
		
#Read Config XML file contents into an object of the class ElementTree. 		
try:		
	objConfigXML = ET.parse(FQconfig); 
except: #XML file not well-formed. 
	errMe("Error parsing Config File...", "1", log_file_name, errHappened);
	errHappened = True;
	exitMe();

#After job is done/aborted, should I wait for user to acknowledge, saying Press any key to Continue... ?	
strWaitForUser = getParamValue(objConfigXML, 'Wait_On_Finish', False); 
if (strWaitForUser == "0"):
	intWaitForUser = 0;

#Which file's Last-Modified-Date-Time should be checked to verify whether Backup files are up-to-date ?
fileToCheckLastModi = getParamValue(objConfigXML, 'File_To_Check_Last_Modi', True); 

if (fileToCheckLastModi == "ERR"):
	exitMe();
	
if (os.path.isfile(fileToCheckLastModi)) == False and os.path.isfile(getConfigFileFullPath(fileToCheckLastModi)) == True:
	fileToCheckLastModi = getConfigFileFullPath(fileToCheckLastModi);

	
#What is the maximum age of Files, beyond which it is treated as out-of-date ?	
ageInMinutes = getParamValue(objConfigXML, 'Age_In_Minutes', False);	
if ageInMinutes.isnumeric() == False:
	ageInMinutes = "1435"; #No. of minutes in a day. MINUS 5 minutes. 
	
intAgeInMinutes = int(ageInMinutes);	

#Once files are found to be old, how often should the user be alerted, in case he hasn't taken action on the first alert ?
alertFreqInMin = getParamValue(objConfigXML, 'Alert_Frequency_In_Minutes', False);	
if alertFreqInMin.isnumeric() == False:
	alertFreqInMin = ageInMinutes; 
	
intAlertFreqInMin = int(alertFreqInMin);	
	
#If connection and word-finding is successful, which batch file should be run ? 
successBatchFileNameWithPath = getParamValue(objConfigXML, 'Batch_FileName_WithPath_If_Connection_Successful', False);

if (os.path.isfile(successBatchFileNameWithPath)) == False and os.path.isfile(getConfigFileFullPath(successBatchFileNameWithPath)) == True:
	successBatchFileNameWithPath = getConfigFileFullPath(successBatchFileNameWithPath);
	
#Check whether file exists. 
if (os.path.isfile(successBatchFileNameWithPath) == False) and (successBatchFileNameWithPath != "") :
	errMe("Error : Parameter named 'Batch_FileName_WithPath_If_Connection_Successful' in Config File : Invalid File Name: " + successBatchFileNameWithPath, "1", log_file_name, errHappened);	
	errHappened = True;
	successBatchFileNameWithPath = "";	

settings = Settings(settingsFile)	

#URL that should be attempted for web-page-opening to check internet connection existence. 
checkURL = getParamValue(objConfigXML, 'Check_URL', True); 

if (checkURL == "ERR"):
	exitMe();
	
#To avoid cached pages being fetched, should I add a random GUID value to the URL ? 	
skipCacheId = getParamValue(objConfigXML, 'Add_UUID_To_Skip_Caching', False);	
if (skipCacheId =="1"):
	is_SkipCacheId = True;
else:
	is_SkipCacheId = False;

timeOutSeconds = getParamValue(objConfigXML, 'TimeOut_In_Seconds', False);	
if timeOutSeconds.isnumeric() == False:
	timeOutSeconds = "1";
	
intTimeOutSeconds = int(timeOutSeconds);	
	
#After the page is fetched, any specific word to look for ? 	
wordToFind = getParamValue(objConfigXML, 'Word_To_Find_In_Page', False);

#--------------Validation of all input parameters over. Now, move on to actual meat of verification... 

#Get the last-modified-date-time of the file to be checked. 
myTimeStamp = os.path.getmtime(fileToCheckLastModi)
#Store a readable format for future display. 
myTimeStampReadable = datetime.datetime.fromtimestamp(myTimeStamp)
#Compare and find the difference between current time and last modified time. 
myTimeDiff = time.time() - myTimeStamp;
#Find difference in minutes. 
myTimeDiff_Minutes = myTimeDiff / 60;

#Compare with allowed age in minutes. 
if (myTimeDiff_Minutes <= intAgeInMinutes):
	isFileToo_Old = False
else:
	isFileToo_Old = True


#If files are not too old, files are upto-date. Nothing to do. Happpies... 	
if (isFileToo_Old == False):
	myMsg = "Checked files. Not too old. Checked at : " + str(time.ctime());
	errMe(myMsg, "0", log_file_name, errHappened);	
	sys.exit();

#Files are old. User should be alerted. Find out when he was last alerted, by loading the earlier saving from the Settings file. (NOT config file). 	
Last_Alert_TimeStamp_Num = float(settings.Last_Alert_TimeStamp_Num);	

#Find time difference between time-of-last-alert-to-user and Now. 
myAlertTimeDiff = time.time() - Last_Alert_TimeStamp_Num;

#Find time difference in minutes. 
myAlertTimeDiff_In_Minutes = myAlertTimeDiff / 60;

#Compare with alert frequency. If a recent alert has been given within the frequency, do not alert again. 
if (myAlertTimeDiff <= intAlertFreqInMin):
	isAlertDue = False
else:
	isAlertDue = True

if (isAlertDue == False):
	myMsg = "Files old. But, already alerted. No fresh alert due. Reviewed at : " + str(time.ctime());
	errMe(myMsg, "0", log_file_name, errHappened);	
	sys.exit();
else: #Alert is due. So write to the settings file, in preparation for the alert that will follow. 
	settings = Settings(settingsFile)			
	settings.Last_Alert_TimeStamp_Num = time.time();	
	settings.store()	

hasProperReply = False;
isRunBatchFile = False;

#Files are old. User needs to be alerted. Before alerting him, find if internet connection is available, so you can tell him that status as well. 
#If he presses Continue, without the internet connection being ON, go into a loop. 
#Until, (a) he either presses Cancel choosing to do the update job later. 
#(OR)
#(b) he connects to Internet and comes back to press the Continue button for the files update to proceed. 

while (hasProperReply == False):
	foundStatus = checkNetConn(checkURL, wordToFind, is_SkipCacheId)
		
	if (foundStatus == 1): #If success, run batch file pertaining to success. 
		myMsg = ("Files due for update." + "\n" + " Last updated : " + str(myTimeStampReadable) + "\n" + 
					" Internet connection available. " + "\n" + "Click the Continue button to update files...")
	else: #If failure, run batch file pertaining to failure. 
		myMsg = ("Files due for update." + "\n" + " Last updated : " + str(myTimeStampReadable) + "\n" + 
					" Unable to connect to Internet. " + "\n" + 
					" Connect to Internet and then click the Continue button to update files...")
					
	title = "Update of Files is due..."
	reply = ccbox(myMsg, title)

	if (reply == False): #User chooses to quit. 
		myMsg = "Files old. Alerted. But, user cancelled action. Reviewed at : " + str(time.ctime());
		errMe(myMsg, "0", log_file_name, errHappened);	
		hasProperReply = True;
		exitMe();
	else: #User chooses to continue. 
		foundStatus = checkNetConn(checkURL, wordToFind, is_SkipCacheId)	
		if (foundStatus == 0): 
			#User chose to continue, but did not connect to Internet. Go back to looping the alerts. 
			hasProperReply = False;			
		else: 
			#User chose to continue with update and internet connection is available. The batch file can be run. Exit Loop. 
			isRunBatchFile = True;
			hasProperReply = True;

if (isRunBatchFile == True):
	if (successBatchFileNameWithPath != ""):
		subprocess.call(successBatchFileNameWithPath);
		errMe("Done! ModiBatudu task successful... All eez well..", "0", log_file_name, errHappened);			
		exitMe();		
	else:
		errMe("Batch file required to run. But File Not found...", "0", log_file_name, errHappened);		errHappened = True;				
		exitMe();
else:
	exitMe();
	
