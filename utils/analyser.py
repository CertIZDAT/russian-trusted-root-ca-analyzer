import ssl

import requests
from OpenSSL import crypto

from utils import logger


def check_link(link, index, website_links, timeout, batch_idx, total_batch):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }

    untrusted = ['Russian Trusted']

    self_signed = ['SberCA', 'St. Petersburg', 'VTB Group', 'Bank GPB', 'Администрация Партизанского городского округа',
                   'Kaliningrad', 'Sigma-REZERV', 'Moscow', 'Stavrolop', 'Saint Petersburg', 'Petrozavodsk', 'Bryansk',
                   'sklif', 'SAMARA', 'Samara', 'SPb', 'Vladimir', 's-t-ORK', 'Donetsk', 'Karelia', 'favr.ru', 'Plesk',
                   'Stavropol']

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
            f'\n\tTO: {timeout}, B: {batch_idx}/{total_batch},\t{index}/{len(website_links)}:\t{link}: {error_message} – {issuer}')
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
