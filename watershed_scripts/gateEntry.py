# name=GateEntry
# displayinmenu=true
# displaytouser=true
# displayinselector=true
#GateEntry Manual Program
#Runs manually via CWMS-Vue when regulator needs to input a gate change
#
#Jessica Branigan
#
#Version 1.0 written Oct 2014
###Does not work!!!
#
#Version 2.0 written Nov 2014
###Changes: Uses JOptionPane rather than creating functions using JComboBox
###updated for MPV in Oct 2021 by M. Weier
# added suggested time as now, loop for multiple gates, and check to prevent gate changes more than 5 days old
from hec.script			import MessageBox
from hec.heclib.util import HecTime
import java
import time,calendar
from javax.swing		import JOptionPane
from java.awt           import BorderLayout,GridLayout, FlowLayout, Toolkit
from java.awt.event     import ActionListener
from javax.swing.border import EmptyBorder
import sys
from rma.swing          import DateChooser
import DBAPI
from hec.script.Constants import TRUE, FALSE
from datetime import datetime, timedelta
#################
timeZone = "America/Chicago"
#timeZone = 
#******************CHOOSE PROJECT FOR GATE ENTRY********************************
gateDict = {
'Baldhill_Dam':[
	'LowFlow01',
	'LowFlow02',
	'TainterGate01',
	'TainterGate02',
	'TainterGate03',
	'FishSiphon'],
'Homme_Dam':[
	'LowFlow'],
'LakeDarling':[
	'TainterGate1',
	'TainterGate2',
	'TainterGate3',
	'TainterGate4',
	'TainterGate5'],
'TraverseRES_Dam':[
	'LongGate',
	'ShortGate'],
'TraverseWR_Dam':[
	'TainterGate01',
	'TainterGate02',
	'TainterGate03'],
'Orwell_Dam':[
	'LowFlow01',
	'LowFlow02',
	'TainterGate01'],
'Highway75_Dam':[
	'LeafGate',
	'LowFlow'],
'MarshLake_Dam':[
	'DrawdownStructure'],
'LacQuiParle_Dam':[
	'BulkheadBay08',
	'BulkheadBay09',
	'BulkheadBay10',
	'BulkheadBay11',
	'BulkheadBay12',
	'LiftGate01',
	'LiftGate02',
	'LiftGate03',
	'LiftGate04',
	'LiftGate05',
	'LiftGate06',
	'LiftGate07',
	'LiftGate08',
	'LiftGate09',
	'OpenBay05',
	'OpenBay06',
	'OpenBay07'],
'RedLake_Dam':[
	'SluiceGate01',
	'SluiceGate02',
	'SluiceGate03'],
'ChippewaDiv_Dam':[
	'TainterGate',
	'LowFlow']
}
#
#Define array of project choices
projectChoices = list(gateDict.keys())
#Calls the JOptionPane funtion:  showInputDialog(Parent Component, Message, Title, MessageType, Icon, List, Initial Selection)
projectSelected = JOptionPane.showInputDialog(None,"Choose a Project","Gate Entry Program",JOptionPane.PLAIN_MESSAGE,None,projectChoices,projectChoices[0])
print(projectSelected)
if str(projectSelected) != "None" :
	#
	#*******************************************************************************
	
	#******************CHOOSE DATE/TIME FOR GATE ENTRY******************************
	#
	#round downn to nearest hour
	todayDT = datetime.today().replace(minute=0)
	
	#Calls the JOptionPane funtion:  showInputDialog(Parent Component, Message, Title, MessageType)
	#dateTimeSelected = JOptionPane.showInputDialog(None,"Enter Date/Time of Gate Change in CST (DDMMMYYYY HHMM) \n Ex. 01Jan2014 0600","Gate Entry Program",todayDT.strftime('%d%b%Y %I%M'),JOptionPane.PLAIN_MESSAGE)
	dateTimeSelected = JOptionPane.showInputDialog(None,"Enter Date/Time of Gate Change in {} time zone (DDMMMYYYY HHMM)".format(timeZone),todayDT.strftime('%d%b%Y %H%M'))
	print(dateTimeSelected)
	
	dateTimeSelectedDT  = datetime.strptime(dateTimeSelected, '%d%b%Y %H%M')
	
	
	while dateTimeSelectedDT<todayDT+timedelta(days=-5):
		MessageBox.showPlain("Date time selected is not within 5 days of current date and time.  Enter start date again or edit gates in CWMSVUE.", "Gate Entry Program")
		#Calls the JOptionPane funtion:  showInputDialog(Parent Component, Message, Title, MessageType)
		dateTimeSelected = JOptionPane.showInputDialog(None,"Enter Date/Time of Gate Change in {} time zone (DDMMMYYYY HHMM)".format(timeZone),todayDT.strftime('%d%b%Y %I%M'))
		print(dateTimeSelected)
		dateTimeSelectedDT  = datetime.strptime(dateTimeSelected, '%d%b%Y %I%M')
		
	
	
	#Validates user-entered date/time and sets it as start time
	dateValid = HecTime()
	dateValid.set(dateTimeSelected)
	startDateTime = dateValid.dateAndTime(4)
	print(startDateTime)
	
	##check if start  date is in the future
	if datetime.strptime(startDateTime,'%d%b%Y, %H:%M')>todayDT:
		#Sets end time as start time +13 hours formatted to be readable by the setTimeWindow method
		endDateTime = datetime.strptime(startDateTime,'%d%b%Y, %H:%M')+timedelta(hours=13)
	else:
		#Sets end time as today time +13 hours formatted to be readable by the setTimeWindow method
		endDateTime = todayDT+timedelta(hours=13)
	
	timeFormat = "%d%b%Y %H%M"
	endDateTime = endDateTime.strftime(timeFormat)
	print(endDateTime)
	#
	#*******************************************************************************
	##trigger to exit the gate entry program
	exitTrigger = False
	
	#Opens and defines CWMS database
	db = DBAPI.open()
	db.setTimeWindow(str(startDateTime), str(endDateTime))
	officeID = 'MVP'
	db.setOfficeId(officeID)
	db.setTimeZone(timeZone)
			
	
	while not exitTrigger:
		#******************CHOOSE GATE TYPE FOR GATE ENTRY******************************
		#
		
		#Define array of gate types
		gateTypeChoices = gateDict[projectSelected]
		
		#Calls the JOptionPane funtion:  showInputDialog(Parent Component, Message, Title, MessageType, Icon, List, Initial Selection)
		gateTypeSelected = JOptionPane.showInputDialog(None,"Choose Gate Type","Gate Entry Program",JOptionPane.PLAIN_MESSAGE,None,gateTypeChoices,gateTypeChoices[0])
		
		print(gateTypeSelected)
		
		if str(gateTypeSelected) == "None" :
			exitTrigger = True
			#Closes database
			db.close()
		else:
			#
			#*******************************************************************************
			
			
			
			#******************CHOOSE GATE OPENING FOR GATE ENTRY***************************
			#
			#Calls the JOptionPane funtion:  showInputDialog(Parent Component, Message, Title, MessageType)
			gateOpeningSelected = JOptionPane.showInputDialog(None,"Enter Gate Opening in FT \n Ex. 0.25","Gate Entry Program",JOptionPane.PLAIN_MESSAGE)
			if gateOpeningSelected is not None:
				gateOpeningSelected = float(str(gateOpeningSelected))
				
				print "Gate Opening is " + str(gateOpeningSelected) + " ft"
				#
				#*******************************************************************************
				
				#Defines time series ids for data
				tsid = str(projectSelected) + "-" + str(gateTypeSelected) + ".Opening.Inst.15Minutes.0.CEMVP-ProjectEntry"
				print(tsid)
				
		
				
				#Verifies tsid is valid.  If invalid, pop up message box saying script failed and exit
				tsidValid = tsid in db.getPathnameList()
				print(tsidValid)
				
				if tsidValid == 1 :
					#The read method returns an HecMath object (time series math object) that holds the data set specified by the pathname
					tsm = db.read(tsid)
					
					#Generates a new regular time series with user-selected values and time window
					##generateRegularIntervalTimeSeries(string start time, string end time, new ts interval, offset (e.g., "5Min"), double initial value)
					tsmNew = tsm.generateRegularIntervalTimeSeries(str(startDateTime), str(endDateTime), "15Minute", None, gateOpeningSelected)
					tsmNew.setType("INST-VAL")
					tsmNew.setUnits("ft")
					
					#Puts new time series into database
					tsmNew.setPathname(tsid)
					tsmNew = tsmNew.getData()
					db.put(tsmNew)
					
					#Show message box summarizing gate change
					MessageBox.showPlain("Gate change to {} for ".format(gateOpeningSelected) + str(projectSelected) + "-" + str(gateTypeSelected) + " will be applied on " + str(startDateTime), "Gate Entry Program")
		
				else:
					#Closes database
					db.close()
					MessageBox.showPlain("Time Series does not exist in database.  Script failed.", "Gate Entry Program")
			else:
				#Closes database
				db.close()
				MessageBox.showPlain("Time Series does not exist in database.  Script failed.", "Gate Entry Program")
	
	#Closes database
	db.close()
