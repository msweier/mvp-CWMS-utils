import DBAPI, hec
from hec.script import Plot, AxisMarker, MessageBox
from hec.heclib.util import HecTime
from java.util import Calendar, TimeZone
from java.lang import System
from javax.swing import JOptionPane, JTextArea, JScrollPane
from collections import OrderedDict
from hec.cwmsVue import CwmsListSelection
from hec.script import AxisMarker

def pathParser(dssPath):
    blank, aPart, bPart, cPart, dPart, ePart, fPart, blank2 = dssPath.split('/')
    return aPart, bPart, cPart, dPart, ePart, fPart
def markerBand(value, label, viewport, color):
    '''
    Adds a horizontal marker to plot viewport
    '''
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
					
def getDataIfExists(tsID):
	try:
		data = db.read(tsID)
		return data
	except:
		print('Error: Data in {} does not exists for time window'.format(tsID))

def lastValidDateString(tsData):
	intTime = tsData.lastValidDate()
	lastTime = HecTime(cal)
	lastTime.set(intTime)
	print(intTime)
	print(lastTime)
	print(lastTime.dateAndTime(104))
	return lastTime.dateAndTime(104)

try:
# Add rtsutils package to sys.path before importing
    sys.path.append(os.path.join(os.environ['APPDATA'], "rsgis"))
    from rtsutils import cavistatus, usgs
except ImportError, ex:
    raise

##read imputs from file

filePath = os.path.join(
    cavistatus.get_shared_directory(),
    'projectDBplotInputs.csv'
    )
print(filePath)
daysToLookBack = 10
daysToLookForward = 7

#############################
#dictionary we will put stuff in from input file
dataDict = OrderedDict()
#grab inputs from file and put into dictionary
with open(filePath, mode='r') as f:
	lines = f.readlines()
	#walk through input file starting on line 2
	for line in lines[1::]:
		print(line)
		#grab dict key from first item
		watershedKey = line.split(',')[0]
		siteKey = line.split(',')[1]
		param = line.split('\n')[0].split(',')[2::]
		#store data  in dictionary 
		if watershedKey not in dataDict:
			dataDict[watershedKey] = OrderedDict()
		dataDict[watershedKey][siteKey] = param

