import pandas as pd
from func import *
from datetime import datetime
import pretty_errors


catagoryPath = "masterCatagories.csv"

# Import accounts, remove rows relating to payments
autoDF, rmvAutoDF = removeRows("wfAutographAugDec.csv", "Autograph", ["ONLINE PAYMENT THANK YOU"])  # Removing payment to card
platDF, rmvPlatDF = removeRows("wfPlatinumAugDec.csv", "Platinum", ["ONLINE PAYMENT THANK YOU"])  # Removing payment to card
chckDF, rmvChckDF = removeRows("wfCheckingAugDec.csv", "Checking", ["ONLINE TRANSFER REF #[A-Z0-9]* TO WELLS FARGO AUTOGRAPH", "ONLINE TRANSFER REF #[A-Z0-9]* TO PLATINUM"])  # Payments to CC came from this account

# Combine all accounts
ckAccount = pd.concat([chckDF, platDF, autoDF])
rmvDF = pd.concat([rmvChckDF, rmvPlatDF, rmvAutoDF])

# Catagorize transactions
accountDF, newCatDf = catagorizeTransactions(ckAccount, catagoryPath)
newCatDf.to_csv("masterCatagories.csv", index=False)

# Create the directory in which everything will be saved, also slice down the transcations by date
saveP, graphP, catCkAcct = sliceDfCreateDir2(accountDF, 2024, 4)

# Create the charts/graphs for the quarterly report
saveLineGraphs(catCkAcct, "catagory", graphP)
genPieCharts(catCkAcct, graphP)
genStackedBar("Transactions Grouped by Name", catCkAcct, "name", graphP + "\\barName.png")
genStackedBar("Transactions Grouped by Catagory", catCkAcct, "catagory", graphP + "\\barCatagory.png")
genLineChart("Checking Account Timeline", catCkAcct.copy(), graphP + "\\lineChecking.png")

# Save the generated tables
catCkAcct.to_csv(saveP + "\\transactionsCatagorized.csv", index=False)
rmvDF.to_csv(saveP + "\\removedTransactions.csv", index=False)
newCatDf.to_csv(saveP + "\\updatedCatagories.csv", index=False)