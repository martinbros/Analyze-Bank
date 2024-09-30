import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime
import os
import sys
import pretty_errors
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#################################
#
# Import data, and remove rows that match regex
#
# accountPath: string ~ path of where csv file is located
# cardID: string ~ tag applied to data for reference to which account the expense was applied
# regexStrings: list ~ list of regex expressions for transactions to be removed
#
#################################
def removeRows(accountPath, cardID, regexStrings):

	accountDF = pd.read_csv(accountPath, usecols=[0, 1, 4], names=["Date", "Transaction", "Info"])  # Import checking account CSV for processing
	accountDF["remove"] = False
	accountDF["cardID"] = cardID

	for regexString in regexStrings:
		filterRows = accountDF["Info"].str.contains(regexString)  # Find the entries that match the regex
		accountDF["remove"] = accountDF["remove"] | filterRows

	return accountDF[~accountDF["remove"]].drop(["remove"], axis=1), accountDF[accountDF["remove"]].drop(["remove"], axis=1)  # kept transactions, transactions that were removed


#################################
#
# Used to slice dataframe by quarters and create folder
#
#
# accountDF: pandas dataframe ~ contains transaction information
# year: int ~ Year which the dataframe will be sliced
# quarter: int ~ Quarter which the dataframe will be sliced
#
#################################
def sliceDfCreateDir2(accountDF, year, quarter):

	accountDF["Date"] = pd.to_datetime(accountDF["Date"])  # Convert the "Date" column to datetime
	accountDF.sort_values(by=["Date"], inplace=True)  # Order the dataframe
	accountDF = accountDF[(accountDF['Date'].dt.year == year) & (accountDF["Date"].dt.quarter == quarter)]

	savePath = "%s_Q%s_working" % (year, quarter)
	grphPath = savePath + "\\graphs"

	try:
		os.makedirs(grphPath)
	except OSError:
		print("Failed to create the directory %s" % grphPath)
	else:
		print("Successfully created the directory %s" % grphPath)

	return savePath, grphPath, accountDF


#################################
#
# Automatic and user input catagorization of a transaction
#
# accountDF: pandas dataframe ~ contains transaction information
# catagoryPath: string ~ path of where the catagory pairing document is found
#
#################################
def catagorizeTransactions(accountDF, catagoryPath):
	print("Catagorizing Account...")
	catagoryDF = pd.read_csv(catagoryPath)  # Import catagory CSV for processing
	allNewCatDf = pd.DataFrame()
	smList = []
	catList = []

	for rowAcc in accountDF.itertuples():  # Iterate down account transactions (data frame)
		foundBool = False  # Set initial conditions, to catagory paired to transaction

		for rowCat in catagoryDF.itertuples():  # Iterate through catagory data frame

			if fuzz.token_set_ratio(rowCat.name.lower(), rowAcc.Info.lower()) > 95:  # Lower case catagory name and transaction information, compare
				if pd.isna(rowCat.ID):  # If a different ID for match is not present
					smList.append(rowCat.name)  # append name to transaction in smList
				else:  # If a separate ID is present
					smList.append(rowCat.ID)  # append ID to transaction in smList

				catList.append(rowCat.cat)  # append catagory to catList
				foundBool = True  # Set found match to true
				break  # break catagory data frame iterations

		if foundBool is False:  # If match is not found
			print("$%s -- %s" % (rowAcc.Transaction, rowAcc.Info))  # Print transaction information to the user
			print(catagoryDF.cat.unique())  # Print for the user all of the catagories within the catagory data frame
			inName = input("Input name:")  # Prompt user for filter string
			inCat = input("Catagory:")  # Prompt user for catagory string
			print()

			newCatDF = pd.DataFrame({"name": [inName], "cat": [inCat]})
			catagoryDF = catagoryDF.append(newCatDF)  # Add new name and catagory to the catagory data frame

			allNewCatDf = allNewCatDf.append(newCatDF)  # Add new name and catagory to the new catagory data frame
			allNewCatDf.to_csv("tempCatagories.csv", index=False)  # Save a temporary catagories file

			catList.append(inCat)  # append inputed catagory to the catList
			smList.append(inName)  # append inputed name to the smList

	accountDF["name"] = smList  # Add "name" column with data to the accountDF
	accountDF["catagory"] = catList  # add "catagory" column with data to accountDF

	return accountDF.iloc[::-1].reset_index(drop=True), catagoryDF.sort_values("name")  # return accountDF reversed (chronological), return catagoryDF with values sorted alphabetically by "name" column


