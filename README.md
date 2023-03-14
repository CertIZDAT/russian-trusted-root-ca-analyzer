# Russian sites what require Russian Trusted CA

IN ACTIVE DEVELOPMENT: SOME RESULTS ARE OUTDATED!

This script allows you to analyze which sites require a Russian Trusted CA certificate to work properly. Also checks for strange certificates issued by Russia.

[tls_list_cleaned.txt](tls_list_cleaned.txt) list is definitely not complete yet, PR's are welcome.

## Summary

Russian banks and other companies, including Sberbank, are facing severe sanctions causing reputable companies to avoid receiving or paying money to/from companies banks to avoid being investigated for circumventing sanctions. Certification authorities (CAs), which issue encryption keys to websites, are among the companies that have refused to work with Sberbank due to the sanctions. As a result, Sberbank had to use a self-signed certificate from the Ministry of Communications, which no browser outside of Russia accepts. Using Russian certificates is risky as it is unclear if they meet the standards for a normal CA, and they may create additional private keys for authorities like FSB.

### TLDR

A dataset of 24163 sites was examined. Of these, 851 sites were found to require a Russian Trusted CA. In addition, 137 sites were found to be using self-signed certificates.

## Results

There are five files with results:

* [ssl_cert_err.txt](ssl_cert_err.txt) – Failed request due to Russian Trusted Sub CA requirement;
* [ssl_self_sign_err.txt](ssl_self_sign_err.txt) – Failed request due to Russian self signed certificate;
* [request_errors.txt](request_errors.txt) – Unsuccessful requests (Python RequestException);
* [unsuccessful.txt](unsuccessful.txt) – Unsuccessful requests and their status codes;
* [successful.txt](successful.txt) – List of successful requests;
* [other_ssl_cert_err.txt](other_ssl_cert_err.txt) – Failed request due to any SSL error.

### Get total count of all sites with Russian Trusted CA

    grep "Russian Trusted" ssl_cert_err.txt | wc -l

## Running

Run the following commands in terminal:

```bash
python3 -m venv env                 # create virtual python environment
source env/bin/activate             # start virtual python environment
pip3 install -r requirements.txt    # install necessary packages
python3 check.py                    # start analysis
deactivate                          # to deactivate python environment
```

Note: Approximate analysis time with 8 cores (with 5 multiplier) and fast VPN is ~12 hours.

## Contributions

The input is really valuable, especially if you can add relevant sites for analysis.
Links format:

* without `http://` or `https://` or `www.`;
* without `/` or any additional path at the end of the link.

## Additional tools

### Save links

[save_links.py](save_links.py) – this script can parse any links at provided url

`python3 save_links.py <url>`

### Deduplication

[dedup.py](dedup.py)

`python3 dedup.py <source_file> <deduplicated_file>`

## Used resources

* The initial [list](tls_list_cleaned.txt) of sites to check was taken (and slightly updated) from [koenrh's repository](https://github.com/koenrh/russian-trusted-root-ca).
* Big government associated domains was taken from [govdomains](https://github.com/infoculture/govdomains)
