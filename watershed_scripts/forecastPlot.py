from hec.heclib.dss import HecDss
from hec.script import Plot, AxisMarker, MessageBox
import os
from hec.heclib.util import HecTime
from com.rma.client import Browser
import datetime
from usace.cavi.action import UploadFileAction
from javax.swing import JOptionPane, JTextArea, JScrollPane
from java.awt  import Component
from com.rma.model import Project
from collections import OrderedDict
import sys
def pathParser(dssPath):
    print
    blank, aPart, bPart, cPart, dPart, ePart, fPart, blank2 = dssPath.split('/')
    return aPart, bPart, cPart, dPart, ePart, fPart
def markerBand(value, label, viewport, color):
    '''
    Adds a horizontal marker to plot viewport
    '''
    from hec.script import AxisMarker
    mb = AxisMarker()
    mb.value = value
    mb.labelText = label
    mb.labelFont = "Arial,Bold,12"
    mb.labelColor = 'gray'
    mb.lineColor = color
    mb.lineWidth = 2.5
    #mb.lineStyle = "Dash Dot-Dot"
    mb.labelPosition = 'below'
    viewport.addAxisMarker(mb)
    return mb
    
def curveFormatter(plot, dataset, lineColor, lineWidth, legendText, lineStyle, fillCurveType):
	'''
	Formats curves (color, width, style)
	'''
	curve = plot.getCurve(dataset)
	curve.setLineColor(lineColor)
	curve.setLineWidth(lineWidth)
	try:
		curve.setLineStyle(lineStyle)
	except:
		print('could not setLinStyle',dataset)
	label = plot.getLegendLabel(dataset)
	label.setText(legendText)
	if fillCurveType == "above":
		curve.setFillColor(lineColor)
		curve.setFillPattern("diagonal cross")
		curve.setFillType("above")
	elif fillCurveType == "below":
		curve.setFillColor(lineColor)
		curve.setFillPattern("diagonal cross")
		curve.setFillType("below")
	return curve
def chktab(tab) :
	'''
	Checks that the "Modeling" tab is selected
	'''
	if tab.getTabTitle() != "Modeling" : 
		msg = "The Modeling tab must be selected"
		output("ERROR : %s" % msg)
		raise Exception(msg)
def chkfcst(fcst) :
	'''
	Checks that a forecast is open
	'''
	if fcst is None : 
		msg = "A forecast must be open"
		output("ERROR : %s" % msg)
		raise Exception(msg)	
def resForecastText(poolPath, 
	outflowPath, 
	storagePath, 
	netInflowPath, 
	currentInflow,
	currentOutflow, 
	currentPool,
	maxStorage, 
	datum,
	datumConversion,
	projectName,
	dssfile, 
	forecast_time, 
	plot_end_string):
	from hec.heclib.util import HecTime
	import datetime
	import os
	def returnData(path, dbPath, startTime, endTime):
		from hec.script import HecDss
		db = HecDss.open(dbPath)
		db.setTimeWindow(startTime, endTime)
		data = db.read(path)
		db.done()
		dataTS = data.getData()
		timeList = dataTS.times
		valueList = dataTS.values
		return data, timeList, valueList
	
	def findMaxLength(lst, hd1, hd2): 
		maxLength = max(max(len(str(int(x))) for x in lst ), len(hd1), len(hd2))
		return maxLength
	## get data from timeseries
	jnk, timeList, poolList = returnData(poolPath, dssfile,forecast_time, plot_end_string)
	jnk, timeList, outflowList = returnData(outflowPath, dssfile,forecast_time, plot_end_string)
	jnk, timeList, storageList = returnData(storagePath, dssfile,forecast_time, plot_end_string)
	jnk, timeList, inflowList = returnData(netInflowPath, dssfile,forecast_time, plot_end_string)
	# calculated the avaiable storage from maxStorage and storage
	storAvailList = []
	for value in storageList:
		storAvail = maxStorage-value
		storAvailList.append(storAvail)
	## replace observed values at forecast time
	inflowList[0] = currentInflow
	outflowList[0] = currentOutflow
	poolList[0] =  currentPool
	# join lists in big list
	combinedList = zip( timeList, inflowList, outflowList, poolList, storageList,storAvailList)
	# create a header list
	headerList = [['Date &', 'Inflow', 'Outflow', 'Pool', 'Storage', 'Stor. Avail.'], ['UTC Time', 'cfs', 'cfs', 'ft '+datum, 'ac-ft','ac-ft']]
	# find the maximum length of the values
	maxLengthList = []
	for tsList, hd1, hd2 in zip(combinedList, headerList[0], headerList[1]):
		maxLengthList.append(findMaxLength(tsList, hd1, hd2))
	# sub in 14 for date time (won't change)
	maxLengthList[0] = 14
	# find the maximum total length of the line
	maxLineLength = sum(maxLengthList)+len(maxLengthList)
	# begin constructing title
	line1String = 'Forecast Summary {}'.format(projectName)
	# center and format and store in outputText variable
	print('\n'*3)
	outputText = '{:^{fill}}'.format(line1String,fill=maxLineLength)
	# generate header output
	for row in headerList:
		outputText +='\n'
		for colHeader, fill in zip(row, maxLengthList):
			outputText += '{:>{fill}}|'.format(colHeader, fill=fill)
	# generate current value output
	outputText += '\n{:-^{fill}}\n'.format('Current Value',fill=maxLineLength)
	time, inflowValue, outflowValue, poolValue, storageValue, storAvail = combinedList[0]
	# create hecTime object so it can be readable
	stringTime = HecTime()
	stringTime.set(time)
	currentValueList = [stringTime.dateAndTime(14),
	'{:,d}'.format(int(inflowValue)),
	'{:,d}'.format(int(outflowValue)), 
	'{:.2f}'.format(float(poolValue)+float(datumConversion)), 
	'{:,d}'.format(int(storageValue)), 
	'{:,d}'.format(int(storAvail))]
	for value, fill in zip(currentValueList, maxLengthList):
		outputText += '{:>{fill}}|'.format(value, fill=fill)
	# begin forecast output
	outputText += '\n{:-^{fill}}\n'.format('Forecast',fill=maxLineLength)
	for row in combinedList[1::]:
		time, inflowValue, outflowValue, poolValue, storageValue, storAvail = row
		stringTime = HecTime()
		stringTime.set(time)
		if stringTime.hour() == 12:
			currentValueList = [stringTime.dateAndTime(14),
			'{:,g}'.format(round(inflowValue,0)),
			'{:,g}'.format(round(outflowValue,0)), 
			'{:.2f}'.format(poolValue+datumConversion), 
			'{:,g}'.format(round(storageValue,-1)), 
			'{:,g}'.format(round(storAvail,-1))]
			
			for value, fill in zip(currentValueList, maxLengthList):
				outputText += '{:>{fill}}|'.format(value, fill=fill)
			outputText += '\n'
	#make end of table border
	outputText +='-'*maxLineLength
	# put issued note on forecast
	line2String ='\nIssued {:%b %d, %Y %I:%M %p} local time by {}'.format(datetime.datetime.now(), os.getenv('username'))
	outputText += '{:<{fill}}'.format(line2String,fill=maxLineLength)
	# put expiration note on forecast
	line2String ='\nValid through {:%b %d, %Y 10 AM local time}'.format((datetime.datetime.now() + datetime.timedelta(days=1)))
	outputText += '{:<{fill}}'.format(line2String,fill=maxLineLength)
	return outputText
