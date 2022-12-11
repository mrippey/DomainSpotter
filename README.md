# DomainSpotter

Have a list of keywords you want to check for typosquatting domains against? DomainSpotter pulls down the most recent list of newly registered domains from WHOISDS, and finds similarly named domains using RapidFuzz. *Note: The cutoff score for RapidFuzz is set to 80 by default. Play around with the score as you see fit.

## Usage

DomainSpotter supports the following:

```bash
domainspotter.py -h

Examples:
         python newdomainspotter.py --wordlist /path/to/user/defined/wordlist
         
optional arguments:
  -h, --help            show this help message and exit
  -w  --wordlist WORDLIST
                        Conduct a fuzzy string match of similar domains using RapidFuzz against user provided wordlist.
 
