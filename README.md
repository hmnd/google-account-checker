# gAccountChecker

> Automated method to test whether a list of emails has associated Google accounts.

## Requirements

- `requests`
- `pandas`
- `tqdm`

## Installation

1. Clone this repository by running `git clone git://github.com/hmnd/gAccountChecker.git`
2. Download the requirements in _requirements.txt_ by running `pip install -r requirements.txt` in the cloned directory

## Usage

### Input

Pass a comma separated file with a "Household Id" column for identification of rows and an infinite number of columns with headers containing "Email". (Note: the names of these columns are used for the names in the outputted file).

### Execution

`python gAccountChecker.py [path to file that is being processed]`

### Output

A file with the same name as the inputted file and `- Google Import.txt` appended to the end is created in the same location as inputted file. This file consists of a "lookup_household_id" column containing the Household IDs from input and a column for each email header with " Type" appended to it. All emails that have Google accounts associated with them will have "Google" in their respective column.
