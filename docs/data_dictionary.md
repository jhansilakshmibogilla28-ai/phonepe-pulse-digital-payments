# PhonePe Pulse Data Dictionary

## aggregated_transactions.csv

| Column | Description |
|---|---|
| year | Calendar year of the transaction data |
| quarter | Quarter number (1–4) |
| period | Year-quarter period label |
| category | Transaction category |
| transaction_count | Total number of transactions |
| transaction_amount | Total transaction value |

## state_transactions.csv

| Column | Description |
|---|---|
| year | Calendar year |
| quarter | Quarter number |
| state | Indian state or union territory |
| transaction_count | Total transactions for the state |
| transaction_amount | Total transaction value for the state |

## users.csv

| Column | Description |
|---|---|
| year | Calendar year |
| quarter | Quarter number |
| registered_count | Number of registered users |

## merchants.csv

| Column | Description |
|---|---|
| year | Calendar year |
| quarter | Quarter number |
| registered_count | Number of registered merchants |

## Data Notes

- Source: PhonePe Pulse public dataset
- Transaction values are represented in the source dataset's monetary units.
- Quarterly aggregation is used for trend analysis.
- Raw source data is intentionally excluded from the repository.
- Processed datasets are generated through the Python data pipeline.
