import pandas as pd
from func import *
from datetime import datetime
import pretty_errors


catagoryPath = "bankResources/masterCatagories.csv"

autoDF, rmvAutoDF = removeRows("bankResources/wfAutographJanSept.csv", "Autograph", ["ONLINE PAYMENT THANK YOU"])  # Removing payment to card
platDF, rmvPlatDF = removeRows("bankResources/wfPlatinumJanSept.csv", "Platinum", ["ONLINE PAYMENT THANK YOU"])  # Removing payment to card
chckDF, rmvChckDF = removeRows("bankResources/wfCheckingJanSept.csv", "Checking", ["ONLINE TRANSFER REF #[A-Z0-9]* TO WELLS FARGO AUTOGRAPH", "ONLINE TRANSFER REF #[A-Z0-9]* TO PLATINUM"])  # Payments to CC came from this account

ckAccount = pd.concat([chckDF, platDF, autoDF])
rmvDF = pd.concat([rmvChckDF, rmvPlatDF, rmvAutoDF])

accountDF, newCatDf = catagorizeTransactions(ckAccount, catagoryPath)
newCatDf.to_csv("masterCatagories.csv", index=False)

# Use the following lines below to generate a quarterly report
saveP, graphP, catCkAcct = sliceDfCreateDir2(accountDF, 2024, 1)

catCkAcct.to_csv(saveP + "\\transactionsCatagorized.csv", index=False)
rmvDF.to_csv(saveP + "\\removedTransactions.csv", index=False)
newCatDf.to_csv(saveP + "\\updatedCatagories.csv", index=False)

saveLineGraphs(catCkAcct, "catagory", graphP)
genPieCharts(catCkAcct, graphP)
genStackedBar("Transactions Grouped by Name", catCkAcct, "name", graphP + "\\barName.png")
genStackedBar("Transactions Grouped by Catagory", catCkAcct, "catagory", graphP + "\\barCatagory.png")
genLineChart("Checking Account Timeline", catCkAcct, graphP + "\\lineChecking.png")
