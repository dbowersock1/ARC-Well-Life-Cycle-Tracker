import sys
import pandas as pd
import openpyxl



def main():
	df = pd.read_excel(r'C:\Users\dbowe\source\repos\Well Life Tracker - ARC\job history - 15-36 pad.xlsx')
	# Comment below, stops the print from mincing rows & columns
	# pd.set_option('display.max_rows', None, 'display.max_columns', None)
	
	# Creates a dictionary of UWIs from the passed worksheet
	listOfWells = {}
	for i in df['UWI']:
		listOfWells[i] = Well(i)
		print(listOfWells[i].UWI)
	print("End")

class Well: 
	def __init__(self,UWI):
		self.UWI = UWI

if __name__ == "__main__":
	main()


