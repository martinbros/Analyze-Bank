import pandas as pd
from func import *
from datetime import datetime
import pretty_errors

bankInfo = "Checking1.csv"
catagoryPath = "masterCatagories.csv"

accounts = {"wfAutographJanSept.csv": "ONLINE TRANSFER REF #[A-Z0-9]* TO WELLS FARGO AUTOGRAPH",
			"wfPlatinumJanSept.csv": "ONLINE TRANSFER REF #[A-Z0-9]* TO PLATINUM"}

#ckAccount = importAccounts("wfCheckingJanSept.csv", accounts)
#ckAccount = pd.read_csv(bankInfo, usecols=[0, 1, 4], names=["Date", "Transaction", "Info"])  # Import checking account CSV for processing

autoDF = removeRows("wfAutographJanSept.csv", ["ONLINE PAYMENT THANK YOU"])
platDF = removeRows("wfPlatinumJanSept.csv", ["ONLINE PAYMENT THANK YOU"])
chckDF = removeRows("wfCheckingJanSept.csv", ["ONLINE TRANSFER REF #[A-Z0-9]* TO WELLS FARGO AUTOGRAPH", "ONLINE TRANSFER REF #[A-Z0-9]* TO PLATINUM"])
# Need to save info of what was removed
ckAccount = pd.concat([chckDF, platDF, autoDF])

print(ckAccount)

accountDF, newCatDf = catagorizeTransactions(ckAccount, catagoryPath)
newCatDf.to_csv("masterCatagories.csv", index=False)


# Use the following lines below to generate a quarterly report
saveP, graphP, catCkAcct = sliceDfCreateDir2(accountDF, 2024, 1)
catCkAcct.to_csv(saveP + "\\transactionsCatagorized.csv", index=False)
newCatDf.to_csv(saveP + "\\updatedCatagories.csv", index=False)
saveLineGraphs(catCkAcct, "catagory", graphP)
genPieCharts(catCkAcct, graphP)
genStackedBar("Transactions Grouped by Name", catCkAcct, "name", graphP + "\\barName.png")
genStackedBar("Transactions Grouped by Catagory", catCkAcct, "catagory", graphP + "\\barCatagory.png")
genLineChart("Checking Account Timeline", catCkAcct, graphP + "\\lineChecking.png")