#################################
#
# Function to loop the generation of pie charts
#
# accountDF: pandas dataframe ~ contains transaction information
# fileDirec: string ~ location of where to save generated figures
#
#################################
def genPieCharts(accountDF, fileDirec=None):
	print("Now generating multiple pie charts...\n")

	percentOfIncome(accountDF, fileDirec)  # run percentOfIncome function

	catNameDf = accountDF.groupby(["catagory", "name"]).Transaction.sum().reset_index()  # Group accountDF by the catagory then by the name, sum the "transaction" column
	for ctgry, catNameDf in catNameDf.groupby("catagory"):  # Iterate though catNameDf by catagory
		graphDF = pd.concat([catNameDf["name"], catNameDf["Transaction"].abs()], axis=1, keys=["name", "Transaction"])  # Pull "name" and "Transaction" column from catNameDf to new DF
		graphDF = graphDF.set_index("name").sort_values(by="Transaction", ascending=False)  # Set index to contentes of "name" DF

		if fileDirec is not None:
			filePath = fileDirec + "\\" + "pie" + ctgry + ".png"
		else:
			filePath = None

		genPieChart(ctgry, graphDF, "Transaction", filePath)  # Generate pie chart using "Transaction" column as data


#################################
#
# Generate Pie Chart
# Used in function above
#
# figName: string ~ a unique string to call the figure
# accountDF: pandas dataframe ~ contains transaction information
# graphCol: string ~ of the DF "accountDF", this string indicates which column to make the chart from
# fileName: string ~ location of where to save generated figure
#
#################################
def genPieChart(figName, accountDF, graphCol, fileName=None):
	print("Generating \"%s\" pie chart..." % (figName))
	plt.style.use('bmh')
	fig = plt.figure(figName, figsize=(10, 10))  # Create catagory figure
	axs = fig.add_subplot(111)  # Create catagory axis
	axs.pie(accountDF[graphCol], labels=list(accountDF.index.values), autopct='%1.1f%%', startangle=90, counterclock=False, rotatelabels=True)  # Generate Pie Chart
	axs.axis("equal")  # Set equal aspect ratio of graph
	axs.legend()  # Add legend
	fig.suptitle(figName, fontsize=16)  # Set title
	fig.tight_layout(pad=6)

	if fileName is None:
		plt.show()  # Show Graph
	else:
		fig.savefig(fileName, dpi=100)  # Safe graph as file

	plt.close(fig)  # Wipe graph from memory


