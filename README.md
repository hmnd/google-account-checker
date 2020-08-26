# gAccountChecker

> Automated method to test whether a list of emails has associated Google accounts.

## Requirements

- `requests`
- `pandas`
- `tqdm`

## Installation

1. Clone this repository by running `git clone git://github.com/hmnd/gAccountChecker.git`
2. Download the requirements in _requirements.txt_ by running `pip install -r requirements.txt` in the cloned directory

## Parameters

### [input-file]

Pass a comma separated file with a "Household Id" column for identification of rows and an infinite number of columns with headers containing "Email". (Note: the names of these columns are used for the names in the outputted file).

### [google-identifier]

1. In a browser, open the [Google login URL](https://accounts.google.com/signin/v2/identifier?hl=en&continue=https%3A%2F%2Fwww.google.com%2F&flowName=GlifWebSignIn&flowEntry=AddSession).
2. Input any valid Google username.
3. Click Next.
4. Open your browser's console (usually F12 or right-click > Inspect Element).
5. Paste the following code to the console:
   <!--prettier-ignore -->
    ```javascript
   window.botguard.bg(JSON.parse('[' + document.querySelector('[data-initial-setup-data]').dataset.initialSetupData.substr(4))[18], void 0).invoke(null, false, {})
   ```

6. Use the result as the [google identifier] when calling gAccountChecker.py.

### Execution

`python gAccountChecker.py [input-file] [google-identifier]`

### Output

A file with the same name as the inputted file and `- Google Import.txt` appended to the end is created in the same location as inputted file. This file consists of a "lookup_household_id" column containing the Household IDs from input and a column for each email header with " Type" appended to it. All emails that have Google accounts associated with them will have "Google" in their respective column.
