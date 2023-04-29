import ssl
import subprocess
from os import path, mkdir, remove, listdir
from shutil import rmtree
from time import sleep
from urllib.parse import quote

import requests
from OpenSSL import crypto

from utils import threading
from utils.lists import UNTRUSTED_CERTS, SELF_SIGNED_CERTS, HEADER
from utils.logger import logger


def _deep_certificate_check(link: str, timeout: int):
    link = link.split('//')[1]
    echo_command = 'echo Q'
    openssl_command = f'openssl s_client -showcerts -verify 15 -connect {link}:443 -servername {link}'
    echo_output = subprocess.check_output(echo_command, shell=True,
                                          stderr=subprocess.DEVNULL,
                                          universal_newlines=True)
    openssl_output = subprocess.check_output(openssl_command, shell=True, input=echo_output,
                                             stderr=subprocess.DEVNULL, universal_newlines=True, timeout=timeout)

    for line in openssl_output.split('\n'):
        if UNTRUSTED_CERTS[0] in line:
            return True
        else:
            return False


def _get_root_cert(link: str) -> str:
    cert = ssl.get_server_certificate((link.split('//')[1], 443))
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert.encode())
    return x509.get_issuer().get_components()[2][1].decode()


def _check_link(source_link: str, index: int, website_links: list[str], batch_idx: int, total_batch: int,
                timeout: int) -> None:
    if batch_idx == 1:
        sub_path: str = path.join('results/', 'government')
    elif batch_idx == 2:
        sub_path: str = path.join('results/', 'social')
    elif batch_idx == 3:
        sub_path: str = path.join('results/', 'top')
    else:
        logger.error(f'FATAL batch_idx error! idx = {batch_idx}')
        exit(1)

    trusted_ca_path: str = f'{sub_path}/russian_trusted_ca.txt'
    self_sign_path: str = f'{sub_path}/ru_self_sign.txt'
    other_ssl_err_path: str = f'{sub_path}/other_ssl_err.txt'
    timeout_err_path: str = f'{sub_path}/timeout_err.txt'
    request_err_path: str = f'{sub_path}/request_errors.txt'

    link: str = source_link.strip()
    if link == '':
        return

    if not link.startswith('http'):
        link = f'https://{link}'

    old_link: str = link
    if link.isascii():
        link = quote(link, safe=':/')

    try:
        response = requests.get(link, headers=HEADER, timeout=timeout)
        if not response.status_code == 200:
            with open(f'{sub_path}/unsuccessful.txt', 'a') as f:
                f.write(
                    f'{link} – status code: {response.status_code}\n')
            logger.error(
                f'TO: {timeout}, B: {batch_idx}/{total_batch}, {index}/{len(website_links)} – {old_link}: HTTPS '
                f'request failed – code={response.status_code}\n')
            return

    except requests.exceptions.SSLError:
        issuer = _get_root_cert(link)
        if issuer not in UNTRUSTED_CERTS:
            if _deep_certificate_check(link, timeout):
                issuer = UNTRUSTED_CERTS[0] + ' No-Snig'

        if any(cert in issuer for cert in UNTRUSTED_CERTS):
            file_name: str = trusted_ca_path
            error_message: str = 'Russian affiliated certificate error'
        elif any(cert in issuer for cert in SELF_SIGNED_CERTS):
            file_name: str = self_sign_path
            error_message: str = 'Russian self signed certificate error'
        else:
            file_name: str = other_ssl_err_path
            error_message: str = 'Other SSL certificate error'

        logger.info(
            f'TO: {timeout}, B: {batch_idx}/{total_batch}, {index}/{len(website_links)} – {link}: {error_message} '
            f'– {issuer}\n')
        with open(file_name, 'a') as f:
            f.write(f'{link} – CA: {issuer}\n')
        return

    except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout):
        logger.error(
            f'TO: {timeout}, B: {batch_idx}/{total_batch}, {index}/{len(website_links)} – {link}: '
            f'Request timed out\n')
        with open(timeout_err_path, 'a') as f:
            f.write(
                link + ' – Request timed out' + '\n')
            return

    except Exception as e:
        with open(request_err_path, 'a') as f:
            f.write(f'{link} – request error: {e}\n')
        logger.error(f'{link} – request error')
        return


def run_pipeline(link_batches: tuple, timeout: int) -> None:
    last_idx: int = len(link_batches)
    idx: int = 0

    if path.exists('results'):
        for content in listdir('results/'):
            content_path = path.join('results/', content)
            if path.isfile(content_path):
                remove(content_path)
            else:
                rmtree(content_path, ignore_errors=True)
    else:
        mkdir('results')

    mkdir('results/government')
    mkdir('results/social')
    mkdir('results/top')

    for tup in link_batches:
        for _, content in enumerate(tup):
            logger.info(f'\nProcessing: {idx + 1}/{last_idx} batch')
            sleep(1)

            # process batch with multiprocessing
            results: list = threading.process_batch(target_func=_check_link,
                                                    batch=content,
                                                    # idx == 1 means government associated sites
                                                    # idx == 2 means social list sites
                                                    # idx == 3 means top-100 sites
                                                    batch_idx=idx + 1,
                                                    total_batch=last_idx,
                                                    timeout=timeout)

            # process completed and not completed tasks
            for future in results:
                try:
                    # get result of task (not used in this case)
                    _ = future.get()
                except Exception as e:
                    logger.error(f'Error: {e}')
        idx += 1