#################################
#
# Generate text log of expenses
# Used in "genPieCharts"
#
# accountDF: pandas dataframe ~ contains transaction information
# fileDirec: string ~ location of where to save generated text file
#
#################################
def percentOfIncome(accountDF, fileDirec=None):

	if fileDirec is not None:
		fileName = fileDirec + "\\pieTotal.png"
		logFilePath = fileDirec.rsplit("\\", 1)[0] + "\\log.txt"
		logFile = open(logFilePath, "w")
		logFile = open(logFilePath, "a")
	else:
		fileName = None
		logFile = sys.stderr

	catSumDF = accountDF.groupby("catagory").Transaction.sum().reset_index()  # Group dataframe by contents of "catagory" column, sum "Transaction" column contents
	catSumDF["abs"] = catSumDF.Transaction.abs()  # Create absolute value of "Transaction" column
	catSumDF = catSumDF.set_index("catagory")  # Set the index to the contents of "catagory" column
	catSumDF = catSumDF.sort_values(by="abs", ascending=False)  # Sort dataframe by contents of "abs" column

	payment = catSumDF["Transaction"]  # Pull "transaction" column
	income = payment["income"]  # Pull data tied to index "income" of "transaction" column
	savings = round(catSumDF["Transaction"].sum(), 2)  # Sum "transaction" column and round to 2 decimal places

	savingsDF = pd.DataFrame([savings], columns=["abs"], index=["savings"])  # create DF with stored savings variable
	percentDF = catSumDF.append(savingsDF)  # append savings DF to catSumDF and create percentDF
	percentDF = percentDF.drop(["income"])  # drop "income" row from the percentDF
	percentDF["Percent"] = percentDF["abs"].apply(lambda x: (x / income), 1)  # create "percent" column from the "abs" column
	percentDF = percentDF.sort_values(by="Percent", ascending=False)  # Sort percentDF by the "percent" column

	if savings < 0:  # If more was spent than earned
		print(percentDF, file=logFile)  # print percentDF
		print("Income: %s" % (income), file=logFile)  # print income
		print("Deficent from account: %s\n" % (savings), file=logFile)  # print balance
		genPieChart("Total Transactions", catSumDF, "abs", fileName)  # generate piechart

	else:
		print(percentDF, file=logFile)  # print percentDF
		print("Income: %s" % (income), file=logFile)  # print income
		print("Amount added to savings: %s\n" % (savings), file=logFile)  # print balance
		genPieChart("Percent of Income", percentDF, "Percent", fileName)  # generate pie chart

	nameDF = accountDF.groupby("name").Transaction.sum().reset_index()
	nameDF["abs"] = nameDF.Transaction.abs()
	savingsDF = pd.DataFrame([["Savings", savings]], columns=["name", "abs"])  # create DF with stored savings variable
	nameDF = nameDF.append(savingsDF)
	nameDF["Percent"] = nameDF["abs"].apply(lambda x: (x / income), 1)  # create "percent" column from the "abs" column
	nameDF = nameDF.sort_values(by="abs", ascending=False)
	print(nameDF.reset_index(drop=True).to_string(), file=logFile)
	logFile.close()


#################################
#
# Function to loop the generation of line graphs
#
# accountDF: pandas dataframe ~ contains transaction information
# groupCol: string ~ of the DF "accountDF", this string indicates which column to make the chart from
# directory: string ~ location where to save generate figures
#
#################################
def saveLineGraphs(accountDF, groupCol, directory):
	print("Now generating multiple line graphs...\n")
	nameList = accountDF[groupCol].unique()  # Create list of all of the names present within the sub-dataframe
	for name in nameList:  # Iterate name list
		nameDF = accountDF[accountDF[groupCol].str.match(name)]  # Create sub-dataframe containing only name data

		filePath = directory + "\\" + "line" + name + ".png"

		genLineChart(name, accountDF.copy(), filePath, nameDF.copy())


