"""domainspotter.py - This module provides a function for searching newly registered domains that match a user-provided wordlist."""

import sys
import os
import base64
import argparse
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import List, Tuple
from zipfile import ZipFile, BadZipFile
import httpx
from httpx import get
from rich.console import Console

AUTHOR = "Michael Rippey, Twitter: @nahamike01"
LAST_SEEN = "2023 Jan 07"
DESCRIPTION = """Search for suspect domains using fuzzy string matching and a user defined wordlist"""

console = Console()

try:
    from rapidfuzz import process

except ImportError:
    print("rapidfuzz not installed, try:")
    print("\t\t python3 -m pip3 install rapidfuzz")
    sys.exit(1)

file_name_date = datetime.now().strftime("%Y-%m-%d")

WHOISDS_URL = "https://whoisds.com//whois-database/newly-registered-domains/"


def format_url_with_date() -> str:
    """
    Set date to yesterday"s date in
    Args: None
    Returns:
    str -> Yesterday"s date Base64 encoded with additional information for URL
    """
    yesterday = datetime.now() - timedelta(days=2)
    format_date = datetime.strftime(yesterday, "%Y-%m-%d")
    url_add_ext = f"{format_date}.zip"
    return base64.b64encode(url_add_ext.encode("utf-8")).decode("utf-8")


def get_whoisds_new_domains_list() -> bytes:
    """
    Fetch content from WHOISDS website for new domains file
    Args: None
    Returns:
    requests.Response -> Content of server response
    (zip file of newly registered domains)
    """
    # add_date_url = format_date_url()

    try:

        # console.print(f"[+] Connecting to {format_url_with_date()}\n", style="bold white")
        headers = {"User-Agent": "DomainSpotter v0.2 (GitHub Username: @mrippey"}
        new_reg_domains = get(
            WHOISDS_URL + format_url_with_date() + "/nrd", headers=headers
        )
        new_reg_domains.raise_for_status()

    except (httpx.HTTPError, httpx.ConnectTimeout) as err:
        console.print(f"[!] Exception: {err}", style="bold red")
        console.print(
            "[!] Connection timed out. Today's domains list may not have been posted yet. Please try again later.",
            style="bold red",
        )

        sys.exit(1)

    return new_reg_domains.content


def open_new_domains_file() -> List[str]:
    """
    Open and read returned zip file from request
    Args: None
    Returns:
    List[str] -> The zip file is read and returns each newly
    identified domain as a list of strings.
    """
    # domain_file = get_whoisds_new_domains_list()
    domains = []

    try:

        with ZipFile(BytesIO(get_whoisds_new_domains_list())) as data:

            for info in data.infolist():
                with data.open(info) as lines:
                    for line in lines:

                        file = line.decode("utf-8")
                        domains.append(str(file).rstrip("\r\n"))

    except BadZipFile as err:
        console.print(f"[!] {err}", style="bold red")

    except UnicodeDecodeError as err:
        console.print(f"[!] {err}", style="bold red",)

        sys.exit(1)

    return domains


def rapidfuzz_multi_query(wordlist) -> List[Tuple]:
    """
    Return RapidFuzz string match of search query
    Args: query_str
    Returns:
    List[Tuple] -> Best matches based on similarity
    """
    if wordlist is None or wordlist == "":
        return
    console.print(
        f"[+] Connecting to {WHOISDS_URL + format_url_with_date()}\n",
        style="bold white",
    )

    console.print(
        "[+] Newly Registered Domains list opened. Conducting fuzzy string matching...\n",
        style="bold white",
    )

    paths = []

    with open(wordlist, "r", encoding='utf-8') as data:
        # query_str = data.readlines()

        paths = [uri_path.strip() for uri_path in data.readlines()]

    new_domains_list = open_new_domains_file()
    split_wordlist_name = os.path.splitext(wordlist)[0]
    for query in paths:
        results_file = (
            Path.cwd() / f"{split_wordlist_name}_{file_name_date}_matches.txt"
        )
        matches = process.extract(query, new_domains_list, limit=10, score_cutoff=70)

        for match in matches:
            # print(f"[*] {result[0]}")

            with open(results_file, "a", encoding='utf-8') as output_file:

                output_file.write(match[0] + "\n")

    console.print(f"[!] Done. Output file can be found at: {results_file}", style="bold white")


def main():
    """  main.py -- Run the program """    
    
    banner = """
    
  __   __                    __   __   __  ___ ___  ___  __  
 |  \ /  \ |\/|  /\  | |\ | /__` |__) /  \  |   |  |__  |__) 
 |__/ \__/ |  | /~~\ | | \| .__/ |    \__/  |   |  |___ |  \                                                                           
--------------------------------------------------------------------------
"""
    parser = argparse.ArgumentParser(
        description=f"{banner}\nBy: {AUTHOR}\tLast_Seen: {LAST_SEEN}\n\nDescription: {DESCRIPTION}".format(
            banner, AUTHOR, LAST_SEEN, DESCRIPTION
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-w", "--wordlist", help="Wordlist to conduct similarity test against."
    )

    args = parser.parse_args()

    if args.wordlist:
        print(banner)
        print()
        rapidfuzz_multi_query(args.wordlist)

    else:
        print(banner)
        menu_help = """[!] usage: python3 domainspotter.py --wordlist /path/to/users/desired/wordlist """
        print(f"[!] No argument provided. \n{menu_help}\n")
        return


if __name__ == "__main__":
    main()
