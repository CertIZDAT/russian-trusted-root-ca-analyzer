import ssl
from os import path, mkdir, remove, listdir
from shutil import rmtree
from time import sleep

import requests
from OpenSSL import crypto

from check import timeout
from utils import threading
from utils.lists import UNTRUSTED_CERTS, SELF_SIGNED_CERTS, HEADER
from utils.logger import logger


# TODO: Add ability to parse links like https://онлайнинспекция.рф
def _get_root_cert(link: str):
    cert = ssl.get_server_certificate((link.split('//')[1], 443))
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert.encode())
    # FIXME: Fix cert chain detection
    # get issuer of the certificate
    return x509.get_issuer().get_components()[2][1].decode()

    # cert = ssl.get_server_certificate((link.split('//')[1], 443))
    # x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert.encode())
    # issuer_cert = x509.get_issuer()
    # issuer_name = issuer_cert.CN

    # print(f'i: {issuer_cert}')
    # print(f'CN: {issuer_cert.CN}')
    # print(f'C: {issuer_cert.C}')
    # print(f'commonName: {issuer_cert.commonName}')
    # print(f'L: {issuer_cert.L}')
    # print(f'localityName: {issuer_cert.localityName}')
    # print(f'O: {issuer_cert.O}')
    # print(f'orgUnitName: {issuer_cert.organizationalUnitName}')
    # print(f'orgName: {issuer_cert.organizationName}')
    # print(f'OU: {issuer_cert.OU}')
    # print(f'ST: {issuer_cert.ST}')
    # print(f'stateOrProvinceName: {issuer_cert.stateOrProvinceName}')

    # return issuer_name


def _check_link(source_link: str, index: int, website_links: list[str], batch_idx: int, total_batch: int) -> None:
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
    try:
        response = requests.get(link, headers=HEADER, timeout=timeout)
        if not response.status_code == 200:
            with open(f'{sub_path}/unsuccessful.txt', 'a') as f:
                f.write(
                    f'{link} – status code: {response.status_code}\n')
            logger.error(
                f'TO: {timeout}, B: {batch_idx}/{total_batch}, {index}/{len(website_links)} – {link}: HTTPS '
                f'request failed – code={response.status_code}\n')
            return

    except requests.exceptions.SSLError:
        issuer = _get_root_cert(link)

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


def run_pipeline(link_batches: tuple) -> None:
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

    tuple_idx: int = 1
    for tup in link_batches:
        print(f'Running at {tuple_idx} file')
        sleep(3)
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
                                                    total_batch=last_idx)

            # process completed and not completed tasks
            for future in results:
                try:
                    # get result of task (not used in this case)
                    _ = future.get()
                except Exception as e:
                    logger.error(f'Error: {e}')
        idx += 1
    tuple_idx += 1