#################################
#
# Generate line chart
# Used above and overview
#
# name: string ~ unique identifier of the generated graph
# accountDF: pandas dataframe ~ contains transaction information
# fileName: string ~ location where to save the generate figure
# groupCol: string ~ of the DF "accountDF", this string indicates which column to make the chart from
# subDF: pandas dataframe ~ additional data to graph on top of accountDF
# weekSpendRate: bool ~ True to see additional axis of expense rate
#
#################################
def genLineChart(name, accountDF, fileName=None, subDF=None, weekSpendRate=False):
	accountDF.loc[:, "Date"] = pd.to_datetime(accountDF.loc[:, "Date"])  # Convert the "Date" column to datetime

	accountSeries = pd.Series(list(accountDF["Transaction"]), index=list(pd.to_datetime(accountDF["Date"])))
	dailySumSeries = accountSeries.resample('1D').sum()
	weeklySumSeries = accountSeries.resample('1W', label="right").sum()  # Collapse data to the mean value spent within a week

	print("Generating \"%s\" line graph..." % (name))
	stdDev = accountDF["Transaction"].std()
	average = accountDF["Transaction"].mean()
	accountDF["StandardDeviations"] = np.absolute((accountDF["Transaction"] - average) / stdDev)

	outlierDF = accountDF[accountDF["StandardDeviations"] > 7]

	if weekSpendRate:
		axNo = 311
	else:
		axNo = 211

	plt.style.use('bmh')
	fig = plt.figure(name, figsize=(21, 9))
	ax1 = fig.add_subplot(axNo)
	ax2 = fig.add_subplot(axNo + 1, sharex=ax1)

	ax1.plot(accountDF["Date"], accountDF["Transaction"], color="dodgerblue", label="Full Account", linewidth=0.65, marker=".")

	# Graph the Outlier Datapoints
	for index, row in outlierDF.iterrows():
		ax1.scatter(row["Date"], row["Transaction"], color="k", marker="x")
		ax1.text(row["Date"], row["Transaction"], row["name"], size=8)

	# If a subDF is passed, Green Trace to indicate specific transactions. Otherwise generate typical graph
	if isinstance(subDF, pd.DataFrame):
		subDF["Date"] = pd.to_datetime(subDF["Date"])
		ax1.plot(subDF["Date"], subDF["Transaction"], color="mediumseagreen", label=name + " Transactions", linewidth=0.65, marker=".")
		ax2.plot(subDF["Date"], subDF["Transaction"].cumsum(), color="darkviolet", label=name + " Balance", linewidth=0.65, marker=".")
	else:
		ax2.plot(weeklySumSeries.index, weeklySumSeries.cumsum(), color="goldenrod", label="Week Ave.", linewidth=1.5)
		ax2.plot(accountDF["Date"], accountDF["Transaction"].cumsum(), color="darkviolet", label="Balance", linewidth=0.65)

	if weekSpendRate:

		# Potentially add cubic interpolation
		ax3 = fig.add_subplot(axNo + 2, sharex=ax1)
		ax3.plot(weeklySumSeries.index, weeklySumSeries, color="red", alpha=0.2, label="Weekly Rate", linewidth=1.5)
		ax3.plot(weeklySumSeries.index, weeklySumSeries.rolling(window=8).mean(), color="red", label="Weekly Rate 8 Week Ave.", linewidth=1.5)
		ax3.legend()
		ax3.set_title("Weekly Spend Rate")

	ax1.legend()
	ax1.set_title("Transaction vs Time")
	ax2.legend()
	ax2.set_title("Balance vs Time")

	fig.suptitle(name, fontsize=16)
	fig.tight_layout(pad=4)

	if fileName is None:
		plt.show()
	else:
		fig.savefig(fileName, dpi=100)

	plt.close(fig)


#################################
#
# Generate a stacked bar graph
#
# figName: string ~ unique identifier of the generated graph
# accountDF: pandas dataframe ~ contains transaction information
# groupCol: string ~ of the DF "accountDF", this string indicates which column to make the chart from
# fileName: string ~ location where to save the generate figure
#
#################################
def genStackedBar(figName, accountDF, groupCol, fileName=None):
	print("Generating \"%s\" stacked bar graph..." % (figName))
	groupDF = accountDF.groupby(groupCol).Transaction.apply(list).reset_index()  # Group accountDF by contents of column variable "groupCol", the contents of column "Transaction" stored in list
	columnsDF = pd.DataFrame(groupDF.Transaction.tolist(), index=groupDF[groupCol]).abs()  # Create dataframe with list data is separated into columns, index set "groupCol" found groups, absolute value data
	a = columnsDF.assign(tmp=columnsDF.sum(axis=1)).sort_values('tmp', ascending=False).drop('tmp', 1)  # Sort rows of DF by the row's sum

	plt.style.use('bmh')
	ax = a.plot(kind='bar', stacked=True, figsize=(18, 9), legend=False)  # Generate a stacked bar graph

	annotateDict = {}

	for p in ax.patches:  # Iterate though the multiple bars in graph
		if 0.0 != round(p.get_height(), 0):  # if hight is not zero

			if p.get_x() in annotateDict.keys():  # if p.get_x() is present in keys of "annotateDict"...
				annotateDict[p.get_x()].append(round(p.get_height(), 1))  # append bar height to list with matching dictionary key
			else:
				annotateDict[p.get_x()] = []  # create list with newly found key
				annotateDict[p.get_x()].append(round(p.get_height(), 1))  # append bar height to list with matching dictionary key

	for x in annotateDict.keys():  # Iterate though keys
		cumSum = 0  # Reset cumulative sum
		if len(annotateDict[x]) > 1:  # if the length of the list is greater than 1 (more than one bar stacked)
			for height in annotateDict[x]:  # Iterate though the heights
				cumSum += height  # Add hight to the cumulative sum
				ax.annotate(str(height), (x, cumSum), verticalalignment="top")  # Annotate the height at coordinates (x, cumSum)
		else:
			cumSum = annotateDict[x][0]  # set cumSum to contents of annotateDict[x][0]

		ax.annotate(str(round(cumSum, 2)), (x, cumSum), fontsize=12, weight='bold')  # Annotate the final height of the bar

	plt.suptitle(figName, fontsize=16)  # Set title
	plt.tight_layout(pad=4)
	ax.set_yscale("log")  # Set y-axis scale to logarithmic
	plt.xlabel("")  # remove x-axis label
	plt.ylabel("Transaction Total (USD)")  # Set y-axis label

	if fileName is None:
		plt.show()  # Show Graph
	else:
		plt.savefig(fileName, dpi=100)  # Safe graph to file

	plt.close()  # Erase graph from memory