################## Get Forecast ###########################################
## This section finds the current forecast.dss file (i.e. active forecast) ##
## Get the current forecast ##
frame = Browser.getBrowser().getBrowserFrame()
proj = frame.getCurrentProject()
pane = frame.getTabbedPane()
tab = pane.getSelectedComponent()
chktab(tab)
fcst = tab.getForecast()
fcstTimeWindowString = str(fcst.getRunTimeWindow())
fcstNames = fcst.getForecastRunNames()
fcstRun = tab.getActiveForecastRun() ###get active forecast
fcstRunKey = fcstRun.getKey()
fPart = fcstRunKey[:6]
#for p in path:
#	print p
dssPath = fcst.getOutDssPath()
scriptPath = os.path.join(dssPath.split('forecast')[0], 'watershed', str(proj),'scripts').replace("\\","/")
if scriptPath not in sys.path:
	sys.path.insert(0,scriptPath)
    
    
###########################################Read arguments from CSV file
watershed_path = Project.getCurrentProject().getProjectDirectory()
sharedPath = os.path.join(watershed_path,'shared')
filePath = os.path.join(sharedPath,'projectForecastPlotInputs.csv') 
#############################
#dictionary we will put stuff in from input file
dataDict = OrderedDict()
#grab inputs from file and put into dictionary
with open(filePath, mode='r') as f:
    lines = f.readlines()
    #walk through input file starting on line 2
    for line in lines[1::]:
        #print(line)
        #grab dict key from first item
        projectKey = line.split(',')[0]
        param = line.split('\n')[0].split(',')[1::]
        #store data  in dictionary 
        if projectKey not in dataDict:
            dataDict[projectKey] = OrderedDict()
        dataDict[projectKey] = param

if len(dataDict.keys())>1:
	projectName = JOptionPane.showInputDialog(None,
	"Choose Project",'Forecast',
	JOptionPane.PLAIN_MESSAGE,None,
	dataDict.keys(),dataDict.keys()[0])
else:
	projectName = dataDict.keys()[0]

params = dataDict[projectName]
# put params from selected project into variables
resSimReservoirName, datum, lookBack, lookAhead, datumConversion, obsPoolPath, poolPath2,\
poolPath3, obsOutflowPath, obsOutflow2Path, obsNetInflowPath, fcstDssFileName, \
ncrfcForecastPaths, stageMarkers, flowMarkers, maxStorage, showGc, ElevationOrStage, \
forecastInflowLegendText, inflowLegendText, nwsFpart, hmsRainOnGroundFparts, \
hmsQPFfparts, nws0dayFpart, nws7dayFpart = params
if showGc.lower == 'true':
	showGc = True
else:
	showGc = False



