from java.awt import BorderLayout, Dimension, Toolkit, GridLayout
from java.awt.datatransfer import DataFlavor
from datetime import datetime, timedelta
import DBAPI
from hec.io          import TimeSeriesContainer
from hec.heclib.util import HecTime
from javax.swing import JFrame, JTextField, JLabel, JPanel, JButton, JTextArea, JScrollPane


def ld1Parser(txt):

	dateStr = txt.split('\n')[1].replace('\t', '')
	dt = datetime.strptime(dateStr, "%B %d, %Y").date()-timedelta(hours=24)
	col1 = []
	col2 = []
	
	for line in txt.split('\n'):
	    if 'Inst' in line and 'reading' not in line:

	        
	        if line.split('Inst')[0].split(' ')[0] == 'Midnight':
	            tCol1 = datetime.combine(dt, datetime.strptime('00:00', '%H:%M').time()) +timedelta(hours=24)
	        else:
	        	tCol1 = datetime.combine(dt, datetime.strptime(line.split('Inst')[0].split(' ')[0], '%H:%M').time())
	        vCol1 = float(line.split('Inst')[1].split('\t\t')[1].replace(',',''))
	        tCol2 = datetime.combine(dt, datetime.strptime(line.split('Inst')[1].split('\t\t\t\t\t')[1].split(' ')[0], '%H:%M').time()) +timedelta(hours=24)
	        if  '12:00' in line.split('Inst')[0].split(' ')[0] or '16:00' in line.split('Inst')[0].split(' ')[0]:
	            
	            vCol2 = float(line.split('Inst')[2].split('\t\t')[1].replace(',',''))
	            col2.append([tCol2, vCol2, 'LockDam_01.Flow-Out.Inst.~4Hours.0.raw-FordHydro'])
	        else:
	            vCol2 = float(line.split('Inst')[1].split('Elev\t\t')[1].split('\t\t')[0])
	            if 'Tailwater' in line:
	            	col2.append([tCol2, vCol2, 'LockDam_01-Tailwater.Elev.Inst.~1Day.0.raw-FordHydro-MSL1912'])
	            else:
	            	col2.append([tCol2, vCol2, 'LockDam_01.Elev.Inst.~1Day.0.raw-FordHydro-MSL1912'])
	        col1.append([tCol1, vCol1, 'LockDam_01.Flow-Out.Inst.~4Hours.0.raw-FordHydro'])
	        
	
	        #print(tCol1, vCol1, tCol2, vCol2)
	    if 'Total Streamflow' in line:
	        val = float(line.split('24 Hour Average		')[1].split('\t')[0].replace(',',''))
	        dailyAvg = [[dt, val, 'LockDam_01.Flow-Out.Ave.1Day.1Day.raw-FordHydro']]
	#print(col1)
	#print(col2)
	
	col1.append(col2[0])
	col1.append(col2[1])
	#print(col1)
	col2 = col2[2:4]
	return col1+col2+dailyAvg

def manualMeasurmentParser(txt):
    dataList = []
    for line in txt.split('\n'):
        print(line)
        try:
            cwmsLoc, param, date_string, value = line.split('\t')
            value = float(value)
            date_format = '%m/%d/%Y %H:%M'
            date = datetime.strptime(date_string, date_format)
            tsid = "{}.{}.Inst.0.0.Raw-CEMVP".format(cwmsLoc, param)
            #print(cwmsLoc, param, date, value)
            dataList.append([date, value, tsid])
        except:
            print('could not parse line {}'.format(line))
    return dataList
	
