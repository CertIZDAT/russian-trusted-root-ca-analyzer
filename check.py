import argparse
import logging
import multiprocessing as mp
import ssl
import sys
from datetime import datetime
from time import sleep, time

import requests
from OpenSSL import crypto

from utils import common, db

# create logger
logger = logging.getLogger('CA-LOGGER')
logger.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class RemoveNewlineFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        if msg.rstrip() == '':
            return ""
        return msg.rstrip()


class StdoutToLogger:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        if message.rstrip() != "":
            self.logger.info(message.rstrip())

    def flush(self):
        pass


# create file handler and set level to INFO
filename = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S") + '_logfile.log'
file_handler = logging.FileHandler(f'logs/{filename}')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(RemoveNewlineFormatter(formatter._fmt))

# create console handler and set level to INFO
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(RemoveNewlineFormatter(formatter._fmt))

# add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


sys.stdout = StdoutToLogger(logger)


class StdoutToLogger:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        self.logger.info(message)

    def flush(self):
        pass


def check_link(link, index, website_links, timeout, batch_idx, total_batch):
    # define headers to send with each request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    untrusted = ['Russian Trusted']

    self_signed = ['SberCA', 'St. Petersburg', 'VTB Group', 'Bank GPB', 'Администрация Партизанского городского округа',
                   'Kaliningrad', 'Sigma-REZERV', 'Moscow', 'Stavrolop', 'Saint Petersburg', 'Petrozavodsk', 'Bryansk', 'sklif',
                   'SAMARA', 'Samara', 'SPb', 'Vladimir', 's-t-ORK', 'Donetsk', 'Karelia', 'favr.ru', 'Plesk', 'Stavropol']

    link = link.strip()
    if link == '':
        return

    if not link.startswith('http'):
        link = f'https://{link}'
    try:
        response = requests.get(link, headers=headers, timeout=timeout)
        if response.status_code == 200:
            with open('successful.txt', 'a') as f:
                f.write(link + '\n')
            print(
                f'TO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: HTTPS request successful')
            return
        else:
            with open('unsuccessful.txt', 'a') as f:
                f.write(
                    f'{link} – status code: {response.status_code}\n')
            print(
                f'TO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: HTTPS request failed with status code {response.status_code}')
            return

    except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout) as e:
        print(
            f'TO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: Request timed out')
        with open('unsuccessful.txt', 'a') as f:
            f.write(
                link + ' – Request timed out' + '\n')
            return

    except requests.exceptions.SSLError as e:
        cert = ssl.get_server_certificate((link.split('//')[1], 443))
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        # get issuer of the certificate
        issuer = x509.get_issuer().get_components()[2][1].decode()

        if any(untrust in issuer for untrust in untrusted):
            file_name = 'ssl_cert_err.txt'
            error_message = 'Russian affiliated certificate error'
        elif any(untrust in issuer for untrust in self_signed):
            file_name = 'ssl_self_sign_err.txt'
            error_message = 'Russian self signed certificate error'
        else:
            file_name = 'other_ssl_cert_err.txt'
            error_message = 'Other SSL certificate error'

        print(
            f'TO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: {error_message} – {issuer}')
        with open(file_name, 'a') as f:
            f.write(f'{link} – CA: {issuer}\n')
        return

    except (requests.exceptions.RequestException,
            ssl.SSLError, ssl.CertificateError,
            ssl.SSLError, ssl.SSLZeroReturnError,
            ssl.SSLWantReadError, ssl.SSLWantWriteError,
            ssl.SSLSyscallError, ssl.SSLEOFError,
            ssl.SSLCertVerificationError) as e:
        with open('request_errors.txt', 'a') as f:
            f.write(f'{link} – error: {e}\n')
        print(
            f'TO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: {e}')
        return

    except Exception as e:
        print(f'FATAL REQUEST ERROR: {link}')
        with open('request_errors.txt', 'a') as f:
            f.write(f'{link} FATAL ERROR: {e}\n')
        return


def process_batch(batch, timeout, batch_idx, total_batch):
    results = []
    thread_multiplier = 8
    with mp.Pool(mp.cpu_count() * thread_multiplier) as pool:
        for i, link in enumerate(batch):
            results.append(pool.apply_async(
                check_link, (link, i+1, batch, timeout, batch_idx, total_batch)))
        pool.close()
        pool.join()
    return results


def main():
    # Parse args
    parser = argparse.ArgumentParser(
        description='This script allows you to analyse which sites require a Russian Trusted CA certificate to work properly.')
    parser.add_argument('--timeout', default=15, type=int,
                        help='Timeout for each web request, in seconds.')
    parser.add_argument('--name', default='statistics.db', type=str,
                        help='Database name, if it does not exist - it will be created.')
    parser.add_argument('--updated', default=False,
                        help='Flag signalling that the dataset has been updated.')
    parser.add_argument('--delete', type=str,
                        help='Delete existed database with name.')
    args = parser.parse_args()

    # Check is db should be deleted
    need_to_del_db = args.delete
    db.need_to_del_db(need_to_del_db)

    # Get values for all args
    timeout = int(args.timeout)
    if args.timeout <= 0:
        print(f'WARN: provided timeout – {timeout} lees or equals to zero')
        sleep(3)
        timeout = 15
    db_name = args.name
    is_dataset_updated = args.updated

    common.delete_old_res()

    link_batches = common.read_links('tls_list_cleaned.txt')

    last_idx = len(link_batches)
    for idx, content in enumerate(link_batches):
        print(f'\nProcessing: {idx + 1}/{last_idx} batch')
        sleep(1)

        # process batch with multiprocessing
        results = process_batch(content, timeout + 1, idx + 1, last_idx)

        # process completed and not completed tasks
        for future in results:
            try:
                # get result of task (not used in this case)
                _ = future.get(timeout=timeout + 1)
            except Exception as e:
                print(f'Error: {e}')

    # Save results to sqlite database
    db.create_db_with_name(db_name)

    ssl_cert_err_filename = 'ssl_cert_err.txt'
    ssl_self_sign_err_filename = 'ssl_self_sign_err.txt'

    request_errors_filename = 'request_errors.txt'
    successful_request_filename = 'successful.txt'
    unsuccessful_requests_filename = 'unsuccessful.txt'

    trusted_count = common.count_strings_in_file(ssl_cert_err_filename)
    self_count = common.count_strings_in_file(ssl_self_sign_err_filename)
    total_ds_size = common.count_strings_in_file('tls_list_cleaned.txt')

    db.write_batch(db_name=db_name,
                   timeout=timeout,
                   total_ds_size=total_ds_size,
                   trusted_count=trusted_count,
                   self_count=self_count,
                   path_to_trusted=ssl_cert_err_filename,
                   path_to_self=ssl_self_sign_err_filename,
                   list_of_request_error=request_errors_filename,
                   list_of_successful=successful_request_filename,
                   list_of_unsuccessful=unsuccessful_requests_filename,
                   is_new_dataset=is_dataset_updated)
    print(f'Results successfully saved to db: {db_name}')


if __name__ == '__main__':

    sys.stdout = StdoutToLogger(logger)

    start_time = time()

    print('Starting analysis pipeline...')
    main()
    print('Analysis pipeline done')

    end_time = time()
    execution_time = end_time - start_time

    print(f'Execution time:\n\
        {execution_time:.2f} seconds,\n\
        {execution_time / 60:.2f} minutes, \n\
        {execution_time / 60 / 60:.2f} hours.')
