import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog

## This section is for creation of a (very) basic GUI to select the directory that contains the CSV files to be used.

def askdirectory():
  dirname = filedialog.askdirectory()
  if dirname:
    var.set(dirname)

def UserFileInput(status,name):
  optionFrame = Frame(root)
  optionLabel = Label(optionFrame)
  optionLabel["text"] = name
  optionLabel.pack(side=LEFT)
  text = status
  var = StringVar(root)
  var.set(text)
  w = Entry(optionFrame, textvariable= var)
  w.pack(side = LEFT)
  optionFrame.pack()
  return w, var

def Print_entry():
  print(var.get())
  
def okClose():
  root.destroy()

if __name__ == '__main__':
  root = Tk()
  root.title("Sean's fetchCSV Application")
  root.geometry('350x200')
  
  messagetext = "This application is designed to quickly and easily create usable graphs from Amplifire CSV output files. \n \n \
	Please select a directory that contains the desired CSV files (Note: This program will also search subdirectories and will include all CSV-type files. \n"
	
  x = Message(text=messagetext, width=300)
  x.pack()
  
  dirBut = Button(root, text='Browse...', command = askdirectory)
  dirBut.pack(side = RIGHT)
  getBut = Button(root, text='Print Entry Text', command = Print_entry)
  getBut.pack(side = BOTTOM)
  quitBut = Button(root, text='OK', command = okClose)
  quitBut.pack(side = BOTTOM)

  w, var = UserFileInput("", "Directory")

  root.mainloop()
  
maindir = var.get()



## DESCRIPTION

def filedate(filename):

	# Read the file date into 'dateperf' and format to MM/DD/YYYY
	dateperf = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(filename)))
	
	return(dateperf)


## Create a function 'fetchCSV' that will fetch a raw Amplifire CSV file and prepare it for plotting

def fetchCSV(filename):

	# Use only the first 11 columns of raw Amplifire CSV
	cols = list(range(11))
	
	# Read the CSV to new dataframe 'df'. Skip the first 21 rows and use only the first 11 columns, specified in variable 'cols'
	df = pd.read_csv(filename, skiprows=21, usecols=cols)

	# Set the column header values
	df.columns = ['Cycle','Temperature','Time (minutes)','LT 1','LT 2','STh 1','STh 2','STp','ipaH 1','ipaH 2','Positive'] 

	# Replace the NaN values in the 'Time (minutes)' column with actual time values
	df['Time (minutes)'] = df['Cycle']*(1/6)

	# Round the values in 'Time (minutes)' to two decimal places
	df['Time (minutes)'] = df['Time (minutes)'].round(2)
	
	return(df)

## Create a function 'plotCSV' that will plot the data from the altered CSV files and save it to <PLACE> 

def plotCSV(df, dateperf, graphname):
	# Plot the data
	plt.plot(df['Time (minutes)'], df['LT 1'], 'b', label='LT 1')
	plt.plot(df['Time (minutes)'], df['LT 2'], 'b--', label='LT 2')
	plt.plot(df['Time (minutes)'], df['STh 1'], 'r', label='STh 1') 
	plt.plot(df['Time (minutes)'], df['STh 2'], 'r--', label='STh 2')
	plt.plot(df['Time (minutes)'], df['STp'], 'g', label='STp')
	plt.plot(df['Time (minutes)'], df['ipaH 1'], 'm', label='ipaH 1')
	plt.plot(df['Time (minutes)'], df['ipaH 2'], 'm--', label='ipaH 2') 
	plt.plot(df['Time (minutes)'], df['Positive'], 'k', label='Positive')

	# Add plot title, labels, etc 	
	plt.xlabel('Time (minutes)')
	plt.ylabel('RFU')
	plt.title('Sample ' + graphname + '\n' + dateperf)
	plt.grid(True)
	plt.legend(loc='upper left')

	# Save the plot to .png file and show the plot
	plt.savefig('sample' + graphname + '.png')
	print(graphname + ' Done.')
	
## Run fetchCSV on all CSV files in the directory 'maindir' which was specified by the user.

# Set directory to 'C:\Users\PCR\Desktop\Sean\Python'
directory = maindir

# Use os.walk to list all CSV files in the directory tree
print('\n' + "The CSV files in this folder are:" + '\n')
for root, dirs, files in os.walk(directory):
	for name in files:
		if name.endswith('.csv'):
			print(name)
	for name in dirs:
		if name.endswith('.csv'):
			print(name)

# Use os.walk to alter raw CSV files using the fetchCSV function
print('\n' + "Now altering CSV files and plotting data..." + '\n')
for root, dirs, files in os.walk(directory):
	for name in files:
		if name.endswith('.csv'):
			graphname = name[:3]
			name = os.path.join(root, name)
			dateperf = filedate(name)
			y = fetchCSV(name)
			plotCSV(y, dateperf, graphname)
			plt.close('all')
			
	for name in dirs:
		if name.endswith('.csv'):
			graphname = name[:3]
			name = os.path.join(root, name)
			y = fetchCSV(name)
			plotCSV(y, dateperf, graphname)
			plt.close('all')

print('\n' + "Done." + '\n')
