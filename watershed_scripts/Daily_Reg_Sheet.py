from hec.heclib.util import HecTime
from hec.script import Plot, MessageBox
from java.util import Calendar, TimeZone
from java.lang import System
import DBAPI, hec
from hec.cwmsVue import CwmsListSelection
from hec.script import AxisMarker
from com.rma.client import Browser
from javax.swing		import JOptionPane
import shutil
import os
import java
from hec.dataTable                  import HecDataTableToExcel, HecDataTableFrame
from com.rma.model import Project

import time
from datetime import datetime, timedelta

def checkDaylightSavingsTime(checkTime):
	# Get the current time
	#current_time = datetime.now()
	
	
	# Get the time 10 days ago
	#ten_days_ago = current_time - timedelta(days=7)
	
	# Convert the datetime object to a time tuple
	time_tuple = checkTime.timetuple()
	
	# Convert the time tuple to seconds since the epoch
	seconds_since_epoch = time.mktime(time_tuple)
	
	# Check if daylight saving time was in effect 10 days ago
	if time.localtime(seconds_since_epoch).tm_isdst:
	    print("Daylight saving is in effect.")
	    return True
	else:
	    print("Daylight saving time is not in effect.")
	    return False
###############
code_version = '11Nov2023'
flowTypes = ['Hornet Comp (Legacy) - green', 'CWMS Comp - red']
#flowTypeSelection = JOptionPane.showInputDialog(None,"Choose Flow Comp to Display","Daily Reg Sheet - ver. {}".format(code_version),JOptionPane.PLAIN_MESSAGE,None,flowTypes,flowTypes[1])
flowTypeSelection = flowTypes[1]
if flowTypeSelection:
	print(flowTypeSelection)

	
	#set True to use hornet flow, False for CWMS comp flow
	if flowTypeSelection == flowTypes[0]:
		legacyFlow = True
	else:
		legacyFlow = False
	
	###########
	
	
	# Determine Script Context
	isClient = hec.lang.ClientAppCheck.haveClientApp()
	isCWMSVue = hec.cwmsVue.CwmsListSelection.getMainWindow() is not None
	isShellScript = not isClient and not isCWMSVue
	# Time Series IDs
	# pool
	idelev2 = 'LockDam_02.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev3 = 'LockDam_03.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev4 = 'LockDam_04.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev5 = 'LockDam_05.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev5a = 'LockDam_05a.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev6 = 'LockDam_06.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev7 = 'LockDam_07.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev8 = 'LockDam_08.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev9 = 'LockDam_09.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev10 = 'LockDam_10.Elev.Inst.1Hour.0.rev-MSL1912'
	# control points
	idelev2c1 = 'STPM5.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev2c2 = 'SSPM5.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev3c1 = 'PREW3.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev3c2 ='STLM5.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev4c1 = 'WABM5.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev4c2 = 'LKCM5.Elev-Transducer.Inst.15Minutes.0.rev'
	idelev5c = 'AMAW3.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev6c = 'WNAM5.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev7c = 'DKTM5.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev8c1 = 'LACW3.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev8c2 = 'BRWM5.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev9c = 'LNSI4.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev10c1 = 'CLAI4.Elev.Inst.15Minutes.0.rev-MSL1912'
	idelev10c2 = 'MCGI4.Elev.Inst.15Minutes.0.rev-MSL1912'
	# tail
	idtail2 = 'LockDam_02-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail3 = 'LockDam_03-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail4 = 'LockDam_04-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail5 = 'LockDam_05-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail5a = 'LockDam_05a-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail6 = 'LockDam_06-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail7 = 'LockDam_07-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail8 = 'LockDam_08-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail9 = 'LockDam_09-Tailwater.Elev.Inst.15Minutes.0.rev-MSL1912'
	idtail10 = 'LockDam_10-Tailwater.Elev.Inst.1Hour.0.rev-MSL1912'
	# flow
	if not legacyFlow:
		idflow2 = 'LockDam_02.Flow.Inst.15Minutes.0.comp'
		idflow3 = 'LockDam_03.Flow.Inst.15Minutes.0.comp'
		idflow4 = 'LockDam_04.Flow.Inst.15Minutes.0.comp'
		idflow5 = 'LockDam_05.Flow.Inst.15Minutes.0.comp'
		idflow5a = 'LockDam_05a.Flow.Inst.15Minutes.0.comp'
		idflow6 = 'LockDam_06.Flow.Inst.15Minutes.0.comp'
		idflow7 = 'LockDam_07.Flow.Inst.15Minutes.0.comp'
		idflow8 = 'LockDam_08.Flow.Inst.15Minutes.0.comp'
		idflow9 = 'LockDam_09.Flow.Inst.15Minutes.0.comp'
		idflow10 = 'LockDam_10.Flow.Inst.1Hour.0.comp'
	else:
		idflow2 = 'LockDam_02.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow3 = 'LockDam_03.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow4 = 'LockDam_04.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow5 = 'LockDam_05.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow5a = 'LockDam_05a.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow6 = 'LockDam_06.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow7 = 'LockDam_07.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow8 = 'LockDam_08.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow9 = 'LockDam_09.Flow.Inst.15Minutes.0.comp'.replace( '15Minutes.0.comp','~4Hours.0.CEMVP-Legacy')
		idflow10 = 'LockDam_10.Flow.Inst.1Hour.0.comp'.replace( '1Hour.0.comp','~4Hours.0.CEMVP-Legacy')
	# hydropower
	idfordp = 'LockDam_01-Powerhouse.Flow.Inst.~1Day.0.CEMVP-Legacy'
	idhydro2 = 'LockDam_02-Powerhouse.Flow.Inst.15Minutes.0.comp'
	# gate settings
	idld2tgates = 'LockDam_02-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld3rgates = 'LockDam_03-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld4rgates = 'LockDam_04-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld4tgates = 'LockDam_04-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld5rgates = 'LockDam_05-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld5tgates = 'LockDam_05-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld5argates = 'LockDam_05a-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld5atgates = 'LockDam_05a-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld6rgates = 'LockDam_06-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld6tgates = 'LockDam_06-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld7rgates = 'LockDam_07-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld7tgates = 'LockDam_07-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld8rgates = 'LockDam_08-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld8tgates = 'LockDam_08-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld9rgates = 'LockDam_09-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld9tgates = 'LockDam_09-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld10rgates = 'LockDam_10-RollerGates.Opening-Normal.Inst.15Minutes.0.comp'
	idld10tgates = 'LockDam_10-TainterGates.Opening-Normal.Inst.15Minutes.0.comp'
	# flow/ft gate opening
	idld2tqft = 'LockDam_02-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld3rqft = 'LockDam_03-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld4rqft = 'LockDam_04-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld4tqft = 'LockDam_04-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld5rqft = 'LockDam_05-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld5tqft = 'LockDam_05-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld5arqft = 'LockDam_05a-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld5atqft = 'LockDam_05a-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld6rqft = 'LockDam_06-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld6tqft = 'LockDam_06-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld7rqft = 'LockDam_07-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld7tqft = 'LockDam_07-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld8rqft = 'LockDam_08-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld8tqft = 'LockDam_08-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld9rqft = 'LockDam_09-RollerGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld9tqft = 'LockDam_09-TainterGates.Flow-PerFootOpen.Inst.15Minutes.0.comp'
	idld10rqft = 'LockDam_10-RollerGates.Flow-PerFootOpen.Inst.1Hour.0.comp'
	idld10tqft = 'LockDam_10-TainterGates.Flow-PerFootOpen.Inst.1Hour.0.comp'
	# wind
	idld2ws = 'LockDam_02.Speed-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld2wd = 'LockDam_02.Dir-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld3ws = 'LockDam_03.Speed-Wind.Inst.~8Hours.0.CEMVP-Legacy'
	idld3wd = 'LockDam_03.Dir-Wind.Inst.~8Hours.0.CEMVP-Legacy'
	idld4ws = 'LockDam_04.Speed-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld4wd = 'LockDam_04.Dir-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld5ws = 'LockDam_05.Speed-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld5wd = 'LockDam_05.Dir-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	#idld5aws = ''
	#idld5awd = ''
	idld6ws = 'LockDam_06.Speed-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld6wd = 'LockDam_06.Dir-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld7ws = 'LockDam_07.Speed-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld7wd = 'LockDam_07.Dir-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld8ws = 'LockDam_08.Speed-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld8wd = 'LockDam_08.Dir-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld9ws = 'LockDam_09.Speed-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld9wd = 'LockDam_09.Dir-Wind.Inst.15Minutes.0.CEMVP-GOES-Raw'
	#idld10ws = ''
	#idld10wd = ''
	# temp
	idld2atemp = 'LockDam_02.Temp-Air.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld3atemp = 'LockDam_03.Temp-Air.Inst.~8Hours.0.CEMVP-Legacy'
	idld4atemp = 'LockDam_04.Temp-Air.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld5atemp = 'LockDam_05.Temp-Air.Inst.15Minutes.0.CEMVP-GOES-Raw'
	#idld5aatemp = ''
	idld6atemp = 'LockDam_06.Temp-Air.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld7atemp = 'LockDam_07.Temp-Air.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld8atemp = 'LockDam_08.Temp-Air.Inst.15Minutes.0.CEMVP-GOES-Raw'
	idld9atemp = 'LockDam_09.Temp-Air.Inst.15Minutes.0.CEMVP-GOES-Raw'
	#idld10atemp = ''
	# precip
	idld2precip = 'LockDam_02.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld3precip = 'LockDam_03.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld4precip = 'LockDam_04.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld5precip = 'LockDam_05.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld5aprecip = 'LockDam_05a.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld6precip = 'LockDam_06.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld7precip = 'LockDam_07.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld8precip = 'LockDam_08.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld9precip = 'LockDam_09.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	idld10precip = 'LockDam_10.Precip-inc.Total.~1Day.1Day.CEMVP-ProjectEntry'
	
	idld10forecast = 'LockDam_10.Flow.Inst.6Hours.0.Fcst-NCRFC-CHIPS'
	idWisconsin = 'MUSW3.Flow.Inst.15Minutes.0.comp'
	idKick = 'STEW3.Flow.Inst.15Minutes.0.rev'
	# Database Connection
	db = DBAPI.open()
	#db.setTimeZone("America/Chicago")
	db.setTimeZone("UTC")
	# set time
	cal = Calendar.getInstance()
	cal.setTimeZone(TimeZone.getTimeZone("America/Chicago"))
	cal.setTimeInMillis(System.currentTimeMillis())
	#cal.setTimeInMillis(1636214400000)
	t = HecTime(cal)
	
	#print t.dateAndTime(104)
	curTime = t.dateAndTime(104)
	curdate = t.date(104)
	t.setTime('0000')
	##############
	#t.setDate('2023-03-11')
	#curTime = t.dateAndTime(104)
	#curdate = t.date(104)
	#print t.dateAndTime(104)
	###############
	# Get the current time
	current_time = datetime.now()
	#current_time = current_time.replace(hour=00, minute=00)
	#current_time = datetime(2023,03,12, 8, 00)

	startData = current_time - timedelta(hours=113)


	dstNow = checkDaylightSavingsTime(current_time)
	dstStart = checkDaylightSavingsTime(startData)
	offsetMinutes = 0

	if dstNow and dstStart:
		print('All DST')
		offsetHours = 113 #cdt
	elif dstStart:
		print('Fall back - DST is not now but DST is starting time')
		offsetHours = 112 #fall back
		offsetMinutes = 15
	elif dstNow:
		print('Spring ahead - DST is now, but not starting time')
		offsetHours = 113 #cdt
	else:
		print('All standard time')
		offsetHours = 112 #cst		


	
	#offsetHours = 113 #cdt
	#offsetHours = 112 #cst
	
	t.subtractHours(offsetHours) 
	t.addMinutes(offsetMinutes)
	
	t.addHours(6)
	#print t.dateAndTime(104)
	startTime = t.dateAndTime(104)
	
	t.addHours(offsetHours+24*5+6)
	fcstTime = t.dateAndTime(104)
	db.setTimeWindow(startTime, fcstTime)
	print(startTime, curTime)
	
	# Get Data
	# pool
	elev2 = db.get(idelev2)
	#print(elev2.times)
	print(elev2.times[0])
	
	ht = HecTime()
	ht.set(elev2.times[-1])
	print(ht.toString())
	
	
	elev3 = db.get(idelev3)
	
	elev4 = db.get(idelev4)
	
	elev5 = db.get(idelev5)
	elev5a = db.get(idelev5a)
	elev6 = db.get(idelev6)
	elev7 = db.get(idelev7)
	elev8 = db.get(idelev8)
	elev9 = db.get(idelev9)
	elev10 = db.get(idelev10)
	
	# control points
	Stpl = db.get(idelev2c1)
	Sthstpl = db.get(idelev2c2)
	Prsct = db.get(idelev3c1)
	Stlwtr = db.get(idelev3c2)
	Wbsha = db.get(idelev4c1)
	Lkcty = db.get(idelev4c2)
	Alma = db.get(idelev5c)
	Wnona = db.get(idelev6c)
	Dkta = db.get(idelev7c)
	Lcrsse = db.get(idelev8c1)
	Brwnsvl = db.get(idelev8c2)
	Lnsg = db.get(idelev9c)
	Clytn = db.get(idelev10c1)
	Mcggr = db.get(idelev10c2)
	# tail
	tail2 = db.get(idtail2)
	tail3 = db.get(idtail3)
	tail4 = db.get(idtail4)
	tail5 = db.get(idtail5)
	tail5a = db.get(idtail5a)
	tail6 = db.get(idtail6)
	tail7 = db.get(idtail7)
	tail8 = db.get(idtail8)
	tail9 = db.get(idtail9)
	tail10 = db.get(idtail10)
	# flow
	flow2 = db.get(idflow2)
	flow3 = db.get(idflow3)
	flow4 = db.get(idflow4)
	flow5 = db.get(idflow5)
	flow5a = db.get(idflow5a)
	flow6 = db.get(idflow6)
	flow7 = db.get(idflow7)
	flow8 = db.get(idflow8)
	flow9 = db.get(idflow9)
	flow10 = db.get(idflow10)
	# Hydropower
	fordp = db.get(idfordp)
	hydro2 = db.get(idhydro2)
	# gate settings
	ld2tgates = db.get(idld2tgates)
	ld3rgates = db.get(idld3rgates)
	ld4rgates = db.get(idld4rgates)
	ld4tgates = db.get(idld4tgates)
	ld5rgates = db.get(idld5rgates)
	ld5tgates = db.get(idld5tgates)
	ld5argates = db.get(idld5argates)
	ld5atgates = db.get(idld5atgates)
	ld6rgates = db.get(idld6rgates)
	ld6tgates = db.get(idld6tgates)
	ld7rgates = db.get(idld7rgates)
	ld7tgates = db.get(idld7tgates)
	ld8rgates = db.get(idld8rgates)
	ld8tgates = db.get(idld8tgates)
	ld9rgates = db.get(idld9rgates)
	ld9tgates = db.get(idld9tgates)
	ld10rgates = db.get(idld10rgates)
	ld10tgates = db.get(idld10tgates)
	# flow/ft gate opening
	ld2tqft = db.get(idld2tqft)
	ld3rqft = db.get(idld3rqft)
	ld4rqft = db.get(idld4rqft)
	ld4tqft = db.get(idld4tqft) 
	ld5rqft = db.get(idld5rqft) 
	ld5tqft = db.get(idld5tqft) 
	ld5arqft = db.get(idld5arqft) 
	ld5atqft = db.get(idld5atqft) 
	ld6rqft = db.get(idld6rqft) 
	ld6tqft = db.get(idld6tqft) 
	ld7rqft = db.get(idld7rqft) 
	ld7tqft = db.get(idld7tqft) 
	ld8rqft = db.get(idld8rqft) 
	ld8tqft = db.get(idld8tqft) 
	ld9rqft = db.get(idld9rqft) 
	ld9tqft = db.get(idld9tqft) 
	ld10rqft = db.get(idld10rqft) 
	ld10tqft = db.get(idld10tqft) 
	# wind
	ld2ws = db.get(idld2ws)
	ld2wd = db.get(idld2wd)
	ld3ws = db.get(idld3ws)
	ld3wd = db.get(idld3wd)
	ld4ws = db.get(idld4ws)
	ld4wd = db.get(idld4wd)
	ld5ws = db.get(idld5ws)
	ld5wd = db.get(idld5wd)
	#ld5aws = db.get(idld5aws)
	#ld5awd = db.get(idld5awd)
	ld6ws = db.get(idld6ws)
	ld6wd = db.get(idld6wd)
	ld7ws = db.get(idld7ws)
	ld7wd = db.get(idld7wd)
	ld8ws = db.get(idld8ws)
	ld8wd = db.get(idld8wd)
	ld9ws = db.get(idld9ws)
	ld9wd = db.get(idld9wd)
	#ld10ws = db.get(idld10ws)
	#ld10wd = db.get(idld10wd)
	# temp
	ld2atemp = db.get(idld2atemp)
	ld3atemp = db.get(idld3atemp)
	ld4atemp = db.get(idld4atemp)
	ld5atemp = db.get(idld5atemp)
	#ld5aatemp = db.get(idld5aatemp)
	ld6atemp = db.get(idld6atemp)
	ld7atemp = db.get(idld7atemp)
	ld8atemp = db.get(idld8atemp)
	ld9atemp = db.get(idld9atemp)
	#ld10atemp = db.get(idld10atemp)
	# precip
	ld2precip = db.get(idld2precip)
	ld3precip = db.get(idld3precip)
	ld4precip = db.get(idld4precip)
	ld5precip = db.get(idld5precip)
	ld5aprecip = db.get(idld5aprecip)
	ld6precip = db.get(idld6precip)
	ld7precip = db.get(idld7precip)
	ld8precip = db.get(idld8precip)
	ld9precip = db.get(idld9precip)
	ld10precip = db.get(idld10precip)
	ld10forecast = db.get(idld10forecast)
	
	wisconsin = db.read(idWisconsin)
	kick = db.read(idKick)
	wiscoKick = wisconsin.add(kick).getData()
	wisconsin = wisconsin.getData()
	kick = kick.getData()
	
	# Close Database
	db.done()
	#set datasets
	datasets = java.util.Vector()
	# pool
	#print(elev2.getTimeZoneID())
	#print(elev2.getTimes())
	#print(elev2.getTimes())
	datasets.add(elev2)	
	datasets.add(elev3)
	
	
	datasets.add(elev4)	
	datasets.add(elev5)
	datasets.add(elev5a)	
	datasets.add(elev6)
	datasets.add(elev7)	
	datasets.add(elev8)
	datasets.add(elev9)	
	datasets.add(elev10)
	# control points
	datasets.add(Sthstpl)
	datasets.add(Stpl)
	datasets.add(Prsct)
	datasets.add(Stlwtr)
	datasets.add(Wbsha)
	datasets.add(Lkcty)
	datasets.add(Alma)
	datasets.add(Wnona)
	datasets.add(Lcrsse)
	datasets.add(Lnsg)
	datasets.add(Clytn)
	datasets.add(Mcggr)
	# tail
	datasets.add(tail2)	
	datasets.add(tail3)
	datasets.add(tail4)	
	datasets.add(tail5)
	datasets.add(tail5a)	
	datasets.add(tail6)
	datasets.add(tail7)	
	datasets.add(tail8)
	datasets.add(tail9)	
	datasets.add(tail10)
	# flow
	datasets.add(flow2)	
	datasets.add(flow3)
	datasets.add(flow4)	
	datasets.add(flow5)
	datasets.add(flow5a)	
	datasets.add(flow6)
	datasets.add(flow7)	
	datasets.add(flow8)
	datasets.add(flow9)	
	datasets.add(flow10)
	# hydropower
	datasets.add(fordp)
	datasets.add(hydro2)
	# gate settings
	datasets.add(ld2tgates)	
	datasets.add(ld3rgates)
	datasets.add(ld4rgates)	
	datasets.add(ld4tgates)
	datasets.add(ld5rgates)	
	datasets.add(ld5tgates)
	datasets.add(ld5argates)	
	datasets.add(ld5atgates)
	datasets.add(ld6rgates)	
	datasets.add(ld6tgates)
	datasets.add(ld7rgates)	
	datasets.add(ld7tgates)
	datasets.add(ld8rgates)	
	datasets.add(ld8tgates)
	datasets.add(ld9rgates)	
	datasets.add(ld9tgates)
	datasets.add(ld10rgates)	
	datasets.add(ld10tgates)
	# flow/ft gate opening
	datasets.add(ld2tqft)
	datasets.add(ld3rqft) 
	datasets.add(ld4rqft)
	datasets.add(ld4tqft) 
	datasets.add(ld5rqft) 
	datasets.add(ld5tqft) 
	datasets.add(ld5arqft) 
	datasets.add(ld5atqft) 
	datasets.add(ld6rqft) 
	datasets.add(ld6tqft) 
	datasets.add(ld7rqft) 
	datasets.add(ld7tqft) 
	datasets.add(ld8rqft) 
	datasets.add(ld8tqft) 
	datasets.add(ld9rqft) 
	datasets.add(ld9tqft) 
	datasets.add(ld10rqft) 
	datasets.add(ld10tqft) 
	# wind
	datasets.add(ld2ws)
	datasets.add(ld2wd)
	datasets.add(ld3ws)
	datasets.add(ld3wd)
	datasets.add(ld4ws)
	datasets.add(ld4wd)
	datasets.add(ld5ws)
	datasets.add(ld5wd)
	#datasets.add(ld5aws)
	#datasets.add(ld5awd)
	datasets.add(ld6ws)
	datasets.add(ld6wd)
	datasets.add(ld7ws)
	datasets.add(ld7wd)
	datasets.add(ld8ws)
	datasets.add(ld8wd)
	datasets.add(ld9ws)
	datasets.add(ld9wd)
	#datasets.add(ld10ws)
	#datasets.add(ld10wd)
	# temp
	datasets.add(ld2atemp)
	datasets.add(ld3atemp)
	datasets.add(ld4atemp)
	datasets.add(ld5atemp)
	#datasets.add(ld5aatemp)
	datasets.add(ld6atemp)
	datasets.add(ld7atemp)
	datasets.add(ld8atemp)
	datasets.add(ld9atemp)
	#datasets.add(ld10atemp)
	# precip
	datasets.add(ld2precip)
	datasets.add(ld3precip)
	datasets.add(ld4precip)
	datasets.add(ld5precip)
	datasets.add(ld5aprecip)
	datasets.add(ld6precip)
	datasets.add(ld7precip)
	datasets.add(ld8precip)
	datasets.add(ld9precip)
	datasets.add(ld10precip)
	#Added Later
	#Brownsville
	datasets.add(Brwnsvl)
	#Dakota
	datasets.add(Dkta)
	
	datasets.add(ld10forecast)
	datasets.add(wiscoKick)
	datasets.add(wisconsin)
	datasets.add(kick)
	
	
	
	
	###put dataset into table to convert time to Local...not sure why this works
	table = HecDataTableFrame.newTable("Output")
	table.setData(datasets)
	print(elev2.getTimeZoneID())
	print(table.getTimeZone())
	table.setTimeZone(TimeZone.getTimeZone("America/Chicago"))
	print(table.getTimeZone())
	#table.showTable()
	
	
	#set datasets
	
	
	
	#export to excel
	myList = []
	myList.append(datasets)
	
	
	ExcelTable = HecDataTableToExcel.newTable()
	
	
	
	#watershed Path
	watershed_path = Project.getCurrentProject().getProjectDirectory()
	sharedPath = os.path.join(watershed_path,'shared')
	
	
	#desktop path
	user = os.getenv('username')
	desktopPath = "C:\Users\{}\Desktop\DailyRegSheet".format(user)
	##create directory if it doesn't exist
	if not os.path.exists(desktopPath):
		os.makedirs(desktopPath)
	
	#create data dump for excel file to reference
	dsrSheet = os.path.join(desktopPath,'DRS.xlsx')
	ExcelTable.createExcelFile(myList, dsrSheet)
	#os.popen(dsrSheet)
	
	
	#make copy of regsheet so edits aren't made to master sheet
	masterSheet = os.path.join(sharedPath, "DailyRegSheet_Computations.xlsx")
	
	dailySheet = os.path.join(desktopPath, "DailyRegSheet_Computations{}.xlsx".format(curdate))
	shutil.copyfile(masterSheet,dailySheet)
	
	##convert table back to UTC so database view isn't set to UTC...not sure why that works...must be a bug
	table.setTimeZone(TimeZone.getTimeZone("UTC"))
	
	os.popen(dailySheet)
	
	print("Saved Reg Sheet at: {}".format(dailySheet))
	MessageBox.showPlain("Saved Reg Sheet at: {}".format(dailySheet), "Daily Reg Sheet Script")