#################################
#
# Generate a simple line graph
# accountDF: pandas dataframe ~ contains transaction information
# graphName: string ~ unique identifier of the generated graph
# groupCol: string ~ of the DF "accountDF", this string indicates which column to make the chart from
# fileName: string ~ location where to save the generate figure
#
#################################
def tLineGraph(accountDF, graphName, groupCol, fileName=None):

	plt.style.use('bmh')
	fig = plt.figure(graphName, figsize=(21, 9))
	ax1 = fig.add_subplot(211)
	ax2 = fig.add_subplot(212, sharex=ax1)
	ax1.set_title("Transaction vs Time")
	ax2.set_title("Balance vs Time")

	nameList = accountDF[groupCol].unique()  # Create list of all of the names present within the sub-dataframe
	for name in nameList:  # Iterate name list
		nameDF = accountDF[accountDF[groupCol].str.match(name)]  # Create sub-dataframe containing only name data

		ax1.plot(pd.to_datetime(nameDF["Date"]), nameDF["Transaction"], label=name, linewidth=0.65, marker=".")
		ax2.plot(pd.to_datetime(nameDF["Date"]), nameDF.cumsum()["Transaction"], label=name, linewidth=0.65, marker=".")

	ax1.legend()
	ax2.legend()

	fig.suptitle(graphName, fontsize=16)
	fig.tight_layout(pad=4)

	if fileName is None:
		plt.show()
	else:
		fig.savefig(fileName, dpi=100)

	plt.close(fig)


#################################
#
# Generate stacked line graphs that are interactable
# Helpful when comparing months or years
# Overview use
#
# name: string ~ unique identifier of the generated graph
# lgDF: pandas dataframe ~ contains transaction information
# separation: string ~ how the user would like to stack the data
#
#################################
def stackGraphs(name, lgDF, separation="year"):
	lgDF["day"] = pd.DatetimeIndex(lgDF["Date"]).day

	if separation == "year":
		lgDF["findCol"] = pd.DatetimeIndex(lgDF["Date"]).year
		lgDF["month"] = pd.DatetimeIndex(lgDF["Date"]).month
		lgDF["year"] = 2008
		lgDF["dateTime"] = pd.to_datetime(lgDF[["year", "month", "day"]])
		lgDF.set_index("dateTime", inplace=True)

	elif separation == "month":
		lgDF["findCol"] = pd.DatetimeIndex(lgDF["Date"]).year.astype(str) + " - " + pd.DatetimeIndex(lgDF["Date"]).month.astype(str)
		lgDF["month"] = 1
		lgDF["year"] = 2008
		lgDF["dateTime"] = pd.to_datetime(lgDF[["year", "month", "day"]])
		lgDF.set_index("dateTime", inplace=True)

	sepList = list(lgDF["findCol"].drop_duplicates())

	fig, axes = plt.subplots(nrows=3, sharex=True)
	fig.set_size_inches(21, 9)

	for idx, sep in enumerate(sepList):
		dfToLine(lgDF.loc[(lgDF.findCol == sep)], idx, str(sep), axes)

	if len(sepList) > 5:
		sizeFont = "xx-small"
		ptTolerance = 2
	else:
		sizeFont = None
		ptTolerance = 8

	legDict = {}
	lineDict = {}
	for idx, ax in enumerate(fig.axes):
		legDict[idx] = ax.legend(bbox_to_anchor=(1, 1), loc="upper left", fancybox=True, shadow=True, fontsize=sizeFont)

		for legline, origline in zip(legDict[idx].get_lines(), ax.lines):
			legline.set_picker(ptTolerance)  # pt tolerance
			legDict[legline] = origline
			origline.set_visible(True)
			legline.set_alpha(1)

			def onpick(event):
				# On pick event, fint the orig line corresponding to the legend proxy line, and toggle the visibility
				legline = event.artist
				origline = legDict[legline]
				vis = not origline.get_visible()
				origline.set_visible(vis)

				# Change the alpha on the line in the legend so that we can see what lines have been toggled
				if vis:
					legline.set_alpha(1)
				else:
					legline.set_alpha(0.2)
				fig.canvas.draw()

	fig.canvas.mpl_connect("pick_event", onpick)
	fig.tight_layout(pad=4)
	fig.suptitle(name, fontsize=16)
	plt.show()