forecastType = ['View Only', "Internal Forecast Graphic Post","Public Forecast Graphic Post", "Internal 28 Day Graphic Post","Public 28 Day Text Post", 
"Remove Public Forecast Graphic", "Remove Public 28 Day Text", "Edit Plot Inputs"]
forecastTypeSelected = JOptionPane.showInputDialog(None,"Choose Forecast Type",'Forecast',JOptionPane.PLAIN_MESSAGE,None,forecastType,forecastType[0])
print(forecastTypeSelected)
if str(forecastTypeSelected) == "None" :
	sys.exit()
frame = Browser.getBrowser().getBrowserFrame()



###########################################Plotting script
## use for different titles
echPath = r'\\mvd\mvp\ECH2\Library\WM\CWMS\Forecasts\Graphs_Texts'
#projSummaryText = '<html><b>%s Forecast</b></html>\n<html>Forecast valid through %s</html>'%(projectName, (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("10 AM local time %b %d, %Y"))
projSummaryText = '<html><b>CUI/WATER/FED ONLY - %s Forecast</b></html>\n<html>Forecast issued %s</html>'%(projectName, (datetime.datetime.now()).strftime("%b %d, %Y"))
plotName = "%sForecast_%s.png"%(projectName.replace(" ", ""),datetime.datetime.now().strftime("%Y-%m-%d_%H%M"))
print(forecastTypeSelected)
if "Internal" in forecastTypeSelected:
	cwmsPath = '/wm/mvp/wm_web/var/apache2/2.4/htdocs/graphs/internal'
elif forecastTypeSelected == "Public 28 Day Text Post" or forecastTypeSelected == "Remove Public 28 Day Text":
	cwmsPath = '/wm/mvp/wm_web/var/apache2/2.4/htdocs/graphs/monthlyOutlookText'
elif forecastTypeSelected == "Public Forecast Graphic Post" or forecastTypeSelected == "Remove Public Forecast Graphic":
	cwmsPath = '/wm/mvp/wm_web/var/apache2/2.4/htdocs/graphs'
	projSummaryText = projSummaryText.replace('CUI/WATER/FED ONLY - ','')
else:
	cwmsPath = None
#if remove public forecast
if forecastTypeSelected == "Remove Public Forecast Graphic":
	#reference forecast unavail png from network
	src =  os.path.join(sharedPath,'forecastUnavailable.png')
	#refence forecast plot on CWMS server
	fileNameCWMS = os.path.join(cwmsPath ,'{}.Forecast.png'.format(projectName.replace(" ", "_"))) 
	dest = fileNameCWMS
	print(src) 
	print(dest)
	action = UploadFileAction()
	worked = action.uploadFile(src, dest, False, 0)
	if worked:
		print("Overwrite {} successful to CWMS server: {}".format(fileNameCWMS,worked))
		MessageBox.showInformation("Overwrote public forecast for {} with blank image".format(projectName), "Success")
	else:
		print("Overwrite {} failed to CWMS server: {}".format(fileNameCWMS,worked))
		MessageBox.showInformation("Failed to overwrite public forecast with blank image for {}".format(projectName), "Failed")
elif forecastTypeSelected == "Remove Public 28 Day Text":
	#reference blank txt
	src = os.path.join(sharedPath,'forecastUnavailable.png')
	#refence forecast plot on CWMS server
	fileNameCWMS = os.path.join(cwmsPath ,projectName.replace(" ", "")+'_monthlyOutlook.txt') 
	dest = fileNameCWMS
	print(src) 
	print(dest)
	action = UploadFileAction()
	worked = action.uploadFile(src, dest, False, 0)
	if worked:
		print("Overwrite {} successful to CWMS server: {}".format(fileNameCWMS,worked))
		MessageBox.showInformation("Overwrote public forecast for {} with blank text".format(projectName), "Success")
	else:
		print("Overwrite {} failed to CWMS server: {}".format(fileNameCWMS,worked))
		MessageBox.showInformation("Failed to overwrite public forecast for {} with blank text".format(projectName), "Failed")
elif forecastTypeSelected == "Edit Plot Inputs":
	os.popen(filePath)
