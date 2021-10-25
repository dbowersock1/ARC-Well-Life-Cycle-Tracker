import sys
import pandas as pd
import openpyxl
import json
import jsonpickle

# To Do
# Function test - split apart excel into 2 files and see if it can handle it!

def main():
	
	# ListOfWells is a dictionary of objects. Key = UWI
	listOfWells = retrieveFile()
	
	# Create method that opens excel file & adds any UWIs & Jobs to listOfWells
	listOfWells = listUpdater(listOfWells)

	# Prints number of wells to console, as a check 
	for i in listOfWells:
		print (f"UWI {listOfWells[i].UWI}, has {listOfWells[i].numOfJobs} number of jobs! This well has an average run life of {listOfWells[i].runLife}.")
		print (f"It has been {listOfWells[i].currentRunLife} days without a failure!")
		print()
	
	storeFile(listOfWells)

	print ("End")

# Opens data text file, converts from JSON to object, returns 
def retrieveFile ():
	with open ('data.txt', 'r') as infile:
		try:
			jsonthawed = json.load(infile)
			thawed = jsonpickle.decode(jsonthawed)
		except:
			thawed = {}
	return thawed

# Opens excel file, stores data in listOfWells Dictionary
def listUpdater(listOfWells):
	uniqueWells = []
	for key in listOfWells:
		uniqueWells.append(key)

	# Creates data frame from a passed excel file
	df = pd.read_excel(r'C:\Users\dbowe\source\repos\Well Life Tracker - ARC\job history - 15-36 pad.xlsx')
	
	# Generates list of unique wells from the excel (data frame)
	# df['UWI'] is a data frame series
	excelUniqueWells = set()
	for i in df['UWI']:
		excelUniqueWells.add(i)

	# Creates object for any wells not already in file!
	diff = excelUniqueWells.difference(uniqueWells)
	for i in diff:
		listOfWells[i] = Well(i)

	
	# Adds jobs to each well Object
	# Checks to ensure jobs are not already populated
	for well in excelUniqueWells:
		#creates unique list of start dates for each well 
		uniqueDataFrame = df[df['UWI']==well]
		uniqueWrkDates = []
		for i in listOfWells[well].wrkArray:
			uniqueWrkDates.append(i["startDate"])
		for index, row in uniqueDataFrame.iterrows():
			# !checks no identical job, based on start date, is already populated in well
			if (row["Start Date"] not in uniqueWrkDates):
				listOfWells[row["UWI"]].addJob(row)
			else:
				continue
		
	# Calculates avg Run Life for all Wells
	for i in listOfWells:
		listOfWells[i].averageRunTime()

	return listOfWells

# Updates listOfWells Dictionary back to to the data file
def storeFile(listOfWells):
	# Write information to JSON File
	frozen = jsonpickle.encode(listOfWells)
	with open('data.txt', 'w') as outfile:
		json.dump(frozen, outfile)


# UWI Objects
class Well: 
	def __init__(self, UWI):
		self.UWI = UWI
		self.numOfJobs=0
		self.wrkArray = []
		self.runLife = 0
		self.currentRunLife = 0

	def addJob(self, dfSeries):
		self.numOfJobs+=1
		jobDict = { 
			"jobCategory" : dfSeries["Job Category"],
			"primaryJobType": dfSeries["Primary Job Type"] ,
			"startDate" : dfSeries["Start Date"],
			"endDate" : dfSeries["End Date"]
			}
		self.wrkArray.append(jobDict)

	def averageRunTime(self):
		wellServicingCount = 0
		avgCount = 0
		avg = 0
		lastWrkDate = 0
		diff = []
		#populates array of diff
		for job in self.wrkArray:
			if job["jobCategory"]=="Well Servicing":
				wellServicingCount += 1 
				# populates first WRK date
				if lastWrkDate == 0 :
					lastWrkDate = job["startDate"]
				# Populates diff array so the average can be calculated further down
				else: 
					diffn = job["startDate"] - lastWrkDate
					diff.append(diffn)
					lastWrkDate = job["startDate"]
					avgCount += 1 
			else: 
				continue
		# calculates average
		sumDays = 0
		for date in diff:
			dateInt = date.days
			sumDays += dateInt
		avg = sumDays / avgCount
		self.runLife = round(avg)
		#populates currentRunLife
		a = self.wrkArray[-1]["startDate"]
		lastWRK = a.to_pydatetime().date()
		today = (pd.to_datetime("today")).to_pydatetime().date()
		self.currentRunLife = (today - lastWRK).days

# Boiler plate
if __name__ == "__main__":
	main()


