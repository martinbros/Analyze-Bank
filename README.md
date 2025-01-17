# Analyze Bank Accounts

Quick Look: Program designed to generate line graphs, pie charts, categorize expenses, and other tools to better visualize expenses

## Operation: genReport.py

The script is executed using 1 or 2 arguments as outlined below:
```
-p string : Pass the path of an already categorized transaction CSV file for reprocessing and generation of graphs and logs

-y int: The year which the script parse down the transaction list for generation of a report

-q int: Only accepts the value 1-4, the quarter which the script will parse down the transaction list for generation of a report
```

The arguments -p and -y are used together to generate a quarterly report. These arguments are not used in any combination with -p.

**Order of Operations: Generate a Quarterly Report**

1. Before executing the script, make sure that the following constants are correct:
- "categoryPath" : The path to a CSV file containing filter strings in a column "name", category strings in column "cat", and user input IDs in column "ID"
- At least one dictionary with the following keys and info:
	- "path" : Path to a CSV file with list of transactions from a bank account
	- "ID" : A generic string to identify which account a transaction originates from
	- "regexStrings" : A list of regex strings that match to certain transactions that one would wish to remove from a transaction list
		- For example: I use this to remove payments from my checking account to a credit card as having both the payment and the individual transactions paints an inaccurate balance
- Function "removeRows2" in "func.py" properly ingests the transaction CSV files
2. Run "genReport.py" with the appropriate -y and -q parameters
3. The script will then prompt the user to create a filter string for the displayed transaction, this is used to identify a this transaction and other similar transactions
4. The script will then prompt the user to create a category for the displayed transaction
5. The script will repeat steps 3 and 4 until all transactions are categorized
6. The script will then generate line graphs, pie charts, expense logs, and stack bar graphs based on the transaction data within a folder following the naming structure "year Q# working"
7. Report generation is now complete

**Order of Operations: Re-generate Quarterly Report**

If the user decides to manually edit "transactionsCatagorized.csv" and wishes to re-run the generation of the report, this can be done by passing the path to "transactionsCatagorized.csv" to the -p argument of "genReport.py" and a new report will be generated.

## Operation: GraphReports.py

This is a general playground for slicing and dicing the data in a quarterly report. 

## More Helpful Info

- Traces of "stackGraphs" can be turned on/off by clicking on the trace's color in the legend
- Adding an entry to the "ID" column of "masterCatagories.csv" will use this value instead of the filtering string value which can make something more human readable.