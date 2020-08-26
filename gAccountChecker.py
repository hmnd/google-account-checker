import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
import sys
import os
from tqdm import tqdm
from time import sleep


def process_household(df, browser: Chrome):
    for email_name in df.index:
        if (
            isinstance(df[email_name], str)
            and "Type" not in email_name
            and "Email" in email_name
        ):
            browser.get(
                "https://accounts.google.com/signin/v2/identifier?hl=en&continue=https%3A%2F%2Fwww.google.com%2F&flowName=GlifWebSignIn&flowEntry=AddSession"
            )
            email = browser.find_element_by_xpath('//*[@id="identifierId"]')
            next_button = browser.find_element_by_xpath(
                '//*[@id="identifierNext"]/div/button'
            )
            email.send_keys(df[email_name])
            next_button.click()
            sleep(2)
            try:
                browser.get_screenshot_as_file("screenshot.png")
                browser.find_element_by_xpath(
                    '//form//div[contains(text(), "Couldn\'t find your Google Account")]'
                )
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
    browser = webdriver.Chrome(
        ChromeDriverManager().install(), options=chrome_options
    )
    print("Itterating through records...")
    out: pd.DataFrame = emails_df.progress_apply(process_household, args=(browser,), axis=1)
    print("Exporting results to CSV...")
    out.to_csv(file_out, sep="\t", index=False)
    print("Closing Chrome...")
    browser.quit()
    print("All done! View file at {}".format(file_out))


if __name__ == "__main__":
    main()
