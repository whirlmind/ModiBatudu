# ModiBatudu
Check for last-modified-date-time of a given file, check for internet connection, if exists, run a batch file. 

ModiBatudu User Guide

10th May 2015

Need :
-----

You want to check when a certain file was last modified. 
If the file age is too old, (say, more than 24 hours old), :
	you want to check for an internet connection. 
		If the internet connection is present, 
				you want to run a batch file. 
		If the internet connection is not present, 
				Remind user to connect. 
If the files are recent/upto-date (i.e. not too old), do nothing. 

How to get going quickly : 
-------------------------

(a) Download and unzip the tool to a folder of your choice. 
(b) ModiBatudu.exe is the executable you are looking for. It runs based on the parameters set in ModiBatudu_Config.xml in the same folder. 
(c) Have a batch file ready, the one that you want to be run, from time to time. At the end of the batch file, ensure it writes to some text file about the last date and time of update. 
(d) Set the parameters in ModiBatudu_Config.xml, mainly the batch file you decided above and the frequency you want it to check. The xml file has in-line comments to guide you. 
(e) Set ModiBatudu.exe to run on a scheduled task in Windows at whichever frequency you want. 

Example use case :
--------------------

Say, You have a web application. You want to schedule backups of the MySql database. You have written your batch file for that using mysqldump.
You also want to take a backup of the remote folder. You don't want to backup all files, but synchronize modified files. For this, you have written your batch file (say, using WinSCP). 
You have also combined both batch files into a single one. (say, MyDailyBackupBatchFile.bat)
In the batch file, include another line to write current date and time into a text file(say, MyLastBackupDateTime.txt)
However, you connect to internet erratically or connect after signing into a proxy. So, the batch file does not know whether it has an internet connection. 
You can use this tool, to check the last-modified-date of MylastBackupDateTime.txt. Add the EXE file ModiBatudu.exe or the python script file ModiBatudu.py to your Windows Scheduler. Set the parameters for the run by modifying ModiBatudu_Config.XML in the same directory. 
If your last backup has been recent, it will shut up and exit. 
If your last backup time is too old, and if an internet connection is present, it will call the batch file MyDailyBackupBatchFile.bat. 
If your last backup time is too old, but internet connection is not present, it will alert you to connect to the internet. Not annoyingly again and again, but as per the alert frequency you have set and logging the last alert. 

Parameters that can be set in config file:
----------------------------------------

(ModiBatudu_Config.xml):
-------------------------

