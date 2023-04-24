import ssl
from time import sleep

import requests
from OpenSSL import crypto
from requests import Response

from check import timeout
from utils import logger, threading, lists


def _check_link(link: str, index: int, website_links: list[str], batch_idx: int, total_batch: int) -> None:
    untrusted: list[str] = lists.untrusted
    self_signed: list[str] = lists.self_signed

    link: str = link.strip()
    if link == '':
        return

    if not link.startswith('http'):
        link = f'https://{link}'
    try:
        response: Response = requests.get(link, headers=lists.headers, timeout=timeout)
        if not response.status_code == 200:
            with open('unsuccessful.txt', 'a') as f:
                f.write(
                    f'{link} – status code: {response.status_code}\n')
            logger.logger.info(
                f'TO: {timeout}, B: {batch_idx}/{total_batch}, {index}/{len(website_links)} – {link}: HTTPS '
                f'request failed – code={response.status_code}\n')
            return

    except requests.exceptions.SSLError:
        cert = ssl.get_server_certificate((link.split('//')[1], 443))
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert.encode())
        # get issuer of the certificate
        issuer = x509.get_issuer().get_components()[2][1].decode()

        if any(untrust in issuer for untrust in untrusted):
            file_name = 'russian_trusted_ca.txt'
            error_message = 'Russian affiliated certificate error'
        elif any(untrust in issuer for untrust in self_signed):
            file_name = 'ru_self_sign.txt'
            error_message = 'Russian self signed certificate error'
        else:
            file_name = 'other_ssl_err.txt'
            error_message = 'Other SSL certificate error'

        logger.logger.info(
            f'TO: {timeout}, B: {batch_idx}/{total_batch}, {index}/{len(website_links)} – {link}: {error_message} '
            f'– {issuer}\n')
        with open(file_name, 'a') as f:
            f.write(f'{link} – CA: {issuer}\n')
        return

    except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout):
        logger.logger.info(
            f'TO: {timeout}, B: {batch_idx}/{total_batch}, {index}/{len(website_links)} – {link}: '
            f'Request timed out\n')
        with open('unsuccessful.txt', 'a') as f:
            f.write(
                link + ' – Request timed out' + '\n')
            return

    except Exception as e:
        with open('request_errors.txt', 'a') as f:
            f.write(f'{link} – request error: {e}\n')
        logger.logger.error(f'{link} – request errors: {e}')
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
