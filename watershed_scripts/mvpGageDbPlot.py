from javax.swing import JTree, JFrame, JOptionPane, JButton, JTextArea, JScrollPane, JComboBox, JPanel, JLabel, WindowConstants, JLabel, JTextField
from java.awt import BorderLayout, Dimension, FlowLayout
from javax.swing.border import EmptyBorder
from java.awt.event     import ActionListener
from javax.swing.tree import DefaultMutableTreeNode
from collections import OrderedDict
import re
import DBAPI, hec
from hec.script import Plot, AxisMarker, MessageBox
from hec.heclib.util import HecTime
from java.util import Calendar, TimeZone
from java.lang import System
from hec.cwmsVue import CwmsListSelection
from hec.script import AxisMarker
try:
# Add rtsutils package to sys.path before importing
    sys.path.append(os.path.join(os.environ['APPDATA'], "rsgis"))
    #print(os.environ['APPDATA'], "rsgis")
    from rtsutils import cavistatus
except ImportError, ex:
    raise

class mvpGagePlotter:

	def __init__(self, dataDict):


		self.dataDict = dataDict
		self.frame = JFrame("MVP CWMS Plotter - Select Project to Plot", defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE)
		self.frame.setSize(500, 400)
		self.frame.setLayout(BorderLayout())
		watershedList = list(dataDict.keys())

		root = DefaultMutableTreeNode('Watershed')
		for watershedName in watershedList:
			watershedSites = DefaultMutableTreeNode(watershedName)
			projectList = list(dataDict[watershedName].keys())
			#print(watershedName)
			watershedNode = DefaultMutableTreeNode(watershedName)
			root.add(watershedNode)

			#now add the cities starting with M & S
			self.addSites(watershedNode, projectList)

		self.tree = JTree(root)

		scrollPane = JScrollPane()  # add a scrollbar to the viewport
		scrollPane.setPreferredSize(Dimension(400,300))
		scrollPane.getViewport().setView((self.tree))

		panel = JPanel()
		panel.add(scrollPane)
		self.frame.add(panel, BorderLayout.NORTH)
		#panel.setBorder(EmptyBorder(10, 10, 10, 10))

		btn = JButton('Select', actionPerformed = self.plotTrigger)
		self.frame.add(btn,BorderLayout.SOUTH)

		#self.label = JLabel('Select Project')
		#frame.add(self.label, BorderLayout.NORTH)

		timeWindowPanel = JPanel()

		self.lookBackOptions = ['Lookback 7 days', 'Lookback 30 days', 'Lookback 3 months', 'Lookback 6 months', 'Lookback 12 months', 'Lookback 18 months', 'Lookback 24 months']
		self.cbLookBack = JComboBox(self.lookBackOptions)
		self.lookForwardOptions = ['Look forward 7 days', 'Look forward 28 days']
		self.cbLookForward = JComboBox(self.lookForwardOptions)
		timeWindowPanel.add(self.cbLookBack)
		timeWindowPanel.add(self.cbLookForward)
		self.frame.add(timeWindowPanel,BorderLayout.CENTER)

		self.frame.pack();
		self.frame.setLocationRelativeTo(None);
		self.frame.setVisible(True)
		self.addSites

	def addSites(self, branch, branchData=None):
		'''  add data to tree branch
			 requires branch and data to add to branch
		'''
		# this does not check to see if its a valid branch
		if branchData == None:
			branch.add(DefaultMutableTreeNode('No valid data'))
		else:
			for item in branchData:
			  # add the data from the specified list to the branch
			  branch.add(DefaultMutableTreeNode(item))

	def cbSelect(self,event, cb, cbList):
		selectionText = cbList[cb.selectedIndex]
		days = int(re.search(r'\d+', selectionText).group())
		#print(cbSelectionTextLB)
		if 'months' in selectionText:
			days = days*30.4167
		return days

	def siteSelect(self, event):
		selectionPaths = self.tree.getSelectionPaths()
		if selectionPaths is not None:
			
			watershedDict = OrderedDict()
			for row in selectionPaths:
				path = list(row.getPath())
				wtshd = str(path[1])
				#print(wtshd)
				if wtshd in watershedDict.keys():
					try:
						# if site is selected and values exist for watershed key
						site = str(path[2])
						if site not in watershedDict[wtshd]:
							watershedDict[wtshd].append(site)
					except:
						# add all sites if watershed is selected and values exist for watershed key
						for site in self.dataDict[wtshd].keys():
							if site not in watershedDict[wtshd]:
								watershedDict[wtshd].append(site)
				else:
					#if no values exists for watershed key
					try:
						site = str(path[2])
						watershedDict[wtshd] = [site]
					except:
						# add all sites if watershed is selected
						watershedDict[wtshd] = self.dataDict[wtshd].keys()	
			#print(watershedDict)
			return watershedDict


	def plotTrigger(self, event):
		#get time window
		self.lookBackDays = int(self.cbSelect(event, self.cbLookBack, self.lookBackOptions))
		self.lookForewardDays = int(self.cbSelect(event, self.cbLookForward, self.lookForwardOptions))
		watershedDict = self.siteSelect(event)

		#if site is selected
		if watershedDict:
			#close GUI
			self.frame.dispose()
			#walkthrough and plot
			for watershedName in watershedDict.keys():
				for projectName in watershedDict[watershedName]:
					print('Plotting ', projectName)
					self.plotFunct(event, watershedName, projectName)

					
	def markerBand(self, value, label, viewport, color, linestyle):
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
	    mb.lineStyle = linestyle
	    mb.labelPosition = 'below'
	    viewport.addAxisMarker(mb)
	    return mb
	def curveFormatter(self, plot, dataset, lineColor, lineWidth, legendText, lineStyle, fillCurveType):
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
		if legendText !='':
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
	def getDataIfExists(self, tsID):
		try:
			data = self.db.read(tsID)
			if self.units == 'metric':
				print('convert to metric')
				print(data.getUnits())
				data = data.convertToMetricUnits()
				print(data.getUnits())
			return data
		except:
			print('Error: Data in {} does not exists for time window'.format(tsID))
	
	def lastValidDateString(self, tsData):
		intTime = tsData.lastValidDate()
		lastTime = HecTime(self.cal)
		lastTime.set(intTime)
		return lastTime.dateAndTime(104)
	
	def getDataWithSuggestedIds(self, tsid, tsIDList):
		#get rev stage level
		if tsid:
			data = self.getDataIfExists(tsid)
		else:
			for tsid in tsIDList:
				data = self.getDataIfExists(tsid)
				if data:
					return 	data		
	
	def plotFunct(self, event, watershedName, projectName):	
		params = self.dataDict[watershedName][projectName]
		om, datum, stageLevelTsIDrev, stageLevelTsIDraw, stageLevelTsIDusgsRaw, stageLevelTsIdusgsRev, stageMeasID, dischargeTsIDrev, dischargeTsIDusgsRaw, dischargeTsIDusgsRev, dischargeMeasID, publicName, forecastedFlowTsID, tailwaterLevelTsID, stageMarkers, flowMarkers, self.units, elevationOrStage, usgsID, hydrographer = params

		
		#plot band if its a lock and dam
		bandwidth = 0.3
		# Determine Script Context
		isClient = hec.lang.ClientAppCheck.haveClientApp()
		isCWMSVue = hec.cwmsVue.CwmsListSelection.getMainWindow() is not None
		isShellScript = not isClient and not isCWMSVue
		
		# Get Database Connection
		self.db = DBAPI.open()
		
		self.db.setTimeZone('UTC')
		# Get Observed Data from CWMS Database
		self.cal = Calendar.getInstance()
		self.cal.setTimeZone(TimeZone.getTimeZone('UTC'))
		self.cal.setTimeInMillis(System.currentTimeMillis())
		t = HecTime(self.cal)
		curTime = t.dateAndTime(104)
		t.subtractDays(self.lookBackDays)
		startTime = t.dateAndTime(104)
		t.addDays(self.lookBackDays+self.lookForewardDays)
		endTime = t.dateAndTime(104)
		# Get Observed Data
		self.db.setTimeWindow(startTime, curTime)
		print(self.lookBackDays, self.lookForewardDays, startTime, curTime)
		
		stageList = []
		#get rev stage level
		stageLevelTsIDList = ['{}.Stage.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Stage.Inst.1Hour.0.rev'.format(projectName),]		
		stageLevelrev = self.getDataWithSuggestedIds(stageLevelTsIDrev, stageLevelTsIDList)
		stageList.append(stageLevelrev)

		#get raw stage level
		stageLevelTsIDrawList = ['{}.Stage.Inst.15Minutes.0.CEMVP-GOES-Raw'.format(projectName),
						'{}.Stage.Inst.1Hour.0.CEMVP-GOES-Raw'.format(projectName),
						'{}.Stage.Inst.15Minutes.0.OTHER-GOES-Raw'.format(projectName),
						'{}.Stage.Inst.1Hour.0.OTHER-GOES-Raw'.format(projectName),]		
		stageLevelraw = self.getDataWithSuggestedIds(stageLevelTsIDraw, stageLevelTsIDrawList)
		stageList.append(stageLevelraw)
		#get usgs raw stage level
		stageLevelTsIDusgsRawList = ['{}.Stage.Inst.~15Minutes.0.Raw-USGS'.format(projectName),
										'{}.Stage.Inst.~15Minutes.0.Raw-MDNR'.format(projectName),]		
		stageLevelUsgsRaw = self.getDataWithSuggestedIds(stageLevelTsIDusgsRaw, stageLevelTsIDusgsRawList)
		stageList.append(stageLevelUsgsRaw)
		
		#get usgs rev stage level
		stageLevelTsIDusgsRevList = ['{}.Stage.Inst.~15Minutes.0.rev-USGS'.format(projectName),]		
		stageLevelUsgsRev = self.getDataWithSuggestedIds(stageLevelTsIdusgsRev, stageLevelTsIDusgsRevList)
		stageList.append(stageLevelUsgsRev)
		
		# get stage manual measurment
		stageMeasTsIdList = ['{}.Stage.Inst.0.0.Raw-USGS'.format(projectName),
					'{}.Stage.Inst.0.0.Raw-CEMVP'.format(projectName),]
		stageMeas = self.getDataWithSuggestedIds(stageMeasID, stageMeasTsIdList)
		stageList.append(stageMeas)
		
		##############################################
		#get rev discharge 
		flowList = []
		dischargeTsIdList = ['{}.Flow.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Flow.Inst.1Hour.0.rev'.format(projectName),]		
		dischargeRev = self.getDataWithSuggestedIds(dischargeTsIDrev, dischargeTsIdList)
		flowList.append(dischargeRev)
		
		#get raw USGS or MDNR discharge 
		dischargeRawTsIdList = ['{}.Flow.Inst.~15Minutes.0.Raw-USGS'.format(projectName),
						'{}.Flow.Inst.~15Minutes.0.Raw-MDNR'.format(projectName),]		
		dischargeRaw = self.getDataWithSuggestedIds(dischargeTsIDusgsRaw, dischargeRawTsIdList)
		flowList.append(dischargeRaw)
		
		#get rev USGS or MDNR discharge 
		dischargeRevTsIdList = ['{}.Flow.Inst.~15Minutes.0.rev-USGS'.format(projectName),
						#'{}.Flow.Inst.~15Minutes.0.rev-MDNR'.format(projectName),
						]		
		dischargeUsgsRev = self.getDataWithSuggestedIds(dischargeTsIDusgsRev, dischargeRevTsIdList)
		flowList.append(dischargeUsgsRev)

		# get outflow manual measurment
		dischargeMeasTsIdList = ['{}.Flow.Inst.0.0.Raw-USGS'.format(projectName),
					'{}.Flow.Inst.0.0.Raw-CEMVP'.format(projectName),]
		dischargeMeas = self.getDataWithSuggestedIds(dischargeMeasID, dischargeMeasTsIdList)
		flowList.append(dischargeMeas)
		
		##get forecasted flow
		self.db.setTimeWindow(curTime, endTime)
		forecastedFlowTsIdList = ['{}.Flow.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),
							'{}.Flow-Sim.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),]
		forecastedFlow = self.getDataWithSuggestedIds(forecastedFlowTsID, forecastedFlowTsIdList)
		flowList.append(forecastedFlow)
		
		self.db.close()
		
		# Configure Plot Layout
		plotName = "{}".format(projectName)	
		try:
			plotName+="\nStage Level {} {} at {} \n Discharge {} {} ".format(round(stageLevelrev.lastValidValue(),2),
			stageLevelrev.getUnits(), self.lastValidDateString(stageLevelrev), round(dischargeRev.lastValidValue()),
			dischargeRev.getUnits())
		except:
			pass	
		plot = Plot.newPlot(plotName)
		layout = Plot.newPlotLayout()
		
		
		
		if all(i is None for i in flowList):
			flowView = None
			stageView = layout.addViewport(1)
			
		else:
			stageView = layout.addViewport(.5)
			flowView = layout.addViewport(.5)
			#flowList.reverse()
			for i in flowList:
				if i is not None:
					flowView.addCurve("Y1", i.getData())

		#stageList.reverse()
		for i in stageList:
			if i is not None:
				stageView.addCurve("Y1", i.getData())
		
		# Add Layout Properties
		layout.setHasLegend(True)
		layout.setHasToolbar(True)
		plot.configurePlotLayout(layout)
		plot.setSize(960, 640)
		panel = plot.getPlotpanel()
		panel.setHorizontalViewportSpacing(1)
		plot.showPlot()

		# Create Plot Title Text
		plotTitle = plot.getPlotTitle()
		plotTitle.setText(plotName)
		#plotTitle.setAlignment('center')
		#plotTitle.setFont("Arial Black")
		plotTitle.setFontSize(18)
		plot.setPlotTitleVisible(1)
		## Plot Line Styles
		if stageLevelrev is not None:
			self.curveFormatter(plot, stageLevelrev.getData(), "blue", 3, "", None, None)
		

		if stageLevelraw is not None:
			self.curveFormatter(plot, stageLevelraw.getData(), "lightgray", 1, "", None, None)
		if stageLevelUsgsRaw is not None:
			self.curveFormatter(plot, stageLevelUsgsRaw.getData(), "gray", 1, "", None, None)
		if stageLevelUsgsRev is not None:
			self.curveFormatter(plot, stageLevelUsgsRev.getData(), "blue", 1, "", 'Dash', None)
		
		if stageMeas is not None:
			curve = self.curveFormatter(plot, stageMeas.getData(), "red", 0, '', None, None)
			curve.setLineVisible(False)
			curve.setSymbolsVisible(True)
			curve.setSymbolSkipCount(0)
			curve.setFirstSymbolOffset(0)
			curve.setSymbolFillColor('red')
			curve.setSymbolLineColor('red')
			curve.setSymbolType('Asterisk')
			curve.setSymbolSize(16)	
		
		if dischargeMeas is not None:
			curve = self.curveFormatter(plot, dischargeMeas.getData(), "red", 0, '', None, None)
			curve.setLineVisible(False)
			curve.setSymbolsVisible(True)
			curve.setSymbolSkipCount(0)
			curve.setFirstSymbolOffset(0)
			curve.setSymbolFillColor('red')
			curve.setSymbolLineColor('red')
			curve.setSymbolType('Asterisk')
			curve.setSymbolSize(16)	
		
			if dischargeRev is not None:
				self.curveFormatter(plot, dischargeRev.getData(), "lightblue", 1.5, "", None, None)
		else:
		
			if dischargeRev is not None:
				self.curveFormatter(plot, dischargeRev.getData(), "red", 1.5, "", None, None)
		
		
		if forecastedFlow is not None:
			self.curveFormatter(plot, forecastedFlow.getData(), "black", 1.5, "", "dash", None)
		if dischargeRaw is not None:
			self.curveFormatter(plot, dischargeRaw.getData(), "gray", 1, "", None, None)
		if dischargeUsgsRev is not None:
			self.curveFormatter(plot, dischargeUsgsRev.getData(), "blue", 1, "", 'Dash', None)
		
			
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
		if stageLevelrev is not None:
			plot.getViewport(stageLevelrev.getData()).addAxisMarker(markerCurTime)
		markerCurTime.labelText = ''
		if dischargeRev	is not None:
			plot.getViewport(dischargeRev.getData()).addAxisMarker(markerCurTime)

		
		if stageMarkers:
			## plot marker bands
			try:
				for a in stageMarkers.split("|"):
					num, comment, color =  a.split(';')
					self.markerBand(str(float(num)),comment.strip(), plot.getViewport(stageLevel.getData()), color.strip(), 'soild')
			except NameError:
				print("stageMarkers not defined")


		if flowMarkers:
			## plot marker bands
			try:
				for a in flowMarkers.split("|"):
					num, comment, color =  a.split(';')
					self.markerBand(str(float(num)),comment.strip(), plot.getViewport(outflow.getData()), color.strip(), 'soild')
			except NameError:
				print("flowMarkers not defined")
		
		#del(datum, stageLevelTsID, stageLevel2TsID, stageLevel3TsID, outflowTsID, inflowTsID, forecastedInflowTsID, tailwaterLevelTsID, stageMarkers, #flowMarkers, elevationOrStage)  	

	

			
if __name__ == '__main__':
    ##read imputs from file
    
    filePath = os.path.join(
        cavistatus.get_shared_directory(),
        'gageDBplotInputs.csv'
        )
    
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
    		watershedKey = line.split(',')[0]
    		siteKey = line.split(',')[1]
    		param = line.split('\n')[0].split(',')[2::]
    		#store data  in dictionary 
    		if watershedKey not in dataDict:
    			dataDict[watershedKey] = OrderedDict()
    		dataDict[watershedKey][siteKey] = param
    #reorder dictionary alphabetically
    dataDict = OrderedDict(sorted(dataDict.items()))
    for key in dataDict:
    	dataDict[key] = OrderedDict(sorted(dataDict[key].items()))
    mvpGagePlotter(dataDict)
    
