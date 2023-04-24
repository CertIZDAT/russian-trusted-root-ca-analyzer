import ssl
from time import sleep

import requests
from OpenSSL import crypto
from requests import Response

from utils import logger, threading, lists
from check import timeout


def _check_link(link: str, index: int, website_links, batch_idx: int, total_batch: int) -> None:
    untrusted: list[str] = lists.untrusted
    self_signed: list[str] = lists.self_signed

    link: str = link.strip()
    if link == '':
        return

    if not link.startswith('http'):
        link = f'https://{link}'
    try:
        response: Response = requests.get(link, headers=lists.headers, timeout=timeout)
        if response.status_code == 200:
            with open('successful.txt', 'a') as f:
                f.write(link + '\n')
            logger.logger.info(
                f'\n\tTO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: HTTPS '
                f'request successful')
            return
        else:
            with open('unsuccessful.txt', 'a') as f:
                f.write(
                    f'{link} – status code: {response.status_code}\n')
            logger.logger.info(
                f'\n\tTO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: HTTPS '
                f'request failed with status code {response.status_code}')
            return

    except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout):
        logger.logger.info(
            f'\n\tTO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: '
            f'Request timed out')
        with open('unsuccessful.txt', 'a') as f:
            f.write(
                link + ' – Request timed out' + '\n')
            return

    except requests.exceptions.SSLError as e:
        cert = ssl.get_server_certificate((link.split('//')[1], 443))
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert.encode())
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

        logger.logger.info(
            f'\n\tTO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: {error_message} '
            f'– {issuer}')
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
            f.write(f'{link} – error: {e}\n')
        logger.logger.info(
            f'\n\tTO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: {e}')
        return

    except Exception as e:
        logger.logger.info(f'FATAL REQUEST ERROR: {link}')
        with open('request_errors.txt', 'a') as f:
            f.write(f'{link} FATAL ERROR: {e}\n')
        return


def analyse(link_batches: tuple):
    last_idx: int = len(link_batches)
    idx: int = 0
    for tup in link_batches:
        for _, content in enumerate(tup):
            logger.logger.info(f'\nProcessing: {idx + 1}/{last_idx} batch')
            sleep(1)

            # process batch with multiprocessing
            results: list = threading.process_batch(target_func=_check_link,
                                                    batch=content,
                                                    batch_idx=idx + 1,
                                                    total_batch=last_idx)

            # process completed and not completed tasks
            for future in results:
                try:
                    # get result of task (not used in this case)
                    _ = future.get()
                except Exception as e:
                    logger.logger.error(f'Error: {e}')
        idx += 1
