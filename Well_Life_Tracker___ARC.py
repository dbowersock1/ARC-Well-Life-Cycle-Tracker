import sys
import pandas as pd
import openpyxl
import json
import jsonpickle

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
		
	# Calculates avg Run Life for all Wells
	for i in listOfWells:
		listOfWells[i].averageRunTime()

	# Prints number of wells to console, as a check 
	for i in listOfWells:
		print (f"UWI {listOfWells[i].UWI}, has {listOfWells[i].numOfJobs} number of jobs! This well has an average run life of {listOfWells[i].runLife}.")
		print (f"It has been {listOfWells[i].currentRunLife} days without a failure!")
		print()
		
	# Write information to JSON File
	frozen = jsonpickle.encode(listOfWells)
	with open('data.txt', 'w') as outfile:
		json.dump(frozen, outfile)

	# Retreive informtion from JSON File
	with open ('data.txt', 'r') as infile:
		jsonthawed = json.load(infile)
	thawed = jsonpickle.decode(jsonthawed)

	# Print to see if back and forth worked!
	print("Test to see if file has been encoded and decoded correctly!")
	print()
	for i in thawed:
		print (f"UWI {thawed[i].UWI}, has {thawed[i].numOfJobs} number of jobs! This well has an average run life of {thawed[i].runLife}.")
		print (f"It has been {thawed[i].currentRunLife} days without a failure!")
		print()

	print ("End")

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

if __name__ == "__main__":
	main()