else:
	print(forecastTypeSelected, 'internal' in forecastTypeSelected)
	if 'Internal' in forecastTypeSelected:
		plotNameCwmsServer =  "%s.Forecast.Internal.png"%(projectName.replace(" ", "_"))
		inflowNeg = True
	else:
		plotNameCwmsServer =  "%s.Forecast.png"%(projectName.replace(" ", "_"))
		inflowNeg = False
	###################
	########################open up and run script
	#########################
	dssfile = fcst.getOutDssPath()
	cwmsFile = HecDss.open(dssfile)
	important_times = [ i.strip(' ') for i in fcstTimeWindowString.split(';') ]
	start_time, forecast_time, end_time = important_times[0], important_times[1], important_times[2]
	if forecastTypeSelected == 'View Only':
			fullForecast = JOptionPane.showConfirmDialog(None,"Show shortened lookback and forecast?")
	elif forecastTypeSelected == 'Internal 28 Day Graphic Post' or forecastTypeSelected == 'Public 28 Day Text Post':
		fullForecast = 28
	else:
		fullForecast=0
		
	if fullForecast==0:
		plot_start = HecTime()
		plot_start.set(forecast_time)
		plot_start.addDays(-int(lookBack))
		plot_start_string = str(plot_start)
		plot_end = plot_start.addDays(int(lookBack)+int(lookAhead))
		plot_end_string = str(plot_start)
		cwmsFile.setTimeWindow(plot_start_string, plot_end_string)
	elif fullForecast==28:
		plot_start = HecTime()
		plot_start.set(forecast_time)
		plot_start.addDays(-int(7))
		plot_start_string = str(plot_start)
		plot_end = plot_start.addDays(int(7)+int(28))
		plot_end_string = str(plot_start)
		cwmsFile.setTimeWindow(plot_start_string, plot_end_string)
		projSummaryText = '<html><b>%s Outlook - CUI</b></html>\n<html>Forecast issued %s</html>'%(projectName, (datetime.datetime.now()).strftime("%b %d, %Y %H:00"))
	else:
		try:
			print('maxLookbackTime = {}'.format(maxLookbackTime))
			maxLookbackTime=int(maxLookbackTime)
		except NameError:
			print("maxLookbackTime not defined, default 7 days")
			maxLookbackTime=7
		#projSummaryText = '<html><b>%s Outlook - CUI</b></html>\n<html>Forecast valid through %s</html>'%(projectName, (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("10 AM local time %b %d, %Y"))
		
		plot_start = HecTime()
		plot_start.set(start_time)
		forecastHecTime = HecTime()
		forecastHecTime.set(forecast_time)
		if forecastHecTime.julian()-plot_start.julian()>maxLookbackTime:
			daysToAdd = forecastHecTime.julian()-maxLookbackTime-plot_start.julian()
		else:
			daysToAdd = 0
		plot_start.addDays(daysToAdd)
		plot_start_string = str(plot_start)
		plot_end_string = end_time
		cwmsFile.setTimeWindow(plot_start_string, end_time)
	#offset by 1 hour to avoid the current time value in the forecast
	timeObj= HecTime()
	timeObj.set(forecast_time)
	timeObj.addHours(1)
	forecast_time = str(timeObj)
	########################get data
	#define ResSim data paths
	#try block to resolve issue with resSim fPart only having two characters instead of 6
	try:
		drawdownCurvePath = "//"+resSimReservoirName+"-CONSERVATION/ELEV-ZONE//1HOUR/"+fPart
		GC = cwmsFile.read(drawdownCurvePath)
	except:
		fPart = fPart[0:2]
		print(fPart)
		drawdownCurvePath = "//"+resSimReservoirName+"-CONSERVATION/ELEV-ZONE//1HOUR/"+fPart
		GC = cwmsFile.read(drawdownCurvePath)
	storagePath = "//"+resSimReservoirName+"-POOL/STOR//1HOUR/"+fPart
	poolPath = "//"+resSimReservoirName+"-POOL/ELEV//1HOUR/"+fPart
	outflowPath = "//"+resSimReservoirName+"-POOL/FLOW-OUT//1HOUR/"+fPart
	inflowForecastPath = "//"+resSimReservoirName+"-Pool/FLOW-IN//1HOUR/"+fPart
	netInflowPath = "//"+resSimReservoirName+"-Pool/FLOW-IN NET//1HOUR/"+fPart #subtracts evap and losses
	evapPath = "//"+resSimReservoirName+"-Pool/FLOW-EVAP//1HOUR/"+fPart
	########get observed data
	cwmsFile.setTimeWindow(plot_start_string, forecast_time)
	obsPool = cwmsFile.read(obsPoolPath)
	try:
		obsOutflow = cwmsFile.read(obsOutflowPath)
	except NameError:
		print("obsOutflowPath not defined")
	obsStorage = cwmsFile.read(storagePath)	
	currentPool = cwmsFile.read(obsPoolPath).lastValidValue()
	try:
		currentOutflow = cwmsFile.read(obsOutflowPath).lastValidValue()
	except NameError:
		currentOutflow = -9999
	try:
		currentInflow = cwmsFile.read(obsNetInflowPath).lastValidValue()
		obsNetInflow = cwmsFile.read(obsNetInflowPath).screenWithMaxMin(0.0, 1000000.0, 1000000.0, 1, 0.0, "Q")
	except NameError:
		currentInflow = -9999
	###########get forecasted data
	cwmsFile.setTimeWindow(forecast_time, plot_end_string)
	netInflow = cwmsFile.read(netInflowPath)
	##screen inflow
	if not inflowNeg:
		netInflow = netInflow.screenWithMaxMin(0.0, 1000000.0, 1000000.0, 1, 0.0, "Q")
	inflowForecast = cwmsFile.read(inflowForecastPath)
	forecastPool = cwmsFile.read(poolPath)
	forecastOutflow = cwmsFile.read(outflowPath)
	forecastStorage = cwmsFile.read(storagePath)
	cwmsFile.done()
	## convert datum conversion to float
	datumConversion = float(datumConversion)
	if abs(datumConversion)>0:
		obsPool = obsPool.add(datumConversion)
		forecastPool = forecastPool.add(datumConversion)
	## maxStorage to float
	maxStorage = float(maxStorage)
	######################pool uncertainty
	try:
		#get upper and lower limits at end of forecast time
		poolUpperLimFcstWind = currentPool+float(poolUncertHigh)
		poolLowerLimFcstWind = currentPool-float(poolUncertLow)
		# get number of timesteps
		n = len(forecastPool.getData().values)
		#create upper limit timeseries
		forecastPoolUpperTSC = forecastPool.getData().clone()
		forecastPoolUpperTSC.fullName = forecastPool.getData().fullName[:-1]+'-Upper Limit/'
		#create lower limit timeseries
		forecastPoolLowerTSC = forecastPool.getData().clone()
		forecastPoolLowerTSC.fullName = forecastPool.getData().fullName[:-1]+'-Lower Limit/'
		#start loop to write values in upper and lower limit timeseries
		for i in range(0,n):
			#linear inerpolate limit value
			upperValue = float(i)/(n-1)*float(poolUncertHigh)+forecastPool.getData().values[i]
			#apply hard code limit
			upperValue = upperValue if upperValue<float(poolForecastCeiling) else float(poolForecastCeiling)
			#linear inerpolate limit value
			lowerValue = forecastPool.getData().values[i]-float(i)/(n-1)*float(poolUncertLow)
			#apply hard code limit
			lowerValue = lowerValue if lowerValue>float(poolForecastFloor) else float(poolForecastFloor)
			#write values to timeseries
			forecastPoolUpperTSC.values[i]=upperValue
			forecastPoolLowerTSC.values[i]=lowerValue
	except NameError:
		print('poolUncertHigh and poolUncertLow are not defined')
	##################
	## Create plot	##
	##################
	plot = Plot.newPlot("")
	layout = Plot.newPlotLayout()
	poolView = layout.addViewport(50)
	FlowView = layout.addViewport(50)
	try:
		poolView.addCurve("Y1", forecastPoolUpperTSC)
		poolView.addCurve("Y1", forecastPoolLowerTSC)
	except NameError:
		print('poolUncertHigh and poolUncertLow are not defined')
	poolView.addCurve("Y1", obsPool.getData())
	poolView.addCurve("Y1", forecastPool.getData())
	try:
		FlowView.addCurve("Y1", obsOutflow.getData())
	except NameError:
		print('obsOutflow are not defined')
	FlowView.addCurve("Y1", forecastOutflow.getData()) 
	try:
		FlowView.addCurve("Y1", obsNetInflow.getData())
	except NameError:
		print('obsNetInflow are not defined')
	try:
		FlowView.addCurve("Y1", netInflow.getData())
	except NameError:
		print('netInflow are not defined')
	##show guide curve option
	try:
		if showGc:
			poolView.addCurve("Y1", GC.getData())
	except:
		print("showGc not defined")
	# Add Layout Properties
	layout.setHasLegend(True)
	layout.setHasToolbar(True)
	plot.configurePlotLayout(layout)
	plot.setSize(960, 640)
	panel = plot.getPlotpanel()
	panel.setHorizontalViewportSpacing(1)
	plot.showPlot()
	plot.getViewport(obsPool.getData()).getAxis('Y1').setLabel('Pool Elevation, ft %s'%datum)
	plot.getViewport(forecastOutflow.getData()).getAxis('Y1').setLabel('Flow, cfs')
	# Create Plot Title Text
	plotTitle = plot.getPlotTitle()
	plotTitle.setText(projSummaryText)
	#plotTitle.setAlignment('center')
	#plotTitle.setFont("Arial Black")
	plotTitle.setFontSize(18)
	plot.setPlotTitleVisible(1)
	## Plot Line Styles
	curveFormatter(plot, obsPool.getData(), "blue", 3, "Obs. Pool Elevation", None, None)
	try:
		curveFormatter(plot, obsOutflow.getData(), "red", 1.5, "Obs. Outflow", None, None)
	except NameError:
		None
	try:
		curveFormatter(plot, obsNetInflow.getData(), "black", 1.5, inflowLegendText, None, None)
	except NameError:
		print("inflowLegendText not defined")
	try:
		curveFormatter(plot, obsNetInflow.getData(), "black", 1.5, "Obs. Inflow", None, None)
	except NameError:
		print("obsNetInflow not defined")
	curve = curveFormatter(plot, forecastPool.getData(), "blue", 3, "Forecasted Pool Elevation",  "dash", None)
	#curve.setSymbolsVisible(True)
	#curve.setSymbolSkipCount(6)
	#curve.setSymbolFillColor('blue')
	#curve.setSymbolLineColor('blue')
	#curve.setSymbolType('Pipe')
	#curve.setSymbolSize(48)
	curveFormatter(plot, forecastOutflow.getData(), "red", 1.5, "Forecasted Outflow",  "dash", None)
	try:
		if forecastInflowLegendText == '':
			if fPart in nwsFpart:
				forecastInflowLegendText = 'NWS NCRFC Inflow'
			elif fPart in hmsRainOnGroundFparts:
				forecastInflowLegendText = 'Forecasted HMS Inflow (No Future Precip.)'
			elif fPart in hmsQPFfparts:
				forecastInflowLegendText = 'Forecasted HMS Inflow (7 day Fcst Precip.)'			
			elif fPart in nws0dayFpart:
				forecastInflowLegendText = 'Forecasted NWS Inflow (No Future Precip.)'
			elif fPart in nws7dayFpart:
				forecastInflowLegendText = 'Forecasted NWS Inflow (7 day Fcst Precip.)'
			else:
				forecastInflowLegendText = 'Forecasted Inflow'
		curve = curveFormatter(plot, netInflow.getData(), "black", 1.5, forecastInflowLegendText, "dash", None)
	except NameError:
		print("forecastInflowLegendText not defined")
		curve = curveFormatter(plot, netInflow.getData(), "black", 1.5, "Forecasted Inflow (NWS)", "dash", None)
	#curve.setSymbolsVisible(True)
	#curve.setSymbolSkipCount(48)
	#curve.setSymbolFillColor('black')
	#curve.setSymbolLineColor('black')
	#curve.setSymbolType('Pipe')
	#curve.setSymbolSize(24)
	##show guide curve option
	try:
		curve = curveFormatter(plot, forecastPoolUpperTSC, 'blue', .2, "upper", 'dash', None)
		#light blue '173, 216, 230'
		#curve.setSymbolsVisible(True)
		#curve.setSymbolSkipCount(4)
		#curve.setSymbolFillColor('blue')
		#curve.setSymbolLineColor('blue')
		#curve.setSymbolType('-')
		#curve.setSymbolSize(1)
		curve.setFillColor('blue')
		curve.setFillPattern("FDiagonal")
		curve.setFillType("below")
		plot.getLegendLabel(forecastPoolUpperTSC).hide()
		curve = curveFormatter(plot, forecastPoolLowerTSC, "blue", .2, "lower", 'dash', None)
		#curve.setSymbolsVisible(True)
		#curve.setSymbolSkipCount(4)
		#curve.setSymbolFillColor('blue')
		#curve.setSymbolLineColor('blue')
		#curve.setSymbolType('-')
		#curve.setSymbolSize(1)
		curve.setFillColor('white')
		curve.setFillPattern("FDiagonal")
		curve.setFillType("below")
		plot.getLegendLabel(forecastPoolLowerTSC).hide()
	except NameError:
		print('poolUncertHigh and poolUncertLow are not defined')
	##show pool uncertainty option
	try:
		curveFormatter(plot, GC.getData(), "lightpurple", 1, "Drawdown Curve", 'dash', None)
	except:
		print("showGc not defined")
	# X Axes Marker
	markerCurTime = AxisMarker()
	markerCurTime.axis = "X1"
	markerCurTime.value = forecast_time
	markerCurTime.labelText = "Forecast Time: "+forecast_time+" UTC"
	markerCurTime.labelFont = "Arial,14"
	markerCurTime.labelPosition = "center"
	markerCurTime.labelAlignment = "center"
	markerCurTime.lineWidth = 1.0
	markerCurTime.lineStyle = "Dot"
	plot.getViewport(obsPool.getData()).addAxisMarker(markerCurTime)
	markerCurTime.labelText = ''
	plot.getViewport(forecastOutflow.getData()).addAxisMarker(markerCurTime)
	## plot marker bands
	try:
		markerBand(str(drawdownTarget), 'Drawdown Target', plot.getViewport(obsPool.getData()), 'darkorange')
	except NameError:
		print("drawdownTarget not defined")
	try:
		markerBand(channelCapacity, '{:,} cfs - Bankfull Discharge'.format(int(channelCapacity)), plot.getViewport(obsOutflow.getData()), 'gray')
	except NameError:
		print("channelCapacity not defined")
	try:
		markerBand(topConservation, 'Top of conservation', plot.getViewport(obsPool.getData()), 'darkorange')
	except NameError:
		print("topConservation not defined")
	try:
		markerBand(bottomConservation, 'Bottom of conservation', plot.getViewport(obsPool.getData()), 'darkorange')
	except NameError:
		print("bottomConservation not defined")
	try:
		markerBand(str(conservation),'Conservation', plot.getViewport(obsPool.getData()), 'darkorange')
	except NameError:
		print("conservation not defined")
	try:
		for a in stageMarkers.split('|'):
			num, comment, color =  a.split(';')
			markerBand(num,comment.strip(), plot.getViewport(obsPool.getData()), color.strip())
	except ValueError:
		print("stageMarkers not defined")
	try:
		for a in flowMarkers.split('|'):
			num, comment, color =  a.split(';')
			markerBand(num,comment.strip(), plot.getViewport(obsOutflow.getData()), color.strip())
	except ValueError:
		print("flowMarkers not defined")
	###output text table
	outputText =resForecastText(poolPath, 
		outflowPath, 
		storagePath, 
		netInflowPath, 
		currentInflow,
		currentOutflow, 
		currentPool,
		maxStorage, 
		datum,
		datumConversion,
		projectName,
		dssfile, 
		forecast_time, 
		plot_end_string)
	print(outputText)
	print('\n'*3)
	### try and get 28 day change in pool-Drought outlook
	if fullForecast==28:
		dtFormat = '%d %B %Y, %H:%M'
		startDT = datetime.datetime.strptime(forecast_time, dtFormat)
		endDT = datetime.datetime.strptime(plot_end_string, dtFormat)
		diffDT = endDT - startDT
		maxDaysToLookAhead = 28
		# use 28 days if forecast extends that far, else use how long it extends
		if datetime.timedelta(days=maxDaysToLookAhead)>diffDT:
			end_string = (startDT+datetime.timedelta(days=maxDaysToLookAhead)).strftime(dtFormat)
		else:
			end_string = plot_end_string
		#set time window
		cwmsFile.setTimeWindow(forecast_time, plot_end_string)
		netInflow = cwmsFile.read(netInflowPath)
		forecastInflow = cwmsFile.read(inflowForecastPath)
		forecastPool = cwmsFile.read(poolPath)
		forecastOutflow = cwmsFile.read(outflowPath)
		forecastStorage = cwmsFile.read(storagePath)
		forecastEvap = cwmsFile.read(evapPath)
		poolChange = forecastPool.lastValidValue() - forecastPool.firstValidValue()
		storageChange = forecastStorage.lastValidValue() - forecastStorage.firstValidValue()
		#print(sum(list(netInflow.getData().values)))
		netInflowAvg = sum(list(netInflow.getData().values))/len(list(netInflow.getData().values))
		netInflowVolume = netInflowAvg*0.08264
		inflowAvg = sum(list(forecastInflow.getData().values))/len(list(forecastInflow.getData().values))
		outflowAvg = sum(list(forecastOutflow.getData().values))/len(list(forecastOutflow.getData().values))
		outflowVolume = outflowAvg*0.08264
		evapAvg = sum(list(forecastEvap.getData().values))/len(list(forecastEvap.getData().values))
		
		msg = """{} {} Day Outlook\nChange in Pool = {:.2f} ft\n
#Change in Pool Storage = {:,d} acre-ft
#Net Inflow Volume = {:,d} acre-ft
#Outflow Volume = {:,d} acre-ft
#Average Net Inflow = {:,d} cfs
Average Inflow = {:,d} cfs
Average Outflow = {:,d} cfs
Average Evap. Loss Rate = -{:,d} cfs\n""".format(projectName, 
		diffDT.days, 
		poolChange, 
		int(storageChange), 
		int(netInflowVolume), 
		int(outflowVolume),
		int(netInflowAvg),
		int(inflowAvg),
		int(outflowAvg),
		int(evapAvg))
		if abs(poolChange)<=0.1:
			outlookMsg = '{} One Month Drought Outlook issued {}: Steady pool level forecasted over next 28 days assuming no forecasted rain, no change in outflow, and average losses from evaporation.'.format(projectName, (datetime.datetime.now()).strftime("%b %d, %Y"))
		else:
			outlookMsg = '{} One Month Drought Outlook issued {}: Change in Pool = {:.1f} ft forecasted over next 28 days assuming no forecasted rain, no change in outflow, and average losses from evaporation.'.format(projectName, (datetime.datetime.now()).strftime("%b %d, %Y"), poolChange)
		print(msg)
		print(outlookMsg)
		#update project Text
		#projSummaryText = '<html><b>{} 28 Day Outlook - CUI</b></html>\nChange in Pool Elev. = {:.2f}ft\n<html>Forecast issued {}</html>'.format(projectName, str(diffDT.days), poolChange, (datetime.datetime.now()).strftime("%b %d, %Y"))
		projSummaryText = '<html><b>CUI/WATER/FED ONLY - {} 28 Day Outlook</b></html>\nChange in Pool Elev. = {:.2f}ft\n<html>Forecast issued {}</html>'.format(projectName, poolChange, (datetime.datetime.now()).strftime("%b %d, %Y"))
		plotTitle.setText(projSummaryText)
		#MessageBox.showInformation(msg, "Drought Outlook")
		
	#	##screen inflow
	#	if not inflowNeg:
	#		netInflow = netInflow.screenWithMaxMin(0.0, 1000000.0, 1000000.0, 1, 0.0, "Q")
	#	inflowForecast = cwmsFile.read(inflowForecastPath)
	#	forecastPool = cwmsFile.read(poolPath)
	#	forecastOutflow = cwmsFile.read(outflowPath)
	#	forecastStorage = cwmsFile.read(storagePath)
	#	forecastPool.times()
	#	print(forecastPool.lastValidValue())
	#Option to save plot and output text
	savePlot = False
	if 'Internal' in forecastTypeSelected:
		savePlot = JOptionPane.showConfirmDialog(None,"Save Figure and Post to Intranet?")
	elif "View" in forecastTypeSelected:
		savePlot = JOptionPane.showConfirmDialog(None,"Save Figure and Data to ECH?")
	elif forecastTypeSelected == "Public 28 Day Text Post":
		t = JTextArea(text = outlookMsg,
		              editable = True,
		              wrapStyleWord = True,
		              lineWrap = True,
		              alignmentX = Component.LEFT_ALIGNMENT,
		              size = (300, 100)
		              )
		        
		mypane = JScrollPane(t)
		savePlot = JOptionPane.showConfirmDialog(None, mypane, "Save 28 Day Outlook Text to Website?", JOptionPane.YES_NO_OPTION, 1)
		
	else:
		savePlot = JOptionPane.showConfirmDialog(None,"Save Figure and Post to Public Website?")
	if savePlot==0:
		if forecastTypeSelected != "Public 28 Day Text Post":
			## save figure and text file to ECH server
			fileName = os.path.join(echPath,plotName)
			print("saved chart to "+ fileName)
			plot.saveToPng(fileName)
			textFileName = fileName.split('.png')[0]+'.txt'
			textFile = open(textFileName, 'w')
			textFile.write(outputText)
			textFile.close()
			print("saved text file to "+ textFileName)
			## Export data to dssFile
			try:
				fcstDssFileName = os.path.join(echPath,fcstDssFileName)
			except:
				#create dssFileName if not defined in args
				fcstDssFileName = os.path.join(echPath,'{}_forecast.dss'.format(projectName.replace(' ','')))
			serverForecastDb = HecDss.open(fcstDssFileName)
			serverForecastDb.setTimeWindow(forecast_time, end_time)
			# forecast data to save, grab from DB again to get extended forecast
			datapathsToSave = [poolPath, outflowPath, inflowForecastPath]
			serverForecastDb = HecDss.open(fcstDssFileName)
			cwmsFile = HecDss.open(dssfile)
			cwmsFile.setTimeWindow(forecast_time, end_time)
			for path in datapathsToSave:
				forecastData = cwmsFile.read(path)
				forecastData.setVersion('fcst_{:%Y-%m-%d}'.format(datetime.datetime.today()))
				serverForecastDb.write(forecastData)
			cwmsFile.done()
			serverForecastDb.setTimeWindow(start_time, end_time)
			#observed data to save
			try:
				dataToSave = [obsPool, obsOutflow, obsNetInflow]
			except:
				try:
					dataToSave = [obsPool, obsOutflow]
				except:
					dataToSave = [obsPool]
			for obsData in dataToSave:
				obsData.setVersion('obs')
				serverForecastDb.write(obsData)
			serverForecastDb.done()
			print("saved forecast data to file to "+ fcstDssFileName)
			# ncrfc forecasts to archive
			try:
				if ncrfcForecastPaths:
					cwmsFile = HecDss.open(dssfile)
					serverForecastDb = HecDss.open(fcstDssFileName)
					for path in ncrfcForecastPaths.split(';'):
						try:
							data = cwmsFile.read(path)
						except:
							print("could not read {}".format(path))
							cwmsFile.done()
						serverForecastDb.done()
						data.setVersion('ncrfcFcst_{:%Y-%m-%d}'.format(datetime.datetime.today()))
						serverForecastDb.write(data)
					cwmsFile.done()
					serverForecastDb.done()
				print("saved ncrfc data to file to "+ fcstDssFileName)
			except NameError:
				print('ncrfcForecastPaths variable not defined')
		#28 day save
		else:
			outlookMsg = t.getText()
			fName = projectName.replace(" ", "")+'_monthlyOutlook.txt'
			text28dayFileName = os.path.join(echPath, fName)
			text28dayFile = open(text28dayFileName, 'w')
			text28dayFile.write(outlookMsg)
			text28dayFile.close()
			print("saved 28 day outlook text file to "+ text28dayFileName)	
			#save 28 day text to CWMS server
			src = text28dayFileName
			fileNameCWMS = os.path.join(cwmsPath ,fName) 
			dest = fileNameCWMS
			action = UploadFileAction()
			worked = action.uploadFile(src, dest, False, 0)
			#worked = True
			if worked:
				print("Upload {} successful to CWMS server: {}".format(fileNameCWMS,worked))
				MessageBox.showInformation("Upload {} successful to CWMS server: {}".format(fileNameCWMS,worked), "Success")
			else:
				print("Upload {} failed to CWMS server: {}".format(fileNameCWMS,worked))
				MessageBox.showInformation("Upload {} failed to CWMS server: {}".format(fileNameCWMS,worked), "Failed")
		if forecastTypeSelected == "Internal 28 Day Graphic Post"\
			 or forecastTypeSelected == "Internal Forecast Graphic Post"\
			 or forecastTypeSelected == "Public Forecast Graphic Post":
			## save figure CWMS server
			fileNameCWMS = os.path.join(cwmsPath,plotNameCwmsServer)
			src = fileName
			dest = fileNameCWMS
			action = UploadFileAction()
			worked = action.uploadFile(src, dest, False, 0)
			#worked = True
			if worked:
				print("Upload {} successful to CWMS server: {}".format(fileNameCWMS,worked))
				MessageBox.showInformation("Upload {} successful to CWMS server: {}".format(fileNameCWMS,worked), "Success")
			else:
				print("Upload {} failed to CWMS server: {}".format(fileNameCWMS,worked))
				MessageBox.showInformation("Upload {} failed to CWMS server: {}".format(fileNameCWMS,worked), "Failed")
				
			
	
print('Finished - exit')
