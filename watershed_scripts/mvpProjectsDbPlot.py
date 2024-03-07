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

class mvpProjectPlotter:

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

		self.lookBackOptions = ['Lookback 7 days', 'Lookback 30 days', 'Lookback 3 months', 'Lookback 6 months', 'Lookback 12 months', 'Lookback 18 months']
		self.cbLookBack = JComboBox(self.lookBackOptions)
		self.lookForwardOptions = ['Look forward 7 days', 'Look forward 28 days', 'Look forward 0 days']
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
		if legendText:
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
	def lockDamBand(self, tsid, viewport, bandwith, linestyle):
		# Dictionaries
		centerOfBand = {'LockDam_02' : 686.50,
				'LockDam_03' : 674.00,
				'LockDam_04' : 666.50,
				'LockDam_05' : 659.50,
				'LockDam_05a' : 650.00,
				'LockDam_06' : 644.50,
				'LockDam_07' : 639.00,
				'LockDam_08' : 630.00,
				'LockDam_09' : 619.00,
				'LockDam_10' : 611.00,
				'SSPM5' : 687.20,
				'PREW3' : 675.00,
				'WABM5' : 667.00,
				'AMAW3' : 660.00,
				'LockDam_05-Tailwater' : 651.00,
				'WNAM5' : 645.50,
				'LACW3' : 631.00,
				'LNSI4' : 620.00,
				'CLAI4' : 611.8,}
		loc = tsid.split('.')[0]
		centerOfBand = centerOfBand[loc]

		upperBand = str(centerOfBand+bandwith)
		lowerBand = str(centerOfBand-bandwith)

		if loc == 'CLAI4':
			self.markerBand(str(centerOfBand), 'Secondary Control - Clayton', viewport, 'red',  linestyle)
		elif loc == 'LockDam_10':
			self.markerBand(upperBand, 'Top of Primary', viewport, 'blue',  linestyle)
			self.markerBand(lowerBand, 'Bottom of Primary', viewport, 'blue',  linestyle)	
			self.markerBand('610', 'Tertiary', viewport, 'cyan',  linestyle)		
		elif 'LockDam' in loc and 'Tailwater' not in loc:
			self.markerBand(upperBand, 'Top of Secondary', viewport, 'blue',  linestyle)
			self.markerBand(lowerBand, 'Bottom of Secondary', viewport, 'blue',  linestyle)
		else:
			self.markerBand(upperBand, 'Top of Primary', viewport, 'red',  linestyle)
			self.markerBand(lowerBand, 'Bottom of Primary', viewport, 'red', linestyle)			
	
	def plotFunct(self, event, watershedName, projectName):	
		params = self.dataDict[watershedName][projectName]
		datum, poolLevelTsID, poolLevel2TsID, poolLevel3TsID, poolLevel4TsID, outflowTsID, outflow2TsID, inflowTsID, forecastedInflowTsID, tailwaterLevelTsID, stageMarkers, flowMarkers, self.units, elevationOrStage = params


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
		
		
		#get pool level
		if poolLevelTsID:
			poolLevel = self.getDataIfExists(poolLevelTsID)
		else:
			poolLevelTsIDList = ['{}.Stage.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Stage.Inst.1Hour.0.rev'.format(projectName),]
			for poolLevelTsID in poolLevelTsIDList:
				poolLevel = self.getDataIfExists(poolLevelTsID)
				if poolLevel:
					break
		
		#get second pool level
		pool2Level = self.getDataIfExists(poolLevel2TsID)
	
		#get third pool level
		pool3Level = self.getDataIfExists(poolLevel3TsID)

		#get fourth pool level
		pool4Level = self.getDataIfExists(poolLevel4TsID)
	
		
		#get tailwater level
		tailwaterLevel = self.getDataIfExists(tailwaterLevelTsID)	
		if 'LockDam' not in poolLevelTsID:
			# get stage manual measurment
			stageMeasTsIdList = ['{}.Stage.Inst.0.0.Raw-USGS'.format(projectName),
						'{}.Stage.Inst.0.0.Raw-CEMVP'.format(projectName),]
			for stageMeasTsID in stageMeasTsIdList:
				stageMeas = self.getDataIfExists(stageMeasTsID)
				if stageMeas:
					print(stageMeas)
					break
		else:
			stageMeas=None		
		#get outflow
		if outflowTsID:
			outflow = self.getDataIfExists(outflowTsID)
		else:
			outflowTsIdList = ['{}.Flow-Out.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Flow-Out.Inst.1Hour.0.rev'.format(projectName),
						'{}.Flow.Inst.15Minutes.0.rev'.format(projectName),
						'{}.Flow.Inst.1Hour.0.rev'.format(projectName),
						'{}.Flow-Out.Inst.~1Day.0.CEMVP-Legacy'.format(projectName),
						'{}.Flow.Inst.~4Hours.0.CEMVP-Legacy'.format(projectName)]
			for outflowTsID in outflowTsIdList:
				outflow = self.getDataIfExists(outflowTsID)
				if outflow:
					break

		#get outflow 2
		outflow2 = self.getDataIfExists(outflow2TsID)
		
			

					
		# get outflow manual measurment
		outflowMeasTsIdList = ['{}-Tailwater.Flow.Inst.0.0.Raw-USGS'.format(projectName),
					'{}-Tailwater.Flow.Inst.0.0.Raw-CEMVP'.format(projectName),]
		for outflowMeasTsID in outflowMeasTsIdList:
			outflowMeas = self.getDataIfExists(outflowMeasTsID)
			if outflowMeas:
				print(outflowMeas)
				break
		if '.Inst.0.0' in outflow2TsID:
			outflowMeas = outflow2
			outflow2 = None
		
		#get inflow
		if 'LockDam' not in poolLevelTsID:
			if inflowTsID:
				inflow = self.getDataIfExists(inflowTsID)
			else:
				inflowTsIdList = ['{}.Flow-In.Ave.15Minutes.1Day.comp'.format(projectName),
							'{}.Flow-In.Inst.~1Day.0.CEMVP-Legacy'.format(projectName),]
				for inflowTsID in inflowTsIdList:
					inflow = self.getDataIfExists(inflowTsID)
					if inflow:
						break
		else:
			inflow = None
		
		##get forecasted inflow
		self.db.setTimeWindow(curTime, endTime)
		if forecastedInflowTsID:
			forecastedInflow = self.getDataIfExists(forecastedInflowTsID)
		else:
			if 'LockDam' in poolLevelTsID:
				forecastedInflowTsIdList = ['{}.Flow.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),
						'{}.Flow.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),]
			else:
				forecastedInflowTsIdList = ['{}.Flow-In.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),
							'{}.Flow-Sim.Inst.6Hours.0.Fcst-NCRFC-CHIPS'.format(projectName),]
			for forecastedInflowTsID in forecastedInflowTsIdList:
				forecastedInflow = self.getDataIfExists(forecastedInflowTsID)
				if forecastedInflow:
					break
		# get navigation flag
		if 'LockDam' in poolLevelTsID:
			t = HecTime(self.cal)
			curTime = t.dateAndTime(104)
			t.subtractDays(365)
			yearAgo = t.dateAndTime(104)		
			self.db.setTimeWindow(yearAgo, curTime)
			navigationFlag = self.getDataIfExists('LockDam_04.Code-Navigation.Inst.~1Day.0.Raw-CEMVP').lastValidValue()


			if navigationFlag ==1:
				bandwidth = 0.2
			else:
				bandwidth = 0.3

		
		self.db.close()
		
		# Configure Plot Layout

		plotName = "{}".format(projectName)	
		try:
			plotName+="\nPool Level {} {} at {} \n Outflow {} {} ".format(round(poolLevel.lastValidValue(),2),
			poolLevel.getUnits(), self.lastValidDateString(poolLevel), round(outflow.lastValidValue()),
			outflow.getUnits())
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
		if stageMeas is not None:
			stageView.addCurve("Y1", stageMeas.getData())
		if pool2Level is not None:
			stageView.addCurve("Y1", pool2Level.getData())
	
		if pool3Level is not None:
			stageView.addCurve("Y1", pool3Level.getData())

		if pool4Level is not None:
			stageView.addCurve("Y1", pool4Level.getData())
			
		if tailwaterLevel is not None:
			stageTailView.addCurve("Y1", taildata)
	
		if outflow is not None:
			flowView.addCurve("Y1", outflow.getData())
		if outflow2 is not None:
			flowView.addCurve("Y1", outflow2.getData())
		
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
				plot.getViewport(poolLevel.getData()).getAxis('Y1').setLabel('Pool Elevation, {} {}'.format(poolLevel.getUnits(),datum))
			else:
				plot.getViewport(poolLevel.getData()).getAxis('Y1').setLabel('Pool Level, {}'.format(poolLevel.getUnits()))
		if tailwaterLevel is not None:
			plot.getViewport(taildata).getAxis('Y1').setLabel('Tailwater Level')
		if outflow	is not None:
			plot.getViewport(outflow.getData()).getAxis('Y1').setLabel('Flow, {}'.format(outflow.getUnits()))
		# Create Plot Title Text
		plotTitle = plot.getPlotTitle()
		# add CUI tag if showing forecast data
		if self.lookForewardDays>0:
			plotName = "<html><strong>\t\t\tCUI//WATER//FED ONLY</b></strong>\n"+plotName
		plotTitle.setText(plotName)
		#plotTitle.setAlignment('center')
		#plotTitle.setFont("Arial Black")
		plotTitle.setFontSize(18)
		plot.setPlotTitleVisible(1)
		## Plot Line Styles
		if poolLevel is not None:
			self.curveFormatter(plot, poolLevel.getData(), "blue", 3, "Pool Elevation", None, None)
		if pool4Level is not None:
			self.curveFormatter(plot, pool4Level.getData(), "green", 2, "", None, None)
		if stageMeas is not None:
			curve = self.curveFormatter(plot, stageMeas.getData(), "red", 0, 'Measurement', None, None)
			curve.setLineVisible(False)
			curve.setSymbolsVisible(True)
			curve.setSymbolSkipCount(0)
			curve.setFirstSymbolOffset(0)
			curve.setSymbolFillColor('red')
			curve.setSymbolLineColor('red')
			curve.setSymbolType('Asterisk')
			curve.setSymbolSize(16)	
		
		if (outflowMeas is not None):
			curve = self.curveFormatter(plot, outflowMeas.getData(), "red", 0, 'Measurement', None, None)
			curve.setLineVisible(False)
			curve.setSymbolsVisible(True)
			curve.setSymbolSkipCount(0)
			curve.setFirstSymbolOffset(0)
			curve.setSymbolFillColor('red')
			curve.setSymbolLineColor('red')
			curve.setSymbolType('Asterisk')
			curve.setSymbolSize(16)	
		
			if outflow is not None:
				self.curveFormatter(plot, outflow.getData(), "lightblue", 1.5, "Outflow", None, None)
		else:
		
			if outflow is not None:
				self.curveFormatter(plot, outflow.getData(), "red", 1.5, "Outflow", None, None)
		
		
		if inflow is not None:
			self.curveFormatter(plot, inflow.getData(), "black", 1.5, 'Net Inflow', None, None)
		
		
		if forecastedInflow is not None:
			self.curveFormatter(plot, forecastedInflow.getData(), "black", 1.5, "Forecasted Inflow (NWS)", "dash", None)

		if outflow2 is not None:
			self.curveFormatter(plot, outflow2.getData(), "gray", 1.5, None, "dash", None)
		
			
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
		
		if stageMarkers != '':
			## plot marker bands
			try:
				for a in stageMarkers.split("|"):
					num, comment, color =  a.split(';')
					self.markerBand(str(float(num)),comment.strip(), plot.getViewport(poolLevel.getData()), color.strip(), 'soild')
			except:
				print("stageMarkers not defined")

		if "LockDam" in poolLevelTsID:
			self.lockDamBand(poolLevelTsID, plot.getViewport(poolLevel.getData()),bandwidth, "Dash Dot-Dot")
			try:
				self.lockDamBand(poolLevel2TsID, plot.getViewport(poolLevel.getData()),bandwidth, "Dash Dot-Dot")
			except:
				pass
		if flowMarkers != '':
			## plot marker bands
			try:
				for a in flowMarkers.split("|"):
					num, comment, color =  a.split(';')
					self.markerBand(str(float(num)),comment.strip(), plot.getViewport(outflow.getData()), color.strip(), 'soild')
			except:
				print("flowMarkers not defined")
		
		del(datum, poolLevelTsID, poolLevel2TsID, poolLevel3TsID, outflowTsID, inflowTsID, forecastedInflowTsID, tailwaterLevelTsID, stageMarkers, flowMarkers, elevationOrStage)  	

	

			
if __name__ == '__main__':
	##read imputs from file
	#watershed Path
	watershed_path = Project.getCurrentProject().getProjectDirectory()
	sharedPath = os.path.join(watershed_path,'shared')
	filePath = os.path.join(sharedPath,'projectDBplotInputs.csv')
	
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
	mvpProjectPlotter(dataDict)
    
