import pandas as pd
import os
from tqdm import tqdm
from time import sleep
import typer
from pathlib import Path
from googleaccountchecker import GoogleAccountChecker


def process_household(df, checker: GoogleAccountChecker):
    for email_name in df.index:
        if type(df[email_name]) is str:
            val = df[email_name].strip()
            if val and "Type" not in email_name and "Email" in email_name:
                is_google = checker.check(df[email_name])
                df[
                    "{}{} Type".format(
                        email_name, "1" if not email_name[-1].isdigit() else ""
                    ).replace(" ", "_")
                ] = ("Google" if is_google else "")
                sleep(3)
    return df


def main(
    input_file: Path = typer.Option(
        None, help="PCR export of email addresses", file_okay=True, dir_okay=False
    ),
    cookies_path: Path = typer.Option(
        None, help="Path to cookies.txt", file_okay=True, dir_okay=False
    ),
    docs_id: str = typer.Option(None, help="ID of any Google Doc in your account"),
):
    print("Processing...")
    checker = GoogleAccountChecker(cookies_path)
    checker.setup(docs_id)
    tqdm.pandas(desc="Processing Households")
    file_out = os.path.join(
        os.path.dirname(os.path.realpath(input_file)),
        os.path.splitext(input_file)[0] + " - Google PCR Import.txt",
    )
    emails_df = pd.read_csv(input_file, delimiter=",", dtype=str).copy()
    emails_df.rename(columns={"Household Id": "lookup_household_id"}, inplace=True)
    print("Itterating through records...")

    out = emails_df.progress_apply(process_household, args=(checker,), axis=1)
    print("Exporting results to CSV...")
    out.to_csv(file_out, sep="\t", index=False)
    print("All done! View file at {}".format(file_out))


if __name__ == "__main__":
    typer.run(main)
