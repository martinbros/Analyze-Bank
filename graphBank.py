import pandas as pd
from func import *
from datetime import datetime

bankInfo = "Checking1.csv"
catagoryPath = "masterCatagories.csv"

ckAccount = pd.read_csv(bankInfo, usecols=[0, 1, 4], names=["Date", "Transaction", "Info"])  # Import checking account CSV for processing
accountDF, newCatDf = catagorizeTransactions(ckAccount, catagoryPath)
newCatDf.to_csv("masterCatagories.csv", index=False)


# Use the following lines below to generate a quarterly report
saveP, graphP, catCkAcct = sliceDfCreateDir2(accountDF, 2023, 2)
catCkAcct.to_csv(saveP + "\\transactionsCatagorized.csv", index=False)
newCatDf.to_csv(saveP + "\\updatedCatagories.csv", index=False)
saveLineGraphs(catCkAcct, "catagory", graphP)
genPieCharts(catCkAcct, graphP)
genStackedBar("Transactions Grouped by Name", catCkAcct, "name", graphP + "\\barName.png")
genStackedBar("Transactions Grouped by Catagory", catCkAcct, "catagory", graphP + "\\barCatagory.png")
genLineChart("Checking Account Timeline", catCkAcct, graphP + "\\lineChecking.png")