#################################
#
# Add line to multiple axes
# Used in the function above
#
# pdDataFrame: pandas dataframe ~ contains transaction information
# color: int ~ choose the index from which color the graphed line will be
# labelID: string ~ identifier for the line to be graphed
# axs: list ~ collection of axis which the line will be applied to
#
#################################
def dfToLine(pdDataFrame, color, labelId, axs):
	colorOpt = ['#e6194B', '#3cb44b', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#000000']

	accountSeries = pd.Series(list(pdDataFrame["Transaction"]), index=pdDataFrame.index)
	weeklySumSeries = accountSeries.resample('1W', label="right").sum()  # Collapse data to the mean value spent within a week

	axs[0].plot(pdDataFrame.index, pdDataFrame["Transaction"], color=colorOpt[color % len(colorOpt)], label=labelId + "Charges")

	axs[1].plot(pdDataFrame.index, pdDataFrame["Transaction"].cumsum(), color=colorOpt[color % len(colorOpt)], alpha=0.4, label=labelId + "Balance")
	axs[1].plot(weeklySumSeries.index, weeklySumSeries.cumsum(), color=colorOpt[color % len(colorOpt)], label=labelId + "Week Ave.")

	axs[2].plot(weeklySumSeries.index, weeklySumSeries, color=colorOpt[color % len(colorOpt)], alpha=0.4, label=labelId + "Weekly Rate")
	axs[2].plot(weeklySumSeries.index, weeklySumSeries.rolling(window=8).mean(), color=colorOpt[color % len(colorOpt)], label=labelId + "Weekly Rate 8 Week Ave.")


#################################
#
# Old code to slice a dataframe
# Used for 2019, 2020, 2021, 2022
#
#################################
def sliceDfCreateDir(accountDF, sliceList=None, createDir=True):
	if sliceList == None:
		incomeRentDF = accountDF.loc[np.logical_or(accountDF['name'] == "Salary", accountDF['name'] == "Rent")]
		incomeRentDF.to_csv("extractIncomeRent.csv")
		print(incomeRentDF)

		while True:

			sliceList = [0, 0]
			sliceList[0] = int(input("Low Index:"))  # Prompt user for filter string
			sliceList[1] = int(input("High Index:"))  # Prompt user for catagory string
			print(accountDF[sliceList[0]:sliceList[1]])

			if input("This dataframe should start with a salary increase or rent payment and not end with a salary or rent payment\nIs this correct? (enter yes):").lower() == "yes":
				break

	accountDF = accountDF[sliceList[0]:sliceList[1]]

	if createDir:
		dateDF = accountDF["Date"]
		lowDate = datetime.strptime(dateDF[sliceList[0]], '%m/%d/%Y').strftime('%Y-%m-%d')
		higDate = datetime.strptime(dateDF[sliceList[1] - 1], '%m/%d/%Y').strftime('%Y-%m-%d')

		savePath = "D:\\Users\\Ryzen\\PythonScripts\\analyzeBank\\%s_%s" % (lowDate, higDate)
		grphPath = savePath + "\\graphs"

		try:
			os.makedirs(grphPath)
		except OSError:
			print("Creation of the directory %s failed" % grphPath)
		else:
			print("Successfully created the directory %s" % grphPath)

		return savePath, grphPath, accountDF

	else:
		return accountDF
