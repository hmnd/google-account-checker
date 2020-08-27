# gAccountChecker

> Automated method to test whether a list of emails has associated Google accounts.

## Requirements

- `python`: 3.6.1 or newer
- [poetry](https://python-poetry.org/docs/#installation) (recommended, but optional)
- pip modules under [tool.poetry.dependencies] in `pyproject.toml` (if not using poetry)

## Installation

Clone this repository by running `git clone https://github.com/hmnd/gAccountChecker.git`

### Using poetry

In the cloned directory, run `poetry install`

### Manual

In the cloned directory run `pip install -r requirements.txt`

## Preparation

### Input file

Create a comma separated file with a "Household Id" column for identification of rows and an infinite number of columns with headers containing "Email". (Note: the names of these columns are used for the names in the outputted file).

### cookies.txt

1. Install the cookies.txt [Chrome](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) extension (or any other extension that allows exporting a cookies.txt file for a given site)
2. Create or open any Google Doc
3. Download the cookies.txt for your Google Doc using the extension installed in step 1

### Google Doc

Create or open any Google Doc (contents do not matter). Note down its URL for later use.

## Usage

**Note**: Prepend all the below commands with `poetry run` if using poetry.

### Parameters

- `--input-file`: [Correctly formatted](#input-file) CSV file of email addresses
- `--cookies-path`: Path to [cookies.txt](#cookies.txt)
- `--google-doc`: URL or ID of [your Google Doc](#google-doc)
- `--out-format` (optional): Format of output file (TXT or CSV)

`--help`: Display help information

### Example execution

`python main.py --input-file MyInputFile.csv --cookies-path cookies.txt --google-doc 14t3uA22VkbsRyGafeiL4Fb7rJA1k-WQd_tN_RK2ge8`

## Output

A file with the same name as the inputted file, with `- Google Import` appended to the end is created. This file consists of a "lookup_household_id" column containing the Household IDs from input and a column for each email header with " Type" appended to it. All emails that have Google accounts associated with them will have "Google" in their respective Type column.
