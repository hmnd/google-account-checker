import pandas as pd
import sys
import os
from tqdm import tqdm
import requests
from fake_useragent import UserAgent
from time import sleep

ua = UserAgent()


error_text = "Couldn't find your Google Account"

req_headers = {
    "Host": "accounts.google.com",
    "Accept": "*/*",
    "Accept-Language": "en-US,en-CA;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "X-Same-Domain": "1",
    "Google-Accounts-XSRF": "1",
    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    "DNT": "1",
    "Connection": "keep-alive",
    "Referer": "https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "Trailers",
}

req_url = "https://accounts.google.com/_/signin/sl/lookup?hl=en&_reqid=27491&rt=j"


def process_household(df, cookies):
    for email_name in df.index:
        if (
            isinstance(df[email_name], str)
            and "Type" not in email_name
            and "Email" in email_name
        ):
            payload = {"f.req": '["' + df[email_name] + '"]'}
            req_headers["User-Agent"] = ua.random
            resp = requests.post(
                req_url, headers=req_headers, data=payload, cookies=cookies
            )
            if df[email_name] in resp.text:
                df[
                    "{}{} Type".format(
                        email_name, "1" if not email_name[-1].isdigit() else ""
                    ).replace(" ", "_")
                ] = "Google"
            sleep(3)
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
    print("Itterating through records...")
    session = requests.Session()
    session.get(
        "https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin"
    )
    cookies = session.cookies.get_dict()
    emails_df.progress_apply(process_household, args=(cookies,), axis=1)
    print("Exporting results to CSV...")
    emails_df.to_csv(file_out, sep="\t", index=False)
    print("All done! View file at {}".format(file_out))


if __name__ == "__main__":
    main()
