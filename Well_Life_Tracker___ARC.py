import sys
import pandas as pd
import openpyxl



def main():
	df = pd.read_excel(r'C:\Users\dbowe\source\repos\Well Life Tracker - ARC\job history - 15-36 pad.xlsx')
	# Comment below, stops the print from mincing rows & columns
	# pd.set_option('display.max_rows', None, 'display.max_columns', None)
	
	# Creates a dictionary of UWIs from the passed worksheet
	listOfWells = {}
	# df['UWI'] is a dataframe series
	# Note that the code below cycles through all the entry points, regardless of duplicate entries! Fix
	# Would be nice to iterate through the entire sheet once!
	for i in df['UWI']:
		listOfWells[i] = Well(i)

	for key in listOfWells:
		print(listOfWells[key].UWI)

	# adds job to individual UWI
	print(listOfWells["102/02-12-066-25W5/00"])
	print(df.loc[0])
	listOfWells["102/02-12-066-25W5/00"].addJob(df.loc[0])
	print(listOfWells["102/02-12-066-25W5/00"].numOfJobs)

	print("End")

class Well: 
	def __init__(self, UWI):
		self.UWI = UWI
		self.numOfJobs=0
		self.wrkArray = []

	def addJob(self, dfSeries):
		self.numOfJobs+=1
		jobDict = { 
			"jobCategory" : dfSeries["Job Category"],
			"primaryJobType": dfSeries["Primary Job Type"] ,
			"startDate" : dfSeries["Start Date"],
			"endDate" : dfSeries["End Date"]
			}
		self.wrkArray.append(jobDict)

if __name__ == "__main__":
	main()


