import sys
import pandas as pd
import openpyxl



def main():
	# Creates data frame from a passed excel file
	df = pd.read_excel(r'C:\Users\dbowe\source\repos\Well Life Tracker - ARC\job history - 15-36 pad.xlsx')
	
	# Creates a dictionary of UWIs from the passed worksheet
	listOfWells = {}
	uniqueWells = set()

	# Generates list of unique wells from the excel (data frame)
	# df['UWI'] is a data frame series
	for i in df['UWI']:
		uniqueWells.add(i)

	# Creates Well Objects for each unique UWI
	for i in uniqueWells:
		listOfWells[i] = Well(i)

	# Adds jobs to each well Object
	for index, row in df.iterrows():
		listOfWells[row["UWI"]].addJob(row)

	# Prints number of wells to console, as a check 
	for i in listOfWells:
		print (f"UWI {listOfWells[i].UWI}, has {listOfWells[i].numOfJobs} number of jobs!")

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


