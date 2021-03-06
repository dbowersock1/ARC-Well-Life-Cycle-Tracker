import sys
import pandas as pd
import openpyxl
import json
import jsonpickle
import datetime
from operator import itemgetter

# To Do

def main():
	
	# ListOfWells is a dictionary of objects. Key = UWI
	listOfWells = retrieveFile()
	
	# The scope below is for updating the well list!!
	# Create method that opens excel file & adds any UWIs & Jobs to listOfWells
	# Must have link to database or will crash!
	linkImport =r'E:\all wells ante.xlsx'
	listOfWells = listUpdater(listOfWells, linkImport)
	# Prints number of wells to console, as a check 
	for i in listOfWells:
		print (f"UWI {listOfWells[i].UWI} on Pad {listOfWells[i].pad}, has had {listOfWells[i].wellServicingJobs} WS Jobs! This well has an average run life of {listOfWells[i].runLife}.")
	# Stores well database in json file
	storeFile(listOfWells)
	# Creates excel file 
	linkExport = r"E:\datacollection.xlsx"
	createExcel(listOfWells, linkExport)

	# The scope below is for more advanced data analysis; namely to calculate the run life average
	#! Build in case handling exceptions
	## linkExportDailyRunLife = r'E:\datacollection2.xlsx'
	## DailyRunLife(listOfWells, linkExportDailyRunLife) 

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
def listUpdater(listOfWells, link):
	uniqueWells = []
	for key in listOfWells:
		uniqueWells.append(key)

	# Creates data frame from a passed excel file
	df = pd.read_excel(link)
	
	# Generates list of unique wells from the excel (data frame)
	excelUniqueWells = set()
	for i in df['UWI']:
		excelUniqueWells.add(i)

	# Creates object for any wells not already in data base file!
	diff = excelUniqueWells.difference(uniqueWells)
	for i in diff:
		listOfWells[i] = Well(i)
	
	
	# Adds jobs to each UWI, if not already populated (works on start date)
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

# Creates excel file w/ pertinent information
def createExcel (listOfWells, link):
	dictToExport = {}
	columns = ["Pad", "Avg Run Life", "Days Since Failure", "Last WRK", "Num of WS Jobs"]
	for i in listOfWells:
		dictToExport[i] = [listOfWells[i].pad, listOfWells[i].runLife, listOfWells[i].currentRunLife, listOfWells[i].wrkArray[-1]["startDate"], listOfWells[i].wellServicingJobs]
	df = pd.DataFrame(dictToExport, index = columns)
	df.to_excel(r"C:\Users\dbowe\source\repos\Well Life Tracker - ARC\datacollection.xlsx")
	df.to_excel(link)
	
	
def DailyRunLife(Wells, exportLink):
	dateArray = []
	# array of dates
	# The array indices could be "days ago"
	# ! need to build in error catching here
	today = (pd.to_datetime("today")).to_pydatetime().date()
	for i in range(0, 365*3, 1):
		dateInIt = today - datetime.timedelta(i)
		dateArray.append({"date" : dateInIt})
		for j in Wells:
			for k in reversed(range(0, len(Wells[j].wrkArray))):
				wrkDate = Wells[j].wrkArray[k]["startDate"].to_pydatetime().date()
				if dateInIt > wrkDate: 
					daysFromWrk = (dateInIt - wrkDate).days
					dateArray[i][j] = daysFromWrk
					break

	df=pd.DataFrame(dateArray)
	df.to_excel(exportLink)
	
	

# UWI Objects
class Well: 
	def __init__(self, UWI):
		self.UWI = UWI
		self.pad = ""
		self.numOfJobs=0
		self.wellServicingJobs=0
		self.wrkArray = []
		self.runLife = 0
		self.currentRunLife = 0

	def addJob(self, dfSeries):
		self.numOfJobs+=1
		self.pad = dfSeries["Pad Name"]
		jobDict = { 
			"jobCategory" : dfSeries["Job Category"],
			"primaryJobType": dfSeries["Primary Job Type"] ,
			"startDate" : dfSeries["Start Date"],
			"endDate" : dfSeries["End Date"]
			}
		self.wrkArray.append(jobDict)

	def averageRunTime(self):
		# Values used in logic
		wellServicingCount = 0
		avgCount = 0
		avg = 0
		lastWrkDate = 0
		diff = []
		# sorts wrkArray based on start date. Logic requires this.
		self.wrkArray= sorted(self.wrkArray, key = itemgetter('startDate'))
		# calculates and populates wrk Array in well object
		for job in self.wrkArray:
			# Catch
			if (pd.isnull(job["startDate"])):
				continue
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
		self.wellServicingJobs=wellServicingCount
		# Catch 
		if (wellServicingCount == 0):
			self.runLife = "Cannot calculate average! There is 0 WS Jobs"
			self.currentRunLife = "Cannot calculate current run time! There is 0 WS Jobs" 
			return
		# Calculates current run life and adds value to well object
		a = self.wrkArray[-1]["startDate"]
		lastWRK = a.to_pydatetime().date()
		today = (pd.to_datetime("today")).to_pydatetime().date()
		self.currentRunLife = (today - lastWRK).days
		# Calculates average and adds value to well object 
		# Catch
		if (wellServicingCount==1):
			self.runLife = "Cannot calculate average! Only 1 Well Servicing Job"
			return
		sumDays = 0
		for date in diff:
			dateInt = date.days
			sumDays += dateInt
		avg = sumDays / avgCount
		self.runLife = round(avg)

# Boiler plate
if __name__ == "__main__":
	main()


