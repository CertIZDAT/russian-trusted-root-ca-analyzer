# Russian sites what require Russian Trusted CA

This script allows you to analyse which sites require a Russian Trusted CA certificate to work properly.

The [list](tls_list_cleaned.txt) of sites to check was taken (and slightly updated) from [koenrh's repository](https://github.com/koenrh/russian-trusted-root-ca), thx.

## Results

There are five files with results:

* [ssl_cert_err.txt](ssl_cert_err.txt) – Failed request due to Russian Trusted Sub CA requirement;
* [request_errors.txt](request_errors.txt) – Unsuccessful requests (Python RequestException);
* [unsuccessful.txt](unsuccessful.txt) – Unsuccessful requests and their status codes;
* [successful.txt](successful.txt) – List of successful requests;
* [other_ssl_cert_err.txt](other_ssl_cert_err.txt) – Failed request due to any SSL error.

## Running

Run the following commands in terminal:

```bash
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python3 check.py
deactivate
```
