import ssl
from os import mkdir, path
from time import sleep
from urllib.parse import quote, urlparse

from OpenSSL import crypto

from utils import threading
from utils.common import clean_logs_directory, clean_results_directory
from utils.cert_references import SELF_SIGNED_CERTS, UNTRUSTED_CERTS
from utils.logger import logger


def __get_root_cert(link: str, timeout: int):
    parsed_url = urlparse(link)
    hostname = parsed_url.netloc
    cert = ssl.get_server_certificate((hostname, 443), timeout=timeout)
    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert.encode())
    return x509.get_issuer().get_components()[2][1].decode()


def __check_link(source_link: str, index: int, website_links: list[str], batch_idx: int, total_batch: int,
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


    link: str = source_link.strip()
    if link == '':
        return

    if not link.startswith('http'):
        link = f'https://{link}'

    if not link.isascii():
        link = quote(link, safe=':/')

    issuer = __get_root_cert(link, timeout=timeout)

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
        f.write(f'{link} – CA: {issuer} – ({error_message})')
    return


def run_pipeline(link_batches: tuple, timeout: int) -> None:
    last_idx: int = len(link_batches)
    idx: int = 0

    clean_results_directory()
    clean_logs_directory()

    mkdir('results/government')
    mkdir('results/social')
    mkdir('results/top')

    for tup in link_batches:
        for _, content in enumerate(tup):
            logger.info(f'\nProcessing: {idx + 1}/{last_idx} batch')
            sleep(1)

            # process batch with multiprocessing
            results: list = threading.process_batch(target_func=__check_link,
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
