import pandas as pd
from func import *
from datetime import datetime

#bankInfo = "jan20apr20.csv"
#bankInfo = "dec18Jan20.csv"
#bankInfo = "Checking1.csv"
#bankInfo = "jun13jun20.csv"
bankInfo = "Checking1.csv"
catagoryPath = "masterCatagories.csv"



ckAccount = pd.read_csv(bankInfo, usecols = [0, 1, 4], names=["Date", "Transaction", "Info"])  # Import checking account CSV for processing
#genLineChart("Checking Account Timeline", ckAccount.iloc[::-1].reset_index(drop=True))
accountDF, newCatDf = catagorizeTransactions(ckAccount, catagoryPath)
newCatDf.to_csv("masterCatagories.csv", index=False)

#accountDF = sliceDfCreateDir(accountDF, createDir=False)
#genPieCharts(accountDF)
#genStackedBar("Transactions Grouped by Name", accountDF, "name")
#genStackedBar("Transactions Grouped by Catagory", accountDF, "catagory")
#genLineChart("Checking Account Timeline", accountDF)

#Use the following lines below to generate a quarterly report

saveP, graphP, catCkAcct = sliceDfCreateDir(accountDF)
catCkAcct.to_csv(saveP + "\\transactionsCatagorized.csv", index=False)
newCatDf.to_csv(saveP + "\\updatedCatagories.csv", index=False)
saveLineGraphs(catCkAcct, "catagory", graphP)
genPieCharts(catCkAcct, graphP)
genStackedBar("Transactions Grouped by Name", catCkAcct, "name", graphP + "\\barName.png")
genStackedBar("Transactions Grouped by Catagory", catCkAcct, "catagory", graphP + "\\barCatagory.png")
genLineChart("Checking Account Timeline", catCkAcct, graphP + "\\lineChecking.png")



#Saving for some reason
"""
#accountDF = pd.read_csv("2019Catagorized.csv")
idxSlice = [83, 321, 607, 943, 1269, 1492]
for i in range(len(idxSlice)):
	if len(idxSlice[i : i+2]) == 2:
		idx = idxSlice[i : i+2]
		print(idx)
		
		saveP, graphP, catCkAcct = sliceDfCreateDir(accountDF, sliceList=idx)
		catCkAcct.to_csv(saveP + "\\transactionsCatagorized.csv", index=False)
		newCatDf.to_csv(saveP + "\\updatedCatagories.csv", index=False)
		newCatDf.to_csv("masterCatagories.csv", index=False)

		tSaveLineGraphs(catCkAcct, "catagory", graphP)
		genPieCharts(catCkAcct, graphP)
		genStackedBar("Transactions Grouped by Name", catCkAcct, "name", graphP + "\\barName.png")
		genStackedBar("Transactions Grouped by Catagory", catCkAcct, "catagory", graphP + "\\barCatagory.png")
		genLineChart("Checking Account Timeline", catCkAcct, graphP + "\\lineChecking.png")
"""