1. File_To_Check_Last_Modi : Which file should I check for Last-Modified-Date-Time to find out if my files or folder is too old ? (Example : MyLastBackupDateTime.txt). 
Should contain the full path and along with the file name. If only a file name is present, current application path will be assumed. 
2. Age_In_Minutes : How old is old ? (Example, more than 24 hours old or more than a week old). 
Should be a positive integer. 
3. Alert_Frequency_In_Minutes : How often should a user be alerted ? (Can be different, and typically should be different, from Files Age as above. 
For example, your backup frequency can be daily and alert frequency (where backup has not happened) can be hourly. An alert frequency of 1 hour means, you don't want to be alerted more often than hourly, if the scheduled task keeps checking of file updates, say, every 15 minutes. 
Should be a positive integer. 
4. Check_URL : Which URL should I attempt to download, to check for an internet connection ? Should be a valid URL. 
5. Add_UUID_To_Skip_Caching : Do you want the tool to add a random GUID to the URL to ensure cached pages returned are not wrongly taken as "internet connection present" ? Value must be 0 or 1, 0=No, 1=Yes. 
6. TimeOut_In_Seconds : Time out for web page download. 
7. Word_To_Find_In_Page  : Once the said web page is downloaded, do you want to check for the presence of any particular word or phrase ? (Example : cookie . In my case, the proxy would return as if the web page www.google.com was downloaded, so the html wouldn't contain the actual web page sent by Google. I would check for the word 'cookie', for instance, to see if the page was sent by Google. (My proxy's return page wouldn't contain the word, if it didn't connect to Google). This parameter is optional. 
8. Batch_FileName_WithPath_If_Connection_Successful : Perhaps the most important parameter. If the files are found to be old and internet connection is present, what batch file can I run to update the files ? 
Should contain the full path and along with the file name. If only a file name is present, current application path will be assumed. 
9. Wait_On_Finish : After you finish the task of downloading, show a prompt before finish for user to acknowledge, saying.. "Press any key to continue."

Ways to execute the tool :
-------------------------

The file ModiBatudu.exe is portable and can run (hopefully) on all versions of Windows XP upwards. Tested on Windows XP and Windows 7, however. Any other testing feedback is welcome. 
Alternatively, if you have Python installed already, you can use the Python script, ModiBatudu.py in the source folder to execute it. 
In both cases, the config file ModiBatudu_Config.XML must be present in the same path as the executable/script file. 

Files found in the tool's folder :
-----------------------------------

ModiBatudu_Config.xml : This is the config file. The file name has to be exactly this and it should be found in the path from which the application/exe/script is running. 
SampleBatFile_ConnSuccess.bat : A sample file that has been mentioned the Sample Config file, shipped with the tool. You will, typically, replace it with the Batch file you want to be run when the internet connection is found and files are out of date. Ensure, full path is mentioned in the config file. 
ModiBatudu_Log.txt : Keeps a simple one-line status about the last time the tool was executed. Along with the timestamp. It is one of : 
(a) Checked for files last-modified and files are upto-date (not too old) 
(b)Files old. But, already alerted. No fresh alert due. 
(c)Files old. Alerted. But, user cancelled action.
(d)Done! ModiBatudu task successful... All eez well..

ModiBatudu_LastAlertTime.txt : Keeps the date-timestamp of the last time user was alerted. This portion uses the python library easyGUI's EgStore class. The usage is pretty much similar to the example found int easyGUI's docs. 
If you change the source code :
ModiBatudu.py : The real meat of the tool. Has inline comments to show what it's doing. My first Python script, so feedback is welcome on all aspects. Be kind, LoL. 
ModiBatudu_Setup.py : This can be found in the folder for source-code. This is accessed while py2exe tries to convert ModiBatudu.py into ModiBatudu.exe. If both these are present, you would typically run:
 "C:\Folder_goes_here\ModiBatudu_Setup.py py2exe " at the command prompt to produce ModiBatudu.exe. You will need to this only if you change the source code. You might want to notice, that as per this set up file, the destination folder for the EXE, the dependent DLL etc, will the the "dist" subfolder of the folder from which this setup script is run. 
 
How I have personally used it : 
------------------------------

We connect to internet from a computer (shared, at the workplace)and through a proxy. Users may or may not remain logged in to the proxy, depending on when they browse. However, I wanted the backups to be regular and automated, even if connections to the Internet were erratic. So, I wrote :
(a) a Windows batch file to do the MySqlDump. 
(b) a WinSCP script to do the ftp Sync of the web application folder 
(c) Combined these two into a single batch file. 
(d) Then mentioned that batch file in the config file of this tool 
(e) Put ModiBatudu.exe on a Windows scheduled task that runs every hour.
I wanted to have a portable tool that runs on Windows, without having to install Python on the deployed machine. 

How do you check for internet connection ?
---------------------------------------------

Well, there is no simple foolproof way, unless to check the remote task you want to do and have it fail and return its failure. PINGs may require administrative privileges, pings may be denied, proxy may stand in the way and fail and so on. However, this script does not complicate the scenario too much (and therefore is not the 100% foolproof method to check an internet connection). It works in “most common” scenarios, if thats good for you. 
It tries to download a web page you specify and if it's able to do so, it thinks internet connection is present. 
It allows you to set which page you want to check. ( in the config file). Yes, only one web page. 
It allows you to ensure cached pages are not returned. (again, too simply, by adding a GUID to the URL). 
Downloads the page, using Python's urllib.request.urlopen. 
Having downloaded the page, if you have asked it to look for a certain word or phrase in the page, it will look for it. 
If no word is set to be sought in the page, as long as the page downloads, it is treated as success. 
If the word is found, the connection is treated as success.
If the word is not found, the connection is treated as failure. 
For example, a Google home page returned by Google, will have the word 'cookie'. The same page, as returned by your proxy not connected to the Internet, may not have it ? ( Well, in my case, my proxy would return “you need to sign in to view this page” or some such. Or you can pick whichever page and whichever word. 

Why that name ?
---------------
It checks for last-modified-time and then checks for internet connection if files are out of date. So, Modi. 
Bat is for the batch file. 
‘udu’ is a Telugu suffix, LoL. 

