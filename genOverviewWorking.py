import pandas as pd
from func import *
from datetime import datetime

pathsTest = ["2021Q2_2021-04-06_2021-06-30\\transactionsCatagorized.csv",
			"2021Q3_2021-07-02_2021-10-06\\transactionsCatagorized.csv"]

paths2021 = ["2021Q1_2021-01-04_2021-04-06\\transactionsCatagorized.csv",
			"2021Q2_2021-04-06_2021-06-30\\transactionsCatagorized.csv",
			"2021Q3_2021-07-02_2021-10-06\\transactionsCatagorized.csv",
			"2021Q4_2021-10-06_2022-01-05\\transactionsCatagorized.csv"]

paths2020 = ["2020Q1_2020-01-03_2020-03-25\\transactionsCatagorized.csv",
			"2020Q2_2020-03-27_2020-06-18\\transactionsCatagorized.csv",
			"2020Q3_2020-06-19_2020-09-22\\transactionsCatagorized.csv",
			"2020Q4_2020-09-25_2021-01-04\\transactionsCatagorized.csv"]

paths2019 = ["2019Q1_2019-01-08_2019-04-02\\transactionsCatagorized.csv",
			"2019Q2_2019-04-02_2019-06-27\\transactionsCatagorized.csv",
			"2019Q3_2019-06-28_2019-09-26\\transactionsCatagorized.csv",
			"2019Q4_2019-09-27_2020-01-02\\transactionsCatagorized.csv"]

paths2022 = ["2022Q1_2022-01-05_2022-04-06\\transactionsCatagorized.csv",
			"2022Q2_2022-04-06_2022-06-30\\transactionsCatagorized.csv",
			"2022Q3_2022-07-01_2022-10-05\\transactionsCatagorized.csv",
			"2022Q4_2022-10-05_2022-12-30\\transactionsCatagorized.csv"]

paths2023 = ["2023_Q1\\transactionsCatagorized.csv",
			"2023_Q2\\transactionsCatagorized.csv",
			"2023_Q3\\transactionsCatagorized.csv",
			"2023_Q4\\transactionsCatagorized.csv"]

paths2024 = ["2024_Q1\\transactionsCatagorized.csv",
			"2024_Q2\\transactionsCatagorized.csv",
			"2024_Q3\\transactionsCatagorized.csv"]

allYears = ["2019Q1_2019-01-08_2019-04-02\\transactionsCatagorized.csv",
			"2019Q2_2019-04-02_2019-06-27\\transactionsCatagorized.csv",
			"2019Q3_2019-06-28_2019-09-26\\transactionsCatagorized.csv",
			"2019Q4_2019-09-27_2020-01-02\\transactionsCatagorized.csv",
			"2020Q1_2020-01-03_2020-03-25\\transactionsCatagorized.csv",
			"2020Q2_2020-03-27_2020-06-18\\transactionsCatagorized.csv",
			"2020Q3_2020-06-19_2020-09-22\\transactionsCatagorized.csv",
			"2020Q4_2020-09-25_2021-01-04\\transactionsCatagorized.csv",
			"2021Q1_2021-01-04_2021-04-06\\transactionsCatagorized.csv",
			"2021Q2_2021-04-06_2021-06-30\\transactionsCatagorized.csv",
			"2021Q3_2021-07-02_2021-10-06\\transactionsCatagorized.csv",
			"2021Q4_2021-10-06_2022-01-05\\transactionsCatagorized.csv",
			"2022Q1_2022-01-05_2022-04-06\\transactionsCatagorized.csv",
			"2022Q2_2022-04-06_2022-06-30\\transactionsCatagorized.csv",
			"2022Q3_2022-07-01_2022-10-05\\transactionsCatagorized.csv",
			"2022Q4_2022-10-05_2022-12-30\\transactionsCatagorized.csv",
			"2023_Q1\\transactionsCatagorized.csv",
			"2023_Q2\\transactionsCatagorized.csv",
			"2023_Q3\\transactionsCatagorized.csv",
			"2023_Q4\\transactionsCatagorized.csv",
			"2024_Q1\\transactionsCatagorized.csv",
			"2024_Q2\\transactionsCatagorized.csv",
			"2024_Q3\\transactionsCatagorized.csv",
			"2024_Q4_working\\transactionsCatagorized.csv",]

accountDF = pd.DataFrame()
for path in allYears:
	#accountDF = accountDF.append(pd.read_csv(path), sort=False)
	accountDF = pd.concat([accountDF, pd.read_csv(path)])


#Single figure analysis
#genLineChartV2("Account Balance", accountDF.copy(), weekSpendRate=True)
#genLineChartV2("Checking Account No Income, No Bills", accountDF.loc[(accountDF.Transaction < 0.0) & (accountDF.catagory != "bills")].copy(), weekSpendRate=True)
#genLineChartV2("Food", accountDF.loc[accountDF["catagory"]=="food"].copy(), weekSpendRate=True)

plt.style.use('bmh')
#stackGraphs(accountDF)
stackGraphs("Checking Account, No Reallocation", accountDF.loc[(accountDF.catagory != "reallocation")].copy())
stackGraphs("Checking Account, Income", accountDF.loc[(accountDF.catagory == "income")].copy())
stackGraphs("Checking Account, No Income, No Bills, No Reallocation", accountDF.loc[(accountDF.catagory != "income") & (accountDF.catagory != "bills") & (accountDF.catagory != "reallocation")].copy())
stackGraphs("Food and Drink", accountDF.loc[(accountDF.catagory == "food") | (accountDF.catagory == "drink")].copy())
stackGraphs("Transportation", accountDF.loc[accountDF.catagory == "transportation"].copy())

#genLineChartV2("Chekcing Account, No Income, No Bills, No Reallocation", accountDF.loc[(accountDF.catagory != "income") & (accountDF.catagory != "bills") & (accountDF.catagory != "reallocation")].copy(), weekSpendRate=True)
#genLineChartV2("Food and Drink", accountDF.loc[(accountDF.catagory == "food") | (accountDF.catagory == "drink")].copy(), weekSpendRate=True)

#Generate Figures for catagories with top spending
dataDF = accountDF.groupby(["catagory"]).Transaction.sum().reset_index().sort_values("Transaction") # Group accountDF by the catagory sum the "transaction" column
topNameList = list(dataDF["catagory"])[:10]  #List of top items
for i, name in enumerate(topNameList, start=1):
	dataSample = accountDF[accountDF["catagory"].str.match(name)]
	genLineChart("#%s: %s" % (i, name), dataSample.copy(), weekSpendRate=True)  # Just transaction info

#Generate figures for the locations with the top spending
dataDF = accountDF.groupby(["catagory", "name"]).Transaction.sum().reset_index().sort_values("Transaction") # Group accountDF by the catagory then by the name, sum the "transaction" column
dataDF = dataDF[dataDF["catagory"] != "bills"]  # Remove rows with "bills" in catagory column
dataDF = dataDF[dataDF["catagory"] != "reallocation"]  # Remove rows with "bills" in catagory column
topNameList = list(dataDF["name"])[:10]  #List of top items
print(dataDF)

for i, name in enumerate(topNameList, start=1):
	dataSample = accountDF[accountDF["name"].str.match(name)]
	genLineChart("#%s: %s" % (i, name), dataSample.copy(), weekSpendRate=True)  # Just transaction info
