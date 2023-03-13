# Russian sites what require Russian Trusted CA

This script allows you to analyze which sites require a Russian Trusted CA certificate to work properly. Also checks for strange certificates issued by Russia.

The [list](tls_list_cleaned.txt) of sites to check was taken (and slightly updated) from [koenrh's repository](https://github.com/koenrh/russian-trusted-root-ca), thx. This list is definitely not complete yet.

## Summary

Russian banks and other companies, including Sberbank, are facing severe sanctions causing reputable companies to avoid receiving or paying money to/from companies banks to avoid being investigated for circumventing sanctions. Certification authorities (CAs), which issue encryption keys to websites, are among the companies that have refused to work with Sberbank due to the sanctions. As a result, Sberbank had to use a self-signed certificate from the Ministry of Communications, which no browser outside of Russia accepts. Using Russian certificates is risky as it is unclear if they meet the standards for a normal CA, and they may create additional private keys for authorities like FSB.

A dataset of 4105 sites was examined. Of these, 321 sites were found to require a Russian Trusted CA. In addition, 61 sites were found to be using self-signed certificates.

## Results

There are five files with results:

* [ssl_cert_err.txt](ssl_cert_err.txt) – Failed request due to Russian Trusted Sub CA requirement;
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

Note: Approximate analysis time with 8 arm64 cores and fast VPN is 5.7 hours.

## Contributions

The input is really valuable, especially if you can add relevant sites for analysis.

## Additional tools

[save_links.py](save_links.py) – this script can parse any links at provided url

`python3 save_links.py <url>`
