AUTHOR = "Michael Rippey, Twitter: @nahamike01"
LAST_SEEN = "2022 Dec 11"
DESCRIPTION = """Search for suspect domains using fuzzy string matching and a user defined wordlist"""


"""domainspotter.py_ = Search for new domains using RapidFuzz"""

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

    try:
       
        console.print(f"[+] Connecting to {WHOISDS_URL}\n", style="bold white")
        headers = {"User-Agent": "DomainSpotter v0.2 (GitHub Username: @mrippey"}
        new_reg_domains = get(WHOISDS_URL + format_url_with_date() + "/nrd", headers=headers)
        new_reg_domains.raise_for_status()

    except httpx.TimeoutException as err:
        console.print(f"[!] Exception: {err}", style="bold red")
        console.print(
            "[!] Connection timed out. Today's domains list may not have been posted yet. Please try again later.",
            style="bold red",
        )
        
        sys.exit(1)
    except httpx.RequestError as err:
        console.print(f"[!] Requests Module Exception: {err}", style="bold red")
        

    return new_reg_domains.content


def open_new_domains_file() -> List[str]:
    """
    Open and read returned zip file from request
    Args: None
    Returns:
    List[str] -> The zip file is read and returns each newly
    identified domain as a list of strings.
    """
  
    domains = []

    try:
        
        console.print(
            "[+] Opening and reading newly registered domains list...\n", style="bold white"
        )
        with ZipFile(BytesIO(get_whoisds_new_domains_list())) as data:

            for info in data.infolist():
                with data.open(info) as lines:
                    for line in lines:

                        file = line.decode("ascii")
                        domains.append(str(file).rstrip("\r\n"))

    except BadZipFile as err:
        console.print(f"[!] {err}", style="bold red")
       
        sys.exit(1)

    return domains


def rapidfuzz_multi_query(wordlist) -> List[Tuple]:
    """
    Return RapidFuzz string match of search query
    Args: query_str
    Returns:
    List[Tuple] -> Best matches based on similarity
    """
    if wordlist is None or wordlist == '':
        return    
    console.print("[+] Conducting Fuzzy string match using RapidFuzz...\n")
    paths = []

    
    with open(wordlist, "r") as data:

        paths = [uri_path.strip() for uri_path in data.readlines()]

    new_domains_list = open_new_domains_file()
    split_wordlist_name = os.path.splitext(wordlist)[0]
  
    for query in paths:
        results_file = Path.cwd() / f"{split_wordlist_name}_{file_name_date}_matches.txt"
        matches = process.extract(query, new_domains_list, limit=10, score_cutoff=80)

        for match in matches:
            # print(f"[*] {result[0]}")

            with open(results_file, "a") as output_file:
               
                output_file.write(match[0] + "\n")

    console.print(
        f"[!] Done. File written to: {results_file}", style="bold white"
    )


def main():
    banner = """
    
  __   __                    __   __   __  ___ ___  ___  __  
 |  \ /  \ |\/|  /\  | |\ | /__` |__) /  \  |   |  |__  |__) 
 |__/ \__/ |  | /~~\ | | \| .__/ |    \__/  |   |  |___ |  \                                                                           
--------------------------------------------------------------------------
"""
    parser = argparse.ArgumentParser(description=f"{banner}\nBy: {AUTHOR}\tLast_Seen: {LAST_SEEN}\n\nDescription: {DESCRIPTION}".format(banner, AUTHOR, LAST_SEEN, DESCRIPTION), formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-w", "--wordlist", help="Wordlist to conduct similarity test against.")

    args = parser.parse_args()

    if args.wordlist: 
        print(banner)
        print() 
        rapidfuzz_multi_query(args.wordlist)

    else: 
        print(banner)
        menu_help = """[!] usage: python3 domainspotter.py --wordlist /path/to/users/desired/wordlist """
        print(f"[!] No argument provided. \n{menu_help}")
        print()
        return


if __name__ == '__main__':
    main()