watershedList = list(dataDict.keys())
#Calls the JOptionPane funtion:  showInputDialog(Parent Component, Message, Title, MessageType, Icon, List, Initial Selection)
watershedName = JOptionPane.showInputDialog(None,"Choose a Watershed","Project Status Plot",JOptionPane.PLAIN_MESSAGE,None,watershedList, watershedList[0])
if watershedName:
	
	projectList = list(dataDict[watershedName].keys())
	
	#Calls the JOptionPane funtion:  showInputDialog(Parent Component, Message, Title, MessageType, Icon, List, Initial Selection)
	projectName = JOptionPane.showInputDialog(None,"Choose a Project","Project Status Plot",JOptionPane.PLAIN_MESSAGE,None,projectList, projectList[0])

	if projectName:
		#construct timeseries

		params = dataDict[watershedName][projectName]
		datum, poolLevelTsID, poolLevel2TsID, poolLevel3TsID, outflowTsID, inflowTsID, forecastedInflowTsID, tailwaterLevelTsID, stageMarkers, flowMarkers, units, elevationOrStage = params
		
		# Determine Script Context
		isClient = hec.lang.ClientAppCheck.haveClientApp()
		isCWMSVue = hec.cwmsVue.CwmsListSelection.getMainWindow() is not None
		isShellScript = not isClient and not isCWMSVue
		
		# Get Database Connection
		db = DBAPI.open()
		
		db.setTimeZone('UTC')
		# Get Observed Data from CWMS Database
		cal = Calendar.getInstance()
		cal.setTimeZone(TimeZone.getTimeZone('UTC'))
		cal.setTimeInMillis(System.currentTimeMillis())
		t = HecTime(cal)
		curTime = t.dateAndTime(104)
		t.subtractDays(daysToLookBack)
		startTime = t.dateAndTime(104)
		t.addDays(daysToLookBack+daysToLookForward)
		endTime = t.dateAndTime(104)
		# Get Observed Data
		db.setTimeWindow(startTime, curTime)
		
		
		#get pool level
		if poolLevelTsID:
			poolLevel = getDataIfExists(poolLevelTsID)
		else:
			poolLevelTsIDList = ['{}.Stage.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Stage.Inst.1Hour.0.rev'.format(projectName),]
			for poolLevelTsID in poolLevelTsIDList:
				poolLevel = getDataIfExists(poolLevelTsID)
				if poolLevel:
					break
		
		#get second pool level
		pool2Level = getDataIfExists(poolLevel2TsID)

		#get third pool level
		pool3Level = getDataIfExists(poolLevel3TsID)

		
		#get tailwater level
		tailwaterLevel = getDataIfExists(tailwaterLevelTsID)	
			
		#get outflow
		if outflowTsID:
			outflow = getDataIfExists(outflowTsID)
		else:
			outflowTsIdList = ['{}.Flow-Out.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Flow-Out.Inst.1Hour.0.rev'.format(projectName),
						'{}.Flow.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Flow.Inst.1Hour.0.rev'.format(projectName),
						'{}.Flow-Out.Inst.~1Day.0.CEMVP-Legacy'.format(projectName),]
			for outflowTsID in outflowTsIdList:
				outflow = getDataIfExists(outflowTsID)
				if outflow:
					break
		# get outflow manual measurment
		outflowMeasTsIdList = ['{}-Tailwater.Flow.Inst.0.0.Raw-USGS'.format(projectName),
					'{}-Tailwater.Flow.Inst.0.0.Raw-CEMVP'.format(projectName),]
		for outflowMeasTsID in outflowMeasTsIdList:
			outflowMeas = getDataIfExists(outflowMeasTsID)
			if outflowMeas:
				print(outflowMeas)
				break
		
		
		#get inflow
		if inflowTsID:
			inflow = getDataIfExists(inflowTsID)
		else:
			inflowTsIdList = ['{}.Flow-In.Ave.15Minutes.1Day.comp'.format(projectName),
						'{}.Flow-In.Inst.~1Day.0.CEMVP-Legacy'.format(projectName),]
			for inflowTsID in inflowTsIdList:
				inflow = getDataIfExists(inflowTsID)
				if inflow:
					break
		
		##get forecasted inflow
		db.setTimeWindow(curTime, endTime)
		if forecastedInflowTsID:
			forecastedInflow = getDataIfExists(forecastedInflowTsID)
		else:
			forecastedInflowTsIdList = ['{}.Flow-In.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),
						'{}.Flow-Sim.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),]
			for forecastedInflowTsID in forecastedInflowTsIdList:
				forecastedInflow = getDataIfExists(forecastedInflowTsID)
				if forecastedInflow:
					break
		
		db.close()
		
		# Configure Plot Layout
		plotName = "{}".format(projectName)
		
		try:
			plotName+="\nPool Level {} ft at {} \n Outflow {} cfs ".format(round(poolLevel.lastValidValue(),2),
			lastValidDateString(poolLevel), round(outflow.lastValidValue()))
		except:
			pass	
		plot = Plot.newPlot(plotName)
		layout = Plot.newPlotLayout()
		if tailwaterLevel is not None:
			taildata = tailwaterLevel.getData()
			taildata.parameter='-1'

			stageView = layout.addViewport(.34)
			stageTailView = layout.addViewport(.33)
			flowView = layout.addViewport(.33)
			
		else:
			stageView = layout.addViewport(.5)
			flowView = layout.addViewport(.5)
			stageTailView = None
		
		stageView.addCurve("Y1", poolLevel.getData())
		if pool2Level is not None:
			stageView.addCurve("Y1", pool2Level.getData())

		if pool3Level is not None:
			stageView.addCurve("Y1", pool3Level.getData())
			
		if tailwaterLevel is not None:
			stageTailView.addCurve("Y1", taildata)

		if outflow is not None:
			flowView.addCurve("Y1", outflow.getData())
		
		if outflowMeas is not None:
			flowView.addCurve("Y1", outflowMeas.getData())
		
		if inflow is not None:
			flowView.addCurve("Y1", inflow.getData())

		if forecastedInflow is not None:
			print(type(forecastedInflow),forecastedInflow)
			flowView.addCurve("Y1", forecastedInflow.getData())

		
		
		# Add Layout Properties
		layout.setHasLegend(True)
		layout.setHasToolbar(True)
		plot.configurePlotLayout(layout)
		plot.setSize(960, 640)
		panel = plot.getPlotpanel()
		panel.setHorizontalViewportSpacing(1)
		plot.showPlot()

		if poolLevel is not None:
			if elevationOrStage:
				plot.getViewport(poolLevel.getData()).getAxis('Y1').setLabel('Pool Elevation, ft {}'.format(datum))
			else:
				plot.getViewport(poolLevel.getData()).getAxis('Y1').setLabel('Pool Level, ft')
		if tailwaterLevel is not None:
			plot.getViewport(taildata).getAxis('Y1').setLabel('Tailwater Level, ft')
		if outflow	is not None:
			plot.getViewport(outflow.getData()).getAxis('Y1').setLabel('Flow, cfs')
		# Create Plot Title Text
		plotTitle = plot.getPlotTitle()
		plotTitle.setText(plotName)
		#plotTitle.setAlignment('center')
		#plotTitle.setFont("Arial Black")
		plotTitle.setFontSize(18)
		plot.setPlotTitleVisible(1)
		## Plot Line Styles
		if poolLevel is not None:
			curveFormatter(plot, poolLevel.getData(), "blue", 3, "Pool Elevation", None, None)
		
		if (outflowMeas is not None):
			curve = curveFormatter(plot, outflowMeas.getData(), "red", 0, 'Measurement', None, None)
			curve.setLineVisible(False)
			curve.setSymbolsVisible(True)
			#curve.setSymbolSkipCount(6)
			curve.setSymbolFillColor('red')
			curve.setSymbolLineColor('red')
			curve.setSymbolType('Asterisk')
			curve.setSymbolSize(16)	
		
			if outflow is not None:
				curveFormatter(plot, outflow.getData(), "lightblue", 1.5, "Outflow", None, None)
		else:
		
			if outflow is not None:
				curveFormatter(plot, outflow.getData(), "red", 1.5, "Outflow", None, None)
		
		
		if inflow is not None:
			curveFormatter(plot, inflow.getData(), "black", 1.5, 'Net Inflow', None, None)
		
		
		if forecastedInflow is not None:
			curveFormatter(plot, forecastedInflow.getData(), "black", 1.5, "Forecasted Inflow (NWS)", "dash", None)
		
			
		# X Axes Marker
		markerCurTime = AxisMarker()
		markerCurTime.axis = "X1"
		markerCurTime.value = curTime
		markerCurTime.labelText = "Cur Time: "+curTime+" UTC"
		markerCurTime.labelFont = "Arial,14"
		markerCurTime.labelPosition = "center"
		markerCurTime.labelAlignment = "center"
		markerCurTime.lineWidth = 1.0
		markerCurTime.lineStyle = "Dot"
		if poolLevel is not None:
			plot.getViewport(poolLevel.getData()).addAxisMarker(markerCurTime)
		markerCurTime.labelText = ''
		if outflow	is not None:
			plot.getViewport(outflow.getData()).addAxisMarker(markerCurTime)
		if tailwaterLevel is not None:
			plot.getViewport(tailwaterLevel.getData()).addAxisMarker(markerCurTime)
		
		if stageMarkers:
			## plot marker bands
			try:
				for a in stageMarkers.split("|"):
					
					num, comment, color =  a.split(';')
					markerBand(str(num),comment.strip(), plot.getViewport(poolLevel.getData()), color.strip())
			except NameError:
				print("stageMarkers not defined")
		
		if flowMarkers:
			## plot marker bands
			try:
				for a in flowMarkers.split("|"):
					num, comment, color =  a.split(';')
					markerBand(str(num),comment.strip(), plot.getViewport(outflow.getData()), color.strip())
			except NameError:
				print("flowMarkers not defined")
		
		del(datum, poolLevelTsID, poolLevel2TsID, poolLevel3TsID, outflowTsID, inflowTsID, forecastedInflowTsID, tailwaterLevelTsID, stageMarkers, flowMarkers, units, elevationOrStage)
