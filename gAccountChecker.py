import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import sys
import os
from tqdm import tqdm


def process_household(df, browser):
    for email_name in df.index:
        if (
            isinstance(df[email_name], str)
            and "Type" not in email_name
            and "Email" in email_name
        ):
            browser.get("https://accounts.google.com/signin/recovery/lookup")
            email = browser.find_element_by_xpath('//*[@id="identifier"]')
            next_button = browser.find_element_by_xpath('//*[@id="next"]')
            email.send_keys(df[email_name])
            next_button.click()
            try:
                browser.find_element_by_xpath('//*[@id="identifierError"]')
            except NoSuchElementException:
                df[
                    "{}{} Type".format(
                        email_name, "1" if not email_name[-1].isdigit() else ""
                    ).replace(" ", "_")
                ] = "Google"
    return df


def main():
    in_file = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        pd.read_csv(in_file, delimiter=",", header=0, dtype=str)
        print("Using passed file ({}).".format(os.path.basename(in_file)))
    except Exception as FileNotFoundError:
        file_not_found_error = "Please enter a valid file path."
        print(file_not_found_error)
        while True:
            in_file = input("Enter file path to PCR export: ").replace('"', "")
            try:
                pd.read_csv(in_file, delimiter=",", header=0, dtype=str)
                print("Using inputted file.\nProcessing...")
                break
            except FileNotFoundError:
                print(file_not_found_error)
                continue
            except KeyboardInterrupt:
                sys.exit()
    print("Processing...")
    tqdm.pandas(desc="Processing Households")
    file_out = os.path.join(
        os.path.dirname(os.path.realpath(in_file)),
        os.path.splitext(in_file)[0] + " - Google PCR Import.txt",
    )
    in_file = pd.read_csv(in_file, delimiter=",", dtype=str)
    emails_df = in_file.copy()
    emails_df.rename(columns={"Household Id": "lookup_household_id"}, inplace=True)
    print("Launching Chrome...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(chrome_options=chrome_options)
    if int(browser.capabilities["version"].split(".")[0]) >= 60:
        print("You are running Chrome v60+. Chrome is therefore running headless.")
    print("Itterating through records...")
    emails_df.progress_apply(process_household, args=(browser,), axis=1)
    print("Exporting results to CSV...")
    emails_df.to_csv(file_out, sep="\t", index=False)
    print("Closing Chrome...")
    browser.quit()
    print("All done! View file at {}".format(file_out))


if __name__ == "__main__":
    main()
