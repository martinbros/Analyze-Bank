import pretty_errors
import pandas as pd
from func import *
import argparse
import re


def delete_files_in_directory(directory_path, extensions=[".txt", ".png"]):
	try:
		files = os.listdir(directory_path)
		for file in files:
			file_path = os.path.join(directory_path, file)
			if os.path.isfile(file_path):

				for extention in extensions:
					if file_path.endswith(extention):
						os.remove(file_path)

	except OSError:
		print("Error occurred while deleting files.")


catagoryPath = "masterCatagories.csv"

autographDict = {"path" : "wfAutograph.csv",
				"ID" : "Autograph",
				"regexStrings" : ["ONLINE PAYMENT THANK YOU"]}

platinumDict = {"path" : "wfPlatinum.csv",
				"ID" : "Platinum",
				"regexStrings" : ["ONLINE PAYMENT THANK YOU"]}

checkingDict = {"path" : "wfChecking.csv",
				"ID" : "Checking",
				"regexStrings" : ["ONLINE TRANSFER REF #[A-Z0-9]* TO WELLS FARGO AUTOGRAPH", "ONLINE TRANSFER REF #[A-Z0-9]* TO PLATINUM"]}

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--year", type=int, help="Pick a Year")
parser.add_argument("-q", "--quarter", type=int, choices=[1, 2, 3, 4], help="Pick a Quarter")
parser.add_argument("-p", "--path", type=str, help="CSV path to update graphs and log")

args = parser.parse_args()

if (args.path is not None) and (re.search(r".*(20)\d{2}(_Q)[1-4].*(transactionsCatagorized.csv)", args.path)):  # Check if it is a good string
	directory = args.path.rsplit("\\", 1)[0]
	graphP = directory + "\\graphs"

	delete_files_in_directory(directory)
	delete_files_in_directory(directory + "\\graphs")

	catCkAcct = pd.read_csv(args.path)
	catCkAcct["Date"] = pd.to_datetime(catCkAcct["Date"])  # Convert the "Date" column to datetime

elif args.year and args.quarter:

	# Import accounts, remove rows relating to payments
	autoDF, rmvAutoDF = removeRows2(autographDict)
	platDF, rmvPlatDF = removeRows2(platinumDict)
	chckDF, rmvChckDF = removeRows2(checkingDict)

	# Combine all accounts
	ckAccount = pd.concat([chckDF, platDF, autoDF])
	rmvDF = pd.concat([rmvChckDF, rmvPlatDF, rmvAutoDF])

	# Catagorize transactions
	accountDF, newCatDf = catagorizeTransactions(ckAccount, catagoryPath)
	newCatDf.to_csv("masterCatagories.csv", index=False)

	# Create the directory in which everything will be saved, also slice down the transcations by date
	saveP, graphP, catCkAcct = sliceDfCreateDir2(accountDF, args.year, args.quarter)

	# Save the generated tables
	catCkAcct.to_csv(saveP + "\\transactionsCatagorized.csv", index=False)
	rmvDF.to_csv(saveP + "\\removedTransactions.csv", index=False)
	newCatDf.to_csv(saveP + "\\updatedCatagories.csv", index=False)

try:
	# Create the charts/graphs for the quarterly report
	saveLineGraphs(catCkAcct, "catagory", graphP)
	genPieCharts(catCkAcct, graphP)
	genStackedBar("Transactions Grouped by Name", catCkAcct, "name", graphP + "\\barName.png")
	genStackedBar("Transactions Grouped by Catagory", catCkAcct, "catagory", graphP + "\\barCatagory.png")
	genLineChart("Checking Account Timeline", catCkAcct.copy(), graphP + "\\lineChecking.png")
except NameError:
	print("Verify Command Line Arguments are Correct")
