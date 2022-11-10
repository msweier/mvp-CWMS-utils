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
from com.rma.model import Project


class mvpGagePlotter:

	def __init__(self, dataDict):


		self.dataDict = dataDict
		self.frame = JFrame("MVP CWMS Plotter - Select Gage to Plot", defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE)
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
		self.lookForwardOptions = ['Look forward 0 days', 'Look forward 7 days', 'Look forward 28 days']
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
		windSpeedTsID, windDirTsid, airTempTsID, waterTempTsId  = params
		
		print(params)
		self.units = 'english'

		

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

		#get wind speed
		windSpeed = self.getDataIfExists(windSpeedTsID)
		#get wind direction
		windDir = self.getDataIfExists(windDirTsid)
        # get air temp
		airTemp = self.getDataIfExists(airTempTsID)
		tempList = [airTemp]
        
        # get water temp
		waterTemp = self.getDataIfExists(waterTempTsId)
		tempList.append(waterTemp)

		
		self.db.close()

		#print(windSpeed, windDir, airTemp, waterTemp)
		
        # Configure Plot Layout
		plotName = "{}".format(projectName)	
		try:
			plotName+="\nAir Temp {} {} at {} \n Wind Speed {} {} ".format(round(airTemp.lastValidValue(),2),
			airTemp.getUnits(), self.lastValidDateString(airTemp), round(windSpeed.lastValidValue()),
			windSpeed.getUnits())
		except:
			pass	
		plot = Plot.newPlot(plotName)
		layout = Plot.newPlotLayout()
		

		windDirView =   layout.addViewport(1)
		windSpeedView = layout.addViewport(2)
		tempView = layout.addViewport(3)
		if windDir is not None:
		    windDirView.addCurve("Y1", windDir.getData())
		if windSpeed is not None:
		    windSpeedView.addCurve("Y1", windSpeed.getData())

		for i in tempList:
		    if i is not None:
		        tempView.addCurve("Y1", i.getData())

		
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
		# add CUI tag if showing forecast data
		if self.lookForewardDays>0:
			plotName = "<html><strong>CUI//WATER//FED ONLY</b></strong>\n"+plotName
		plotTitle.setText(plotName)
        #plotTitle.setAlignment('center')
		#plotTitle.setFont("Arial Black")
		plotTitle.setFontSize(18)
		plot.setPlotTitleVisible(1)
		# Plot Line Styles
		if windDir is not None:
		    self.curveFormatter(plot, windDir.getData(), "lightgray", 1, "", None, None)
		

		if windSpeed is not None:
			self.curveFormatter(plot, windSpeed.getData(), "black", 1, "", None, None)
		if airTemp is not None:
			self.curveFormatter(plot, airTemp.getData(), "gray", 1, "", None, None)
		if waterTemp is not None:
			self.curveFormatter(plot, waterTemp.getData(), "blue", 1, "", 'Dash', None)
		
		if airTemp is not None:
		    self.markerBand(str(32),'Freezing', plot.getViewport(airTemp.getData()), 'black', 'dashdot')


		elif waterTemp is not None:
		        self.markerBand(str(float(32)),'Freezing', plot.getViewport(waterTemp.getData()), 'black', 'dashdot')

		if windDir is not None:
		    self.markerBand('90', 'East', plot.getViewport(windDir.getData()), 'red', 'dash')
		    self.markerBand('180', 'South', plot.getViewport(windDir.getData()), 'red', 'dash')
		    self.markerBand('270', 'West', plot.getViewport(windDir.getData()), 'red', 'dash')
		    print('could not plot wind compass')
		del(windSpeed, windDir, airTemp, waterTemp)
			
		# # X Axes Marker
		# markerCurTime = AxisMarker()
		# markerCurTime.axis = "X1"
		# markerCurTime.value = curTime
		# markerCurTime.labelText = "Cur Time: "+curTime+" UTC"
		# markerCurTime.labelFont = "Arial,14"
		# markerCurTime.labelPosition = "center"
		# markerCurTime.labelAlignment = "center"
		# markerCurTime.lineWidth = 1.0
		# markerCurTime.lineStyle = "Dot"
		# if stageLevelrev is not None:
			# plot.getViewport(stageLevelrev.getData()).addAxisMarker(markerCurTime)
		# markerCurTime.labelText = ''
		# if dischargeRev	is not None:
			# plot.getViewport(dischargeRev.getData()).addAxisMarker(markerCurTime)

		

        ## plot marker bands
		
if __name__ == '__main__':
	##read imputs from file
	#watershed Path
	watershed_path = Project.getCurrentProject().getProjectDirectory()
	sharedPath = os.path.join(watershed_path,'shared')
	filePath = os.path.join(sharedPath, 'gageWindTempinputs.csv')
	
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
    
