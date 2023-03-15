# Russian sites what require Russian Trusted CA

IN ACTIVE DEVELOPMENT: SOME RESULTS ARE OUTDATED!

This script allows you to analyze which sites require a Russian Trusted CA certificate to work properly. Also checks for strange certificates issued by Russia.
Results of each run saved to sqlite database at end of the analysis.

[tls_list_cleaned.txt](tls_list_cleaned.txt) list is definitely not complete yet, PR's are welcome.

## Summary

Russian banks and other companies, including Sberbank, are facing severe sanctions causing reputable companies to avoid receiving or paying money to/from companies banks to avoid being investigated for circumventing sanctions. Certification authorities (CAs), which issue encryption keys to websites, are among the companies that have refused to work with Sberbank due to the sanctions. As a result, Sberbank had to use a self-signed certificate from the Ministry of Communications, which no browser outside of Russia accepts. Using Russian certificates is risky as it is unclear if they meet the standards for a normal CA, and they may create additional private keys for authorities like FSB.

### TLDR

~~A dataset of 24163 sites was examined. Of these, 851 sites were found to require a Russian Trusted CA. In addition, 137 sites were found to be using self-signed certificates.~~

## Results

There are five files with results:

- [ssl_cert_err.txt](ssl_cert_err.txt) – Failed request due to Russian Trusted Sub CA requirement;
- [ssl_self_sign_err.txt](ssl_self_sign_err.txt) – Failed request due to Russian self signed certificate;
- [request_errors.txt](request_errors.txt) – Unsuccessful requests (Python RequestException);
- [unsuccessful.txt](unsuccessful.txt) – Unsuccessful requests and their status codes;
- [successful.txt](successful.txt) – List of successful requests;
- [other_ssl_cert_err.txt](other_ssl_cert_err.txt) – Failed request due to any SSL error.

### Get total count of all sites with Russian Trusted CA

    cat ssl_cert_err.txt | wc -l

## Running

Before running you should understand that many resources allow income traffic only from Russian IP's addresses.

Note: Approximate analysis time with 8 cores, `timeout=15` and fast VPN is 30 minutes.

### Analysis

Run the following commands in terminal:

```bash
python3 -m venv env                 # create virtual python environment;
source env/bin/activate             # start virtual python environment;
pip3 install -r requirements.txt    # install necessary packages;

# Default param value is 15 seconds;
python3 check.py [--param=<val> --param...]  # start analysis with specified timeout param, see "Parameters" and "Examples" sections;

deactivate                          # to deactivate python environment
```

### Parameters

- `--timeout`, default=15, timeout for each web request, in seconds.
- `--name`, default='statistics.db', type=str, database name, if it does not exist - it will be created.
- `--updated`, default=False, flag signalling that the dataset has been updated. This flag must be set to true if the dataset has been.
- `--delete`, type=str, delete existed database with name.

#### Examples

- Run analysis with standard params (db name: `statistic.db`, `timeout`: 15 secs) – `python3 check.py`
- Run analysis with custom db name and timeout – `python3 check.py --name=test.db --timeout=5`
- Run analysis with standard params, set dataset was updated before run – `python3 check.py --updated=True`
- Delete db with custom name – `python3 check.py  --delete=test_db.db`
- Get help – python3 check.py --help

## Contributions

The input is really valuable, especially if you can add relevant sites for analysis.
Links format:

- without `http://` or `https://` or `www.`;
- without `/` or any additional path at the end of the link.

## sqlite database scheme

    id INTEGER PRIMARY KEY,                 # primary key
    date_time TEXT NOT NULL,                # current date and time (UTC)
    trusted_ca_count INTEGER NOT NULL,      # total sites count with Russian Trusted CA
    self_signed_count INTEGER NOT NULL,     # total sites count with self signed certificates
    list_of_trusted_ca TEXT NOT NULL,       # list of links contains sites with Russian Trusted CA
    list_of_self_sign TEXT NOT NULL,        # list of links contains sites with self signed certificates
    is_dataset_updated INTEGER NOT NULL     # bool flag, which must be set to true if the dataset has been updated

## Additional tools

### Save links

[save_links.py](save_links.py) – this script can parse any links at provided url

`python3 save_links.py <url>`

### Deduplication

[dedup.py](dedup.py)

`python3 dedup.py <source_file> <deduplicated_file>`

## Used resources

- The initial [list](tls_list_cleaned.txt) of sites to check was taken (and slightly updated) from [koenrh's repository](https://github.com/koenrh/russian-trusted-root-ca).
- Big government associated domains was taken from [govdomains](https://github.com/infoculture/govdomains)
- LIST OF SOCIALLY IMPORTANT INFORMATION RESOURCES ON THE INTERNET [consultant.ru](http://www.consultant.ru/document/cons_doc_LAW_349660/5715f8a0641b857e9e101510d765f9671e6b716a/)
