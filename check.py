import os
import ssl
import requests
import concurrent.futures
from OpenSSL import crypto
from multiprocessing import cpu_count

# remove output files from previous runs
if os.path.exists('successful.txt'):
    os.remove('successful.txt')
if os.path.exists('unsuccessful.txt'):
    os.remove('unsuccessful.txt')
if os.path.exists('ssl_cert_err.txt'):
    os.remove('ssl_cert_err.txt')
if os.path.exists('request_errors.txt'):
    os.remove('request_errors.txt')
if os.path.exists('other_ssl_cert_err.txt'):
    os.remove('other_ssl_cert_err.txt')

with open('tls_list_cleaned.txt', 'r') as f:
    website_links = f.readlines()

# define headers to send with each request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def check_link(link, index):
    link = link.strip()
    if not link.startswith('http'):
        link = f'https://{link}'
    try:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            with open('successful.txt', 'a') as f:
                f.write(link + '\n')
            print(f'{index}/{len(website_links)}: {link}: HTTPS request successful')
        else:
            with open('unsuccessful.txt', 'a') as f:
                f.write(
                    link + ' – status code: {}'.format(response.status_code) + '\n')
            print(
                f'{index}/{len(website_links)}: {link}: HTTPS request failed with status code {response.status_code}')
    except requests.exceptions.SSLError as e:
        cert = ssl.get_server_certificate((link.split("//")[1], 443))
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        issuer = x509.get_issuer().get_components()[2][1].decode()

        print(f'Root CA name: {issuer}')
        if issuer == 'Russian Trusted Sub CA':
            print(
                f'{index}/{len(website_links)}: {link}: Russian CA certificate error')
            with open('ssl_cert_err.txt', 'a') as f:
                f.write(link + ' – CA: {}'.format(issuer) + '\n')
        else:
            print(
                f'{index}/{len(website_links)}: {link}: Other SSL certificate error')
            with open('other_ssl_cert_err.txt', 'a') as f:
                f.write(link + ' – CA: {}'.format(issuer) + '\n')

    except requests.exceptions.RequestException as e:
        with open('request_errors.txt', 'a') as f:
            f.write(link + ' – error: {}'.format(e) + '\n')
        print(f'{index}/{len(website_links)}: {link}: {e}')


# create thread pool
with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
    # submit tasks to thread pool
    futures = [executor.submit(check_link, link, i+1)
               for i, link in enumerate(website_links)]

    # wait for tasks to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            _ = future.result()  # get result of task (not used in this case)
        except Exception as e:
            print(f'Error: {e}')