def storeTS(cwmsTsid, times, values, quality):
    global db
    # try:
    storeToCwmsDbSuccessful = False
    cwmsLoc, param, tp, interval, duration, version = cwmsTsid.split('.')
    if 'Flow' in param:
    	unit = 'cfs'
    elif 'Elev' in param or 'Stage' in param:
    	unit = 'ft'
    else:
    	unit = None
    tsc = TimeSeriesContainer()
    tsc.fullName     = cwmsTsid
    IRREGULAR_INTERVAL = -1
    #print('*****',cwmsTsid)
    location, parameter, type, interval, duration, version       = cwmsTsid.split('.')
    if '~' in interval or '.Raw-CEMVP' in cwmsTsid or '.raw-FordHydro' in cwmsTsid: interval = IRREGULAR_INTERVAL
    tsc.location, tsc.parameter, tsc.type, tsc.interval, duration, tsc.version = [location, parameter, type, interval, duration, version  ]
    tsc.units        = unit
    tsc.times        = times
    tsc.values       = values
    tsc.quality      = quality
    tsc.numberValues = len(times)
    tsc.startTime    = times[0]
    tsc.endTime      = times[-1]
    

    db.put(tsc)
    storeToCwmsDbSuccessful = True
    msg = "*** Saved record: {} to CWMS Database. ***".format(cwmsTsid)

    return msg


def clipboard_listener():
    text = ""
    try:
        clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
        contents = clipboard.getContents(None)
        if contents != None and contents.isDataFlavorSupported(DataFlavor.stringFlavor):
            new_text = contents.getTransferData(DataFlavor.stringFlavor)
            if new_text != text:
                text = new_text
                #print("New clipboard text:", text)
    except Exception as e:
        print("Error:", e)

def inputFrame():
    frame = JFrame("Paste Data to Import into CWMS")
    frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
    frame.setLayout(BorderLayout())
    frame.setSize(Dimension(400, 300))
    frame.setLocationRelativeTo(None)
    text_area = JTextArea()
    scroll_pane = JScrollPane(text_area)
    frame.add(scroll_pane, BorderLayout.CENTER)
    button_panel = JPanel()
    ok_button = JButton("OK", actionPerformed=lambda event: on_ok_button_click(frame, text_area))
    button_panel.add(ok_button)
    cancel_button = JButton("Cancel", actionPerformed=lambda event: frame.dispose())
    button_panel.add(cancel_button)
    frame.add(button_panel, BorderLayout.SOUTH)
    frame.setVisible(True)

def on_ok_button_click(frame, text_area):
    
    clipboard_listener()
    txt = text_area.getText()
    loadData(txt)
    
    frame.dispose()
    return data
   
def outputFrameInit():
	frame = JFrame("****Progress***")
	frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
	frame.setLayout(BorderLayout())
	frame.setSize(Dimension(600, 300))
	frame.setLocationRelativeTo(None)
	text_area = JTextArea()
	scroll_pane = JScrollPane(text_area)
	frame.add(scroll_pane, BorderLayout.CENTER)
	button_panel = JPanel()
	close_button = JButton("Close", actionPerformed=lambda event: frame.dispose())
	button_panel.add(close_button)
	frame.add(button_panel, BorderLayout.SOUTH)
	frame.setVisible(True)
	return text_area



def loadData(txt):
    global db
    if "Government Lock" in txt:
    	data = ld1Parser(txt)
    	timezone = 'CST'
    elif 'Primary Reference measurement' in txt:
    	data = manualMeasurmentParser(txt)
    	timezone = 'UTC'
    else:
    	data = None

    print(data)
    # init output frame
    text_field = outputFrameInit()

    if data:
   
	    quality = None
	    db = DBAPI.open()
	    db.setTimeZone(timezone)
	    db.setStoreRule("REPLACE ALL")
	    db.setOfficeId('MVP')
	    msg = ''
	    for d, values, tsid in data:
	   	
	   	    t = HecTime()
	   	    if type(d) == type(datetime.now().date()):
	   	    	minutes =  0
	   	    else:
	   	    	minutes = d.hour*60+d.minute
	   	    print(d.year, d.month, d.day, minutes)
	   	    t.setYearMonthDay(d.year, d.month, d.day, minutes)
	   	    	
	   	    time = t.value()
	   	    msg += storeTS(tsid, [time], [values], quality)+'\n'
	   	    print(msg)
	   	    text_field.setText(msg)

	    db.close()
	    
    else:
    	text_field.setText(txt+'\n***Could not recognize text input above')

if __name__ == "__main__":
    data = inputFrame()
    print('******************')
