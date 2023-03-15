import argparse
import concurrent.futures
import ssl
from multiprocessing import cpu_count
from time import time

import requests
from OpenSSL import crypto

from utils import common, db


def check_link(link, index, website_links, timeout):
    # define headers to send with each request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    untrusted = ["Russian Trusted"]

    self_signed = ["SberCA", "St. Petersburg", "VTB Group", "Bank GPB", "Администрация Партизанского городского округа",
                   "Kaliningrad", "Sigma-REZERV", "Moscow", "Stavrolop", "Saint Petersburg", "Petrozavodsk", "Bryansk", "sklif"]

    link = link.strip()
    if not link.startswith('http'):
        link = f'https://{link}'
    try:
        response = requests.get(link, headers=headers, timeout=timeout)
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
    except requests.exceptions.Timeout as e:
        print(f'{index}/{len(website_links)}: {link}: Request timed out')
        with open('unsuccessful.txt', 'a') as f:
            f.write(
                link + ' – Request timed out' + '\n')
    except requests.exceptions.SSLError as e:
        cert = ssl.get_server_certificate((link.split("//")[1], 443))
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        # get issuer of the certificate
        issuer = x509.get_issuer().get_components()[2][1].decode()

        if any(untrust in issuer for untrust in untrusted):
            print(
                f'{index}/{len(website_links)}: {link}: Russian affiliated certificate error – {issuer}')
            with open('ssl_cert_err.txt', 'a') as f:
                f.write(link + ' – CA: {}'.format(issuer) + '\n')
        elif any(untrust in issuer for untrust in self_signed):
            print(
                f'{index}/{len(website_links)}: {link}: Russian self signed certificate error – {issuer}')
            with open('ssl_self_sign_err.txt', 'a') as f:
                f.write(link + ' – CA: {}'.format(issuer) + '\n')
        else:
            print(
                f'{index}/{len(website_links)}: {link}: Other SSL certificate error – {issuer}')
            with open('other_ssl_cert_err.txt', 'a') as f:
                f.write(link + ' – CA: {}'.format(issuer) + '\n')

    except requests.exceptions.RequestException as e:
        with open('request_errors.txt', 'a') as f:
            f.write(link + ' – error: {}'.format(e) + '\n')
        print(f'{index}/{len(website_links)}: {link}: {e}')


def main():
    parser = argparse.ArgumentParser(
        description='This script allows you to analyse which sites require a Russian Trusted CA certificate to work properly.')
    parser.add_argument('--timeout', default=15, type=int,
                        help='Timeout for each web request, in seconds.')
    parser.add_argument('--db_name', default='statistics', type=str,
                        help='Database name, if it does not exist - it will be created.')
    parser.add_argument('--dataset_updated', default=False,
                        help='Flag signalling that the dataset has been updated.')
    parser.add_argument('--delete', type=str,
                        help='Delete existed database with name.')
    args = parser.parse_args()

    need_to_del_db = args.delete
    db.need_to_del_db(need_to_del_db)

    timeout = int(args.timeout)
    db_name = args.db_name
    is_dataset_updated = args.dataset_updated

    common.delete_old_res()

    with open('tls_list_cleaned.txt', 'r') as f:
        website_links = f.readlines()

    # create thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count() * 6) as executor:
        # submit tasks to thread pool
        futures = [executor.submit(check_link, link, i+1, website_links, timeout)
                   for i, link in enumerate(website_links)]

        # wait for tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                _ = future.result()  # get result of task (not used in this case)
            except Exception as e:
                print(f'Error: {e}')


if __name__ == '__main__':
    start_time = time()

    main()

    end_time = time()
    execution_time = end_time - start_time

    print(f"Execution time:\n\
        {execution_time:.2f} seconds,\n\
        {execution_time / 60:.2f} minutes, \n\
        {execution_time / 60 / 60:.2f} hours.")
