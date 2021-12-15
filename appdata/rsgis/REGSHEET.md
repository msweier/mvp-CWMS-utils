USACE St. Paul District Water Management 
Mississippi Navigation Regulation Sheet 
For use in daily regulation of Lock and Dam 2 through Lock and Dam 10
Developed Jan 2019 (updated Dec 2021 by m. weier)
 
 
Author: Nathaniel Anderson 
nathaniel.d.anderson@usace.army.mil
 
Purpose and Scope:
This new regulation sheet was developed at the request of the current St. Paul District Water Management and Hydrology section chief: Elizabeth Nelsen. The project scope was to create a new version of a regulation sheet in order to support the daily orders from water management to the locks and dams of the navigable Mississippi River within the St. Paul District (LD2-LD10). 
The St. Paul District water management team is in the process of changing platforms for data management from an antiquated “hornet” system to the current Corps platform (CWMS) for water management. The new CWMS platform stores data in CWMSvue using .dss files. The new regulation sheet is intended to work with this new platform and allow the district to obtain data without accessing the antiquated “hornet” system. 
It is also the intent of the water management team to have the ability to obtain data directly from the database without needing any personnel on site (at any given lock and dam) to enter data regarding their site. This will enable water management personnel to obtain the most up to date information at all locations when making regulation decisions regardless of timely data entries by site personnel.  
Getting started with the new regulation sheet:
Add Daily_Reg_Sheet using script_downloader_mvp script (found at https://github.com/msweier/mvp-CWMS-utils) to add to active scripts in your CAVI script window like any other script
Select the “visualization” tab within your CAVI
Right click in the script area (currently located on left hand side of screen as a greyish box area containing script buttons) and select “edit”
Find “Daily_Reg_Sheet” on the left hand window and select it, then select the “Add” button to move it to the right hand side of the dialogue box. Then click “OK”
You should now be able to run the script without any errors
 
 
 
 
Running the Script
When the script is run, Microsoft Excel will open, and may prompt you to “update”. Click “Update”. There may also be a highlighted security warning appearing near the top of the screen. Click “Enable Content”. 
You can now edit and otherwise modify this sheet during regulation.  It is best practice for records to directly enter the order information into the provided blocks. When done, save as a .pdf and print.
Save as .pdf
Select file, save as
Change file type to .pdf and save
Print the regulation sheet
Select the “file” menu
Select “print”
Select desired printer
Select “landscape” orientation
Select “2 sided (flipping on long edge)”
Select the print button again
Save the Excel File
Close the Excel file
 
Basic Methodology:
This task was accomplished using the combination of a CWMS script (written in Python) and Microsoft Excel. A script was developed that collects and organizes all the data required by the Mississippi River regulator. The script then exports this data to an Excel file. A second Excel file on the user’s computer was built to reference this newly created file, rearranges the data into a usable format, and prepares it for regulation use and printing. 
 
 
Script Format:
The main body of the script is broken into 4 groups. 1st, data is assigned to a variable that is easy to use in the organization process. 2nd, the data is acquired by retrieving the data from the database and renaming the variables to items that make sense to all water managers. 3rd, the variables are all added to a compiled dataset. 4th, the script does a number of operations involving Microsoft Excel including the generation of a new Excel workbook, opening a second workbook, and creating a copy of the second workbook with the current date.
 
DATA
The script pulls data from the CWMSvue database. It pulls data only within the time window set in the script. The time window is set in the script by looking at today’s date, then going back 5 days, and beginning at 1400 UTC (0800 CST). Data is then pulled through whatever time the script is run, meaning the later in the day the script is run, the more data should be available in the database.
 
Excel Workbook Format:
1: The Microsoft Excel workbook (DRS.xlsx) is overwritten every time the script is run. This workbook contains all of the data obtained from CWMSvue by the script. This data is organized in a specific format and affects the entire flow of functions. Changes to this format in the script must be made in a specific way in order to maintain the integrity of the regulation sheet and all supporting processes.
2: The Microsoft Excel workbook (DailyRegSheet_Computations) was developed separately from the script. It is built to reference the workbook (DRS.xlsx) that is created every time the script is run. This workbook is opened by the script and is what the user will see when the script is run. The workbook has two parts and is specifically organized for ease of modification when new or updated data becomes available. See the “tasks to be completed after migration from hornet” section below for details on how to update the spreadsheet with new data.
Part 1 contains worksheets for every lock and dam site to be regulated. Each of these “site” worksheets reference back to the “DRS.xlsx” workbook and act as a filter to isolate all the data specific to any given lock and dam. 
	Part 2 contains a worksheet “Reg Sheet”. This worksheet references each of the other worksheets within the workbook and acts as the formatting tool to create the desired look of the regulation sheet for water managers. 
	Part3 contains a worksheet “Plot Markers”. This worksheet is used to generate the band limits on each of the Lock and Dam plots on the main “reg Sheet” tab. The worksheet is referencing the entered band value and will dynamically change when entering a new value in “Reg Sheet” cell G16.
	Part4 contains a worksheet “LogicalTests”. This worksheet contains logical tests to determine the latest valid value for multiple datasets including dam outflow, gate settings, precip, temp, wind spd, and wind direction. This sheet is referenced by the main “Reg Sheet” for each site. 
	Part5 contains the worksheet “ReadMe”. This worksheet is simply a text box containing a copy of this document. 
3: the Microsoft Excel workbook (DailyRegSheettoday’sdate) is generated by the script and is simply a copy of the “DailyRegSheet_Computations” workbook with the current date added to the name. This workbook contains all the same links and formulas as the source workbook. Currently, there are no forthcoming paths to create a .pdf file within the script. The intent for this workbook is to give the user a file with a date, ready to go so the user can simply open, click “file”, then “save as” and save as a .pdf for records.
 
 
 

 
 
 
Maintenance tasks by River Regulator
 
 
Maintain Updated and Historical Backup Server copies for all of water management
Save most updated script and updated spreadsheet to your local folder “DailyRegSheet”. 
Open file explorer and navigate to: \\mvd\mvp\ECH\Water_Control_Files\Mississippi River Navigation
Copy your local folder (DailyRegSheet) and paste to the server location above. Rename the folder by adding today’s date to the beginning of the folder name. The folder name should now be in the format: YYYYMMDDDailyRegSheet. Keep the historical folders for backup purposes.  
 
 

 
Tasks to be completed once migration from “hornet” is completed by data manager:
 
Update script
Much of the data used for this regulation sheet is still “legacy” data. Once the migration from the “hornet” system is complete, the data pathnames must be updated in the script in order to access the correct data. To do so, replace every “legacy” dataset in the script with its corresponding site parameter in the updated database. The only part of the script that needs to be edited are the sections including “id” beginning on line 31 and ending on line 160. All the data for the regulation sheet is specified in this section of script. The data is labeled by type, (ie. precipitation, temperature, etc.) for ease of access. Do not move the location within the script, as this will alter the resultant workbook, and the internal functions will not work. Simply paste in the new pathname for the data where the old pathname was. This is done by navigating to the data needed in CWMSvue, right clicking on the needed data, selecting “copy pathname” and then pasting in the correct location within the script.
 
 
Update Server copy for all of water management
Save your updated script and updated spreadsheet to your desktop folder “DailyRegSheet”. 
Open file explorer and navigate to: \\mvd\mvp\ECH\Water_Control_Files\Mississippi River Navigation
Copy your desktop folder (DailyRegSheet) and paste to the server location above. Rename the folder by adding today’s date to the beginning of the folder name. The folder name should now be in the format: YYYYMMDDDailyRegSheet. 
 
Email water management notice of an updated folder on the server, and attach these instructions to the email.
Send a reminder stating when anyone copies this updated folder to their desktop to use the new information, they will need to delete the date off the folder name for the script to work properly and place the data in the folder.

![image](https://user-images.githubusercontent.com/9432394/146250603-0cd18bde-b6c3-4525-ac1e-dcae80983891.png)
USACE St. Paul District Water Management 
Mississippi Navigation Regulation Sheet 
For use in daily regulation of Lock and Dam 2 through Lock and Dam 10
Developed Jan 2019 (updated Dec 2021 by m. weier)
 
 
Author: Nathaniel Anderson 
nathaniel.d.anderson@usace.army.mil
 
Purpose and Scope:
This new regulation sheet was developed at the request of the current St. Paul District Water Management and Hydrology section chief: Elizabeth Nelsen. The project scope was to create a new version of a regulation sheet in order to support the daily orders from water management to the locks and dams of the navigable Mississippi River within the St. Paul District (LD2-LD10). 
The St. Paul District water management team is in the process of changing platforms for data management from an antiquated “hornet” system to the current Corps platform (CWMS) for water management. The new CWMS platform stores data in CWMSvue using .dss files. The new regulation sheet is intended to work with this new platform and allow the district to obtain data without accessing the antiquated “hornet” system. 
It is also the intent of the water management team to have the ability to obtain data directly from the database without needing any personnel on site (at any given lock and dam) to enter data regarding their site. This will enable water management personnel to obtain the most up to date information at all locations when making regulation decisions regardless of timely data entries by site personnel.  
Getting started with the new regulation sheet:
Add Daily_Reg_Sheet using script_downloader_mvp script (found at https://github.com/msweier/mvp-CWMS-utils) to add to active scripts in your CAVI script window like any other script
Select the “visualization” tab within your CAVI
Right click in the script area (currently located on left hand side of screen as a greyish box area containing script buttons) and select “edit”
Find “Daily_Reg_Sheet” on the left hand window and select it, then select the “Add” button to move it to the right hand side of the dialogue box. Then click “OK”
You should now be able to run the script without any errors
 
 
 
 
Running the Script
When the script is run, Microsoft Excel will open, and may prompt you to “update”. Click “Update”. There may also be a highlighted security warning appearing near the top of the screen. Click “Enable Content”. 
You can now edit and otherwise modify this sheet during regulation.  It is best practice for records to directly enter the order information into the provided blocks. When done, save as a .pdf and print.
Save as .pdf
Select file, save as
Change file type to .pdf and save
Print the regulation sheet
Select the “file” menu
Select “print”
Select desired printer
Select “landscape” orientation
Select “2 sided (flipping on long edge)”
Select the print button again
Save the Excel File
Close the Excel file
 
Basic Methodology:
This task was accomplished using the combination of a CWMS script (written in Python) and Microsoft Excel. A script was developed that collects and organizes all the data required by the Mississippi River regulator. The script then exports this data to an Excel file. A second Excel file on the user’s computer was built to reference this newly created file, rearranges the data into a usable format, and prepares it for regulation use and printing. 
 
 
Script Format:
The main body of the script is broken into 4 groups. 1st, data is assigned to a variable that is easy to use in the organization process. 2nd, the data is acquired by retrieving the data from the database and renaming the variables to items that make sense to all water managers. 3rd, the variables are all added to a compiled dataset. 4th, the script does a number of operations involving Microsoft Excel including the generation of a new Excel workbook, opening a second workbook, and creating a copy of the second workbook with the current date.
 
DATA
The script pulls data from the CWMSvue database. It pulls data only within the time window set in the script. The time window is set in the script by looking at today’s date, then going back 5 days, and beginning at 1400 UTC (0800 CST). Data is then pulled through whatever time the script is run, meaning the later in the day the script is run, the more data should be available in the database.
 
Excel Workbook Format:
1: The Microsoft Excel workbook (DRS.xlsx) is overwritten every time the script is run. This workbook contains all of the data obtained from CWMSvue by the script. This data is organized in a specific format and affects the entire flow of functions. Changes to this format in the script must be made in a specific way in order to maintain the integrity of the regulation sheet and all supporting processes.
2: The Microsoft Excel workbook (DailyRegSheet_Computations) was developed separately from the script. It is built to reference the workbook (DRS.xlsx) that is created every time the script is run. This workbook is opened by the script and is what the user will see when the script is run. The workbook has two parts and is specifically organized for ease of modification when new or updated data becomes available. See the “tasks to be completed after migration from hornet” section below for details on how to update the spreadsheet with new data.
Part 1 contains worksheets for every lock and dam site to be regulated. Each of these “site” worksheets reference back to the “DRS.xlsx” workbook and act as a filter to isolate all the data specific to any given lock and dam. 
	Part 2 contains a worksheet “Reg Sheet”. This worksheet references each of the other worksheets within the workbook and acts as the formatting tool to create the desired look of the regulation sheet for water managers. 
	Part3 contains a worksheet “Plot Markers”. This worksheet is used to generate the band limits on each of the Lock and Dam plots on the main “reg Sheet” tab. The worksheet is referencing the entered band value and will dynamically change when entering a new value in “Reg Sheet” cell G16.
	Part4 contains a worksheet “LogicalTests”. This worksheet contains logical tests to determine the latest valid value for multiple datasets including dam outflow, gate settings, precip, temp, wind spd, and wind direction. This sheet is referenced by the main “Reg Sheet” for each site. 
	Part5 contains the worksheet “ReadMe”. This worksheet is simply a text box containing a copy of this document. 
3: the Microsoft Excel workbook (DailyRegSheettoday’sdate) is generated by the script and is simply a copy of the “DailyRegSheet_Computations” workbook with the current date added to the name. This workbook contains all the same links and formulas as the source workbook. Currently, there are no forthcoming paths to create a .pdf file within the script. The intent for this workbook is to give the user a file with a date, ready to go so the user can simply open, click “file”, then “save as” and save as a .pdf for records.
 
 
 

 
 
 
Maintenance tasks by River Regulator
 
 
Maintain Updated and Historical Backup Server copies for all of water management
Save most updated script and updated spreadsheet to your local folder “DailyRegSheet”. 
Open file explorer and navigate to: \\mvd\mvp\ECH\Water_Control_Files\Mississippi River Navigation
Copy your local folder (DailyRegSheet) and paste to the server location above. Rename the folder by adding today’s date to the beginning of the folder name. The folder name should now be in the format: YYYYMMDDDailyRegSheet. Keep the historical folders for backup purposes.  
 
 

 
Tasks to be completed once migration from “hornet” is completed by data manager:
 
Update script
Much of the data used for this regulation sheet is still “legacy” data. Once the migration from the “hornet” system is complete, the data pathnames must be updated in the script in order to access the correct data. To do so, replace every “legacy” dataset in the script with its corresponding site parameter in the updated database. The only part of the script that needs to be edited are the sections including “id” beginning on line 31 and ending on line 160. All the data for the regulation sheet is specified in this section of script. The data is labeled by type, (ie. precipitation, temperature, etc.) for ease of access. Do not move the location within the script, as this will alter the resultant workbook, and the internal functions will not work. Simply paste in the new pathname for the data where the old pathname was. This is done by navigating to the data needed in CWMSvue, right clicking on the needed data, selecting “copy pathname” and then pasting in the correct location within the script.
 
 
Update Server copy for all of water management
Save your updated script and updated spreadsheet to your desktop folder “DailyRegSheet”. 
Open file explorer and navigate to: \\mvd\mvp\ECH\Water_Control_Files\Mississippi River Navigation
Copy your desktop folder (DailyRegSheet) and paste to the server location above. Rename the folder by adding today’s date to the beginning of the folder name. The folder name should now be in the format: YYYYMMDDDailyRegSheet. 
 
Email water management notice of an updated folder on the server, and attach these instructions to the email.
Send a reminder stating when anyone copies this updated folder to their desktop to use the new information, they will need to delete the date off the folder name for the script to work properly and place the data in the folder.
