# Research into the use of Ministry of Digital Development root certificates and self-signed SSL certificates on the Runet

This script allows you to analyze which sites require a Russian root certificate to work correctly.
It also checks for the presence of some self-signed certificates issued by companies associated with Russia.
The results of each run are stored in the `results` directory and in the SQlite3 [statistics.db](statistics.db) database
at the end of the analysis.

Note: the dataset is certainly not complete yet, pull requests are welcome. Especially for the dump of actual government
domains.

## TLDR

A dataset of 21698 sites was analyzed.

- Government associated sites:
  - 667 sites require a Russian Trusted CA.
  - 250 sites use self-signed certificates issued in Russia.
- Social important sites:
  - 5 site require a Russian Trusted CA.
  - 0 sites use self-signed certificates issued in Russia.
- Top-100 sites in Russia:
  - 1 site require a Russian Trusted CA.
  - 0 sites use self-signed certificates issued in Russia.

## About Russian Trusted CA

Many Russian companies face severe sanctions, forcing reputable companies to avoid receiving or paying money to/from
Russian companies in order to avoid investigations into sanctions bypass.

Certification Authorities (CA), which issue encryption keys for websites, are among the companies that have refused to
work with Russian companies because of the sanctions policy.

As a result, some websites have been forced to use a certificate from the Russian Ministry of Communications, which is
not accepted by any browser outside of Russia.

In addition, the Russian authorities, in another rush to censor the Internet, have taken advantage of this situation and
have begun to force all government (and not just government) websites to use such a certificate. This raises some
concerns.

Using Russian certificates is risky, because it is not clear whether they meet the standards of a trusted Certificate
Authority. There are concerns that Russian Certificate Authorities may issue additional private keys for agencies such
as the FSB, etc.

## Results

There are several directories in the `results/`:

- [results/government/](results/government) – list of results for russian government associated sites;
- [results/social/](results/social) – list of results for russian government associated sites;
- [results/top/](results/top) – list of results for russian government associated sites.

There are several files in each directory:

- `russian_trusted_ca.txt` – list of sites requiring Russian Trusted CA;
- `ru_self_sign.txt` – list of sites using self-signed certificate issued in Russia;
- `other_ssl_err.txt` – list of requests that failed due to any other SSL errors;
- `request_errors.txt` – list of failed requests (due to Python exception);
- `unsuccessful.txt` – list of failed requests with their status codes;
- `timeout_err.txt` – list of requests closed due to timeout.

### Database

The results of each run are stored in a SQLite database [statistics.db](statistics.db). You can easily access the
statistics with SQL queries.

#### Some useful SQL queries

- `SELECT * FROM statistic_table WHERE date_time = (SELECT MAX(date_time) FROM statistic_table);` – get all results for
  last analysis date;
- `SELECT * FROM statistic_table WHERE date_time LIKE '2023-04-27%';` – get all results for specific date;
- `SELECT gov_ca_list, COUNT(*) AS count FROM statistic_table GROUP BY gov_ca_list ORDER BY count DESC;` – get all-time
  statistic for specific column, `gov_ca_list` for example.

#### Database scheme

    id INTEGER PRIMARY KEY,                   # primary key;
    date_time TEXT NOT NULL,                  # current date and time (UTC);
    timeout INTEGER NOT NULL                  # timeout value for each exec;
    gov_count INTEGER NOT NULL,               # government dataset size;
    gov_ca_list TEXT NOT NULL,                # list of gov sites with a Russian trusted CA;
    gov_ss_list TEXT NOT NULL,                # list of gov sites with self-signed certificates;
    gov_other_ssl_err_list TEXT NOT NULL,     # list of gov sites with other SSL errors;
    social_count INTEGER NOT NULL,            # social dataset size;
    social_ca_list TEXT NOT NULL,             # list of social sites with a Russian trusted CA;
    social_ss_list TEXT NOT NULL,             # list of social sites with self-signed certificates;
    social_other_ssl_err_list TEXT NOT NULL,  # list of social sites with other SSL errors;
    top_count INTEGER NOT NULL,               # top-100 dataset size;
    top_ca_list TEXT NOT NULL,                # list of top-100 sites with a Russian trusted CA;
    top_ss_list TEXT NOT NULL,                # list of top-100 sites with self-signed certificates;
    top_other_ssl_err TEXT NOT NULL,          # list of top-100 sites with other SSL errors;
    is_dataset_updated INTEGER NOT NULL       # boolean flag set to true when dataset/self-sign list has been updated.

## Running

### Prerequisites

Python3 compatibility:

- python3.11 – tested, works ✅;
- python3.9-3.10 – not tested, might work;
- python3.8 and earlier – doesn't work 🛑.

Before running, be aware that many resources only allow incoming traffic from Russian IP addresses.

Note: with a higher timeout valueA higher timeout value will give more accurate results, but the speed of the analysis
will be significantly reduced.

### Perform the analysis

Run the following commands in the terminal:

```bash
python3 -m venv env               # create virtual python environment;
source env/bin/activate           # activate virtual python environment;
pip3 install -r requirements.txt  # install dependencies;

python3 check.py                  # run the analysis (use statistics.db and timeout=30 seconds by default);

deactivate                        # deactivate python environment.

```

#### Command line arguments

- `--timeout`, `default=30`, timeout for each web request, in seconds;
- `--name`, `default=statistics.db`, database name with `.db` extension, if it does not exist – it will be created;
- `--updated`, `default=False`, flag indicating that the dataset/self-sign list has been updated. This flag must be set to `True` if
  dataset has been updated.

#### Examples

- Perform analysis with default parameters (db name: `statistic.db`, `timeout`: 30 secs) – `python3 check.py`
- Perform analysis with custom database name and timeout – `python3 check.py --name=test.db --timeout=5`
- Perform analysis with default parameters, but set that the dataset/self-sign list has been updated before
  running – `python3 check.py --updated=True`
- Get help – `python3 check.py --help`

## Contributions

Your contribution will be very valuable, especially if you can add relevant sites for analysis.

Dataset format:

- without the leading `http://`, `https://` or `www.`;
- without `/` or any additional path at the end of the primary domain.

## Additional tools

### Save links

[save_links.py](save_links.py) – this script can parse and store any links at a provided url.

Usage:
`python3 save_links.py <url>`

### Deduplication

[dedup.py](dedup.py) – this script can perform deduplication of dataset files.

Usage:
`python3 dedup.py <source_file> <deduplicated_file>`

## Used resources

- Big government associated domains was taken from [govdomains](https://github.com/infoculture/govdomains) repo;
- LIST OF SOCIALLY IMPORTANT INFORMATION RESOURCES ON THE
  INTERNET [consultant.ru](http://www.consultant.ru/document/cons_doc_LAW_349660/5715f8a0641b857e9e101510d765f9671e6b716a/)
