import pandas as pd
import os
from tqdm import tqdm
from time import sleep
import typer
from pathlib import Path
from googleaccountchecker import GoogleAccountChecker
from urllib.parse import urlsplit, parse_qs
from enum import Enum


class FileFormat(str, Enum):
    txt = "txt"
    csv = "csv"


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
    google_doc: str = typer.Option(
        None, help="URL or ID of any Google Doc in your account"
    ),
    out_format: FileFormat = typer.Option(
        FileFormat.txt, help="Format of output file", case_sensitive=False
    ),
):
    if google_doc.startswith("http"):
        split_url = urlsplit(google_doc)
        docs_id = str(dict(parse_qs(split_url.query)).get("id"))
    else:
        docs_id = google_doc
    print("Processing...")
    checker = GoogleAccountChecker(cookies_path)
    checker.setup(docs_id)
    tqdm.pandas(desc="Processing Households")
    file_out = os.path.join(
        os.path.dirname(os.path.realpath(input_file)),
        os.path.splitext(input_file)[0] + f" - Google PCR Import.{out_format}",
    )
    emails_df = pd.read_csv(input_file, delimiter=",", dtype=str).copy()
    emails_df.rename(columns={"Household Id": "lookup_household_id"}, inplace=True)
    print("Itterating through records...")

    out = emails_df.progress_apply(process_household, args=(checker,), axis=1)
    print("Exporting results to CSV...")
    if out_format == FileFormat.txt:
        out_separator = "\t"
    else:
        out_separator = ","
    out.to_csv(file_out, sep=out_separator, index=False)
    print("All done! View file at {}".format(file_out))


if __name__ == "__main__":
    typer.run(main)
