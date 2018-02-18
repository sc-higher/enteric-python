##################################################################################################################
##
## NEXT STEPS
## 1. Determine the 'standard curve' from previous LAMP performance testing. -- CHECK
## 2. Fit the average time to result for each sample/gene to the standard curve to give approximate CFU. -- CHECK
## 3. See how the CFU given by different genes compares (i.e. a sample both LT and STh positive - does the CFU
##    given by the average time to result for each gene match?)
## 4. Output the data from all samples to a single file.
##
##################################################################################################################	

import os
import time
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog


## This section is for creation of a basic GUI to select the directory that contains the CSV files to be used.

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


## filedate DESCRIPTION

def filedate(filename):

	# Read the file date into 'dateperf' and format to MM/DD/YYYY
	dateperf = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(filename)))
	
	return dateperf


## fetchCSV DESCRIPTION

def fetchCSV(filename):

	# Use only the first 11 columns of raw Amplifire CSV
	cols = list(range(11))
	
	# Read the CSV to new dataframe 'df'. Skip the first 21 rows and use only the first 11 columns, specified in variable 'cols'
	df1 = pd.read_csv(filename, skiprows=21, usecols=cols)

	# Set the column header values
	df1.columns = ['Cycle','Temperature','Time (minutes)','LT 1','LT 2','STh 1','STh 2','STp','ipaH 1','ipaH 2','Positive'] 

	# Replace the NaN values in the 'Time (minutes)' column with actual time values
	df1['Time (minutes)'] = df1['Cycle']*(1/6)

	# Round the values in 'Time (minutes)' to two decimal places
	df1['Time (minutes)'] = df1['Time (minutes)'].round(2)
	
	# Subtract initial value so that first time value is zero.
	df1['Time (minutes)'] = df1['Time (minutes)']-.17
	
	return df1


## Quantitative Analysis DESCRIPTION
	
def Standard_Curves(time_LT1,time_LT2,time_STh1,time_STh2,time_STp,time_ipaH1,time_ipaH2):
	
	# LT Standard Curve: y = 41.839x^(-0.031)  R^2 = 0.9475
	CFU_LT1 = (time_LT1/41.839)**(1/-0.031)
	CFU_LT2 = (time_LT2/41.839)**(1/-0.031)
	
	# STh Standard Curve: y = 66.722x^(-0.057)  R^2 = 0.959
	CFU_STh1 = (time_STh1/66.722)**(1/-0.057)
	CFU_STh2 = (time_STh2/66.722)**(1/-0.057)
	
	# STp Standard Curve: y = 53.737x^(-0.052)  R^2 = 0.965
	CFU_STp = (time_STp/53.737)**(1/-0.052)
	
	# ipaH Standard Curve: y = 75.493x^(-0.046)  R^2 = 0.9999
	CFU_ipaH1 = (time_ipaH1/75.493)**(1/-0.046)
	CFU_ipaH2 = (time_ipaH2/75.493)**(1/-0.046)
	
	return CFU_LT1, CFU_LT2, CFU_STh1, CFU_STh2, CFU_STp, CFU_ipaH1, CFU_ipaH2
	
def Semi_Quant_Analysis(df1, csv_name):
	
	cols = ['Cycle','Temperature','Time (minutes)','LT 1','LT 2','STh 1','STh 2','STp','ipaH 1','ipaH 2','Positive']
	
	# Create a new dataframe to store Max RFU, RFU 10m, etc for each sample. Set all values to NaN.
	df2 = pd.DataFrame(np.nan, index=['Max RFU', 'RFU 10m', 'True Midpoint', 'Time to Result', 'Estimated CFU/mL'], columns=cols)
		
	# Set cell values for 'Max RFU'
	df2.iat[0,3] = df1['LT 1'].max()
	df2.iat[0,4] = df1['LT 2'].max()
	df2.iat[0,5] = df1['STh 1'].max()
	df2.iat[0,6] = df1['STh 2'].max()
	df2.iat[0,7] = df1['STp'].max()
	df2.iat[0,8] = df1['ipaH 1'].max()
	df2.iat[0,9] = df1['ipaH 2'].max()
	
	# Set cell values for 'RFU 10m' and 'True Midpoint'
	for i in range(3,10):
		df2.iat[1,i] = df1.iat[60,i] # RFU 10m
		df2.iat[2,i] = (df2.iat[0,i]/2)+(df2.iat[1,i]/2) # True Midpoint
		
	# Calcuate the time to result
	for i in range(3,10): # Run through all genes (LT 1, LT 2, STh 1, etc)
		if df2.iat[2,i] - df2.iat[1,i] > 2000: # Check if positive by difference between True Midpoint and RFU 10m
			for j in range(df1.shape[0]-1):	# Length of column i.e. number of timepoints form original CSV
				if df2.iat[2,i] < df1.iat[j+1,i] and df2.iat[2,i] > df1.iat[j,i]: # Check if midpoint is between two adjacent time values
					df2.iat[3,i] = df1.iat[j,2] # If so, set the lower time value as the Time to Result in df2
							
	# Feed Time to Result into Standard_Curves to estimate CFU/mL
	cfu = Standard_Curves(df2.iat[3,3],df2.iat[3,4],df2.iat[3,5],df2.iat[3,6],df2.iat[3,7],df2.iat[3,8],df2.iat[3,9])
	cfur = [round(i, 0) for i in cfu]
	
	for i in range(3,10):
		df2.iat[4,i] = cfur[i-3]
		
	# Export df2 to csv, appending each new sample
	with open('quantAnalysis.csv', 'a') as f:
		outwriter=csv.writer(f, delimiter=',')
		outwriter.writerow([csv_name])
		df2.to_csv(f, header=False)
		outwriter=csv.writer(f, delimiter=',')
		outwriter.writerow([])
		
	f.close()
	
	
	return df2
	

## Create a function 'plotCSV' that will plot the data from the altered CSV files and save it to <PLACE> 

def plotCSV(df1, dateperf, graphname):
	# Plot the data
	plt.plot(df1['Time (minutes)'], df1['LT 1'], 'b', label='LT 1')
	plt.plot(df1['Time (minutes)'], df1['LT 2'], 'b--', label='LT 2')
	plt.plot(df1['Time (minutes)'], df1['STh 1'], 'r', label='STh 1') 
	plt.plot(df1['Time (minutes)'], df1['STh 2'], 'r--', label='STh 2')
	plt.plot(df1['Time (minutes)'], df1['STp'], 'g', label='STp')
	plt.plot(df1['Time (minutes)'], df1['ipaH 1'], 'm', label='ipaH 1')
	plt.plot(df1['Time (minutes)'], df1['ipaH 2'], 'm--', label='ipaH 2') 
	plt.plot(df1['Time (minutes)'], df1['Positive'], 'k', label='Positive')

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
			graphname = name[:7]
			name = os.path.join(root, name)
			dateperf = filedate(name)
			y = fetchCSV(name)
			plotCSV(y, dateperf, graphname)
			plt.close('all')
			Semi_Quant_Analysis(y, graphname)
			
	# for name in dirs:
		# if name.endswith('.csv'):
			# graphname = name[:7]
			# name = os.path.join(root, name)
			# y = fetchCSV(name)
			# plotCSV(y, dateperf, graphname)
			# plt.close('all')
			# Semi_Quant_Analysis(y, graphname)

print('\n' + "Done." + '\n')	
	

# csv = fetchCSV('C:/Users/PCR/Desktop/2270_JHU 68C 50 Min 3000RFU_0_2017_8_24_13_15_28_final.csv')

# print(Semi_Quant_Analysis(csv))
# # print(csv)
