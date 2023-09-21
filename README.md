# Research into the use of the Russian Trusted CA root Certificate and self-signed SSL Certificates on the Russian Internet

Want to go to the technical part? Go [here](#technical-details)

This article also available in PDF format: [English](https://github.com/CertIZDAT/russian-trusted-root-ca-analyzer/blob/master/article_en.pdf) or [Russian](https://github.com/CertIZDAT/russian-trusted-root-ca-analyzer/blob/master/article_ru.pdf).

## Introduction

This report delves into digital security and the usage of the digital certificates on the Russian segment of the Internet. This analysis examines the prevalence of Ministry of Digital Development, Communications and Mass Media root certificates and self-signed SSL certificates associated with Russia. SSL-certificates play a critical role in securing online communication. Our research sheds light on their usage within the Russian cyber landscape.

**Note:** The information in project's [GitHub repository](https://github.com/CertIZDAT/russian-trusted-root-ca-analyzer) is regularly updated to provide up-to-date statistics on root and self-signed certificates usage.

## Understanding the dataset

Our research is based on an extensive dataset comprising 21,698 websites. This dataset serves as the foundation for our exploration of digital certificate usage patterns across different categories of websites.

**Note:** What is an SSL Certificate?

Before we go any further, it's important to clarify what an SSL Certificate is. A Secure Sockets Layer (SSL) certificate is a digital certificate that authenticates the identity of a website and encrypts data sent to the server. In simple terms, it ensures that the information exchanged between a user's browser and a website remains private and secure.

### Government-related sites

We identified 715 government-related sites websites that require a Russian Trusted CA, and 249 sites that use self-signed SSL certificates issued by Russian-linked companies. These findings reveal the significant presence of such certificates in the government sector.

### Socially important sites

We also examined socially important sites. Within this category, we found that 7 sites require a Russian Trusted CA, while none of them use self-signed SSL Certificates issued in Russia. These results provide an insight into the reliance on Russian Trusted CAs for access to socially important platforms.

**Note:**

- *Government-related sites* include official sites that are either directly or indirectly related to the government. The list of these sites can be found [here](https://github.com/infoculture/govdomains).
- *Socially important sites* are sites to which telecom operators are required by law to provide free access for every citizen [source](https://digital.gov.ru/uploaded/files/prilozhenie-k-prikazu-280.pdf). These sites are considered critical for access by all citizens and include entities such as Russian social networks, banks, government portals, etc.

It's important to note that these categories, especially *Socially important sites*, include very important and popular platforms such as SberBank (the most popular bank in Russia) and GosUslugi, which provides access to state functions and services. Consequently, the requirement to use Russian Trusted CA in this category has the potential to force a large number of people to install Russian Trusted CA on their primary devices.

### Top-100 websites in Russia

This research extended to the top 100 websites in Russia by traffic. Among these, only one site required a Russian Trusted CA, and none of them used self-signed SSL Certificates issued in Russia. But that's SberBank – an extra popular bank in Russia. But in general, this result shows that the most popular websites in Russia tend to use certificates issued by internationally recognised certification centres.


## The role of the Russian Trusted CA

### Sanctions and Certification Authorities

One of the key drivers behind the use of Russian Trusted CAs is the sanctions imposed on Russian companies (as stated by the Russian government). These sanctions have forced many reputable companies to avoid financial transactions with their Russian counterparts in order to avoid sanctions-related investigations. Even some Certification Authorities, which issue encryption keys for websites, have refrained from working with Russian companies because of these sanctions.

### The Russian Ministry of Digital Development, Communications, and Mass Media

As a result, some websites have resorted to using certificates issued by the Russian Ministry of Communications. However, it's important to note that these certificates are marked as insecure in all modern web browsers, with some exceptions like Yandex Browser and certain custom in-house builds of Chromium Browser used by government agencies. Moreover, it should be noted that the analysis of the source code of Yandex.Browser shows that the application of the Russian Trusted CA is currently possible only on sites from a special list [source](https://github.com/yandex/domestic-roots-patch). Attempting to apply the certificate to other domains will result in a standard error and inaccessibility of the site for the user.

## Security risks and concerns

There are inherent risks in using Russian certificates. It remains unclear whether these certificates meet the rigorous standards expected of a trusted Certificate Authority. This uncertainty raises concerns about the reliability and trustworthiness of the certificates issued by Russian CAs.

It's important to note that cryptography in Russia has already been criticised, including issues such as a lack of randomness in the permutation table [source](https://eprint.iacr.org/2016/071) and the theoretical possibility of a backdoor in S-Box [source](https://eprint.iacr.org/2019/092) in "Streebog" and "Kuznyechik" algorithms.

There is an apparent disparity in the perception of security between Russian browsers and those used internationally. While Russian browsers may accept these certificates, they are met with skepticism by most international browsers. This divergence in trust standards can lead to unforeseen consequences for users and organizations relying on such certificates.

## Potential for abuse

There are also concerns that Russian Certificate Authorities may issue additional private keys for government agencies such as the Federal Security Service (FSB) and other intelligence services. See the [MITM incident](https://en.wikipedia.org/wiki/Kazakhstan_man-in-the-middle_attack) in Kazakhstan. Such practices could potentially compromise the security and privacy of online communications.

## Implications and consequences

The results of our research underscore the complex landscape of digital security on the Russian internet. The proliferation of Russian Trusted CAs and self-signed SSL Certificates associated with Russia poses significant challenges and risks to both individuals and organisations.

## Conclusion

In conclusion, our research provides valuable insights into the use of Russian Trusted CA and self-signed SSL Certificates on the Russian Internet. These certificates, while prevalent in certain sectors, come with security and trustworthiness concerns. It is essential for users and organizations to make informed choices when navigating the online landscape to ensure their digital security and privacy are protected. The implications of these findings go beyond just the technical; they touch upon the very fabric of civil society and society at large, where privacy and security are fundamental rights that must be protected. The use of such certificates may have unforeseen consequences, given the uncertainty about their compliance with international standards and some concerns about potential access by the government to private keys.

## Technical Details

This script allows you to analyze which sites require a Russian root certificate to work correctly.
It also checks for the presence of some self-signed certificates issued by companies associated with Russia.
The results of each run are stored in the `results` directory and in the SQlite3 [statistics.db](statistics.db) database
at the end of the analysis.

Note: the dataset is certainly not complete yet, pull requests are welcome. Especially for the dump of actual government
domains.

### TLDR

A dataset of 21698 sites was analyzed.

- Government associated sites:
  - 715 sites require a Russian Trusted CA.
  - 249 sites use self-signed certificates issued in Russia.
- Social important sites:
  - 7 site require a Russian Trusted CA.
  - 0 sites use self-signed certificates issued in Russia.
- Top-100 sites in Russia:
  - 1 site require a Russian Trusted CA.
  - 0 sites use self-signed certificates issued in Russia.

### Shortly about Russian Trusted CA

Many Russian companies face severe sanctions, forcing reputable companies to avoid receiving or paying money to/from
Russian companies in order to avoid investigations into sanctions bypass.

Certification Authorities (CA), which issue encryption keys for websites, are among the companies that have refused to
work with Russian companies because of the sanctions policy.

As a result, some websites have been forced to use a certificate from The Russian Ministry of Digital Development, Communications, and Mass Media, which is not accepted by any browser outside of Russia.

In addition, the Russian authorities, in another rush to censor the Internet, have taken advantage of this situation and
have begun to force all government (and not just government) websites to use such a certificate. This raises some
concerns.

Using Russian certificates is risky, because it is not clear whether they meet the standards of a trusted Certificate
Authority. There are concerns that Russian Certificate Authorities may issue additional private keys for agencies such
as the FSB, etc.

### Results

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

#### Database

The results of each run are stored in a SQLite database [statistics.db](statistics.db). You can easily access the
statistics with SQL queries.

##### Some useful SQL queries

- `SELECT * FROM statistic_table WHERE date_time = (SELECT MAX(date_time) FROM statistic_table);` – get all results for
  last analysis date;
- `SELECT * FROM statistic_table WHERE date_time LIKE '2023-04-27%';` – get all results for specific date;
- `SELECT gov_ca_list, COUNT(*) AS count FROM statistic_table GROUP BY gov_ca_list ORDER BY count DESC;` – get all-time
  statistic for specific column, `gov_ca_list` for example.

##### Database scheme

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

### Running

#### Prerequisites

Python3 compatibility:

- python3.11 – tested, works ✅;
- python3.9-3.10 – not tested, might work;
- python3.8 and earlier – doesn't work 🛑.

Before running, be aware that many resources only allow incoming traffic from Russian IP addresses.

Note: with a higher timeout valueA higher timeout value will give more accurate results, but the speed of the analysis
will be significantly reduced.

#### Perform the analysis

Run the following commands in the terminal:

```bash
python3 -m venv env               # create virtual python environment;
source env/bin/activate           # activate virtual python environment;
pip3 install -r requirements.txt  # install dependencies;

python3 check.py                  # run the analysis (use statistics.db and timeout=30 seconds by default);

deactivate                        # deactivate python environment.

```

##### Command line arguments

- `--timeout`, `default=30`, timeout for each web request, in seconds;
- `--name`, `default=statistics.db`, database name with `.db` extension, if it does not exist – it will be created;
- `--updated`, `default=False`, flag indicating that the dataset/self-sign list has been updated. This flag must be set to `True` if
  dataset has been updated.

##### Examples

- Perform analysis with default parameters (db name: `statistic.db`, `timeout`: 30 secs) – `python3 check.py`
- Perform analysis with custom database name and timeout – `python3 check.py --name=test.db --timeout=5`
- Perform analysis with default parameters, but set that the dataset/self-sign list has been updated before
  running – `python3 check.py --updated=True`
- Get help – `python3 check.py --help`

### Contributions

Your contribution will be very valuable, especially if you can add relevant sites for analysis.

Dataset format:

- without the leading `http://`, `https://` or `www.`;
- without `/` or any additional path at the end of the primary domain.

### Additional tools

#### Save links

[save_links.py](save_links.py) – this script can parse and store any links at a provided url.

Usage:
`python3 save_links.py <url>`

#### Deduplication

[dedup.py](dedup.py) – this script can perform deduplication of dataset files.

Usage:
`python3 dedup.py <source_file> <deduplicated_file>`

### Used resources

- Big government associated domains was taken from [govdomains](https://github.com/infoculture/govdomains) repo;
- LIST OF SOCIALLY IMPORTANT INFORMATION RESOURCES ON THE
  INTERNET [consultant.ru](http://www.consultant.ru/document/cons_doc_LAW_349660/5715f8a0641b857e9e101510d765f9671e6b716a/)
