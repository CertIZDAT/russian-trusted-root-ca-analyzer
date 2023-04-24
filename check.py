import argparse
import signal
from time import sleep, time

from utils import common, db, logger, analyser

db_name: str = ''
timeout: int = 30
is_dataset_updated: bool = False


def main() -> None:
    # Register SIGINT signal handler
    signal.signal(signal.SIGINT, logger.signal_handler)

    # Parse args
    parser = argparse.ArgumentParser(
        description='This script allows you to analyse which sites require a Russian Trusted CA certificate to work '
                    'properly. Also script performs self-signed certificates checking.')
    parser.add_argument('--timeout', default=30, type=int,
                        help='Timeout for each web request, in seconds.')
    parser.add_argument('--name', default='statistics.db', type=str,
                        help='Database name, if it does not exist - it will be created.')
    parser.add_argument('--updated', default=False,
                        help='Flag signalling that the dataset has been updated.')
    args = parser.parse_args()

    # Get values for all args
    global timeout
    timeout = int(args.timeout)
    if args.timeout <= 0:
        logger.logger.warn(
            f'WARN: provided timeout – {timeout} lees or equals to zero')
        sleep(3)
        timeout = 30

    global db_name
    db_name = args.name

    global is_dataset_updated
    is_dataset_updated = args.updated

    link_batches: tuple = (common.read_links('dataset/govdomains.txt'),
                           common.read_links('dataset/social.txt'),
                           common.read_links('dataset/top-100.txt'))

    analyser.analyse(link_batches=link_batches)

    exit(0)
    # Save results to sqlite database
    db.create_db_with_name(db_name)

    total_ds_size = common.count_strings_in_file('tls_list_cleaned.txt')

    ssl_cert_err_filename = 'ssl_cert_err.txt'
    ssl_self_sign_err_filename = 'ssl_self_sign_err.txt'
    ssl_other_cert_err_filename = 'other_ssl_cert_err.txt'

    successful_request_filename = 'successful.txt'
    unsuccessful_requests_filename = 'unsuccessful.txt'
    request_errors_filename = 'request_errors.txt'

    trusted_count = common.count_strings_in_file(ssl_cert_err_filename)
    self_count = common.count_strings_in_file(ssl_self_sign_err_filename)
    other_ssl_count = common.count_strings_in_file(ssl_other_cert_err_filename)

    successful_count = common.count_strings_in_file(
        successful_request_filename)
    unsuccessful_count = common.count_strings_in_file(
        unsuccessful_requests_filename)
    error_count = common.count_strings_in_file(request_errors_filename)

    db.write_batch(db_name=db_name,
                   timeout=timeout,
                   total_ds_size=total_ds_size,
                   trusted_ca_count=trusted_count,
                   self_signed_count=self_count,
                   other_ssl_count=other_ssl_count,
                   successful_count=successful_count,
                   unsuccessful_count=unsuccessful_count,
                   error_count=error_count,
                   path_to_trusted=ssl_cert_err_filename,
                   path_to_self=ssl_self_sign_err_filename,
                   path_to_other_ssl=ssl_other_cert_err_filename,
                   path_to_successful=successful_request_filename,
                   path_to_unsuccessful=unsuccessful_requests_filename,
                   path_to_request_errors=request_errors_filename,
                   is_new_dataset=is_dataset_updated)
    logger.logger.info(f'Results successfully saved to db: {db_name}')


if __name__ == '__main__':
    start_time: float = time()

    logger.logger.info('Starting analysis pipeline...')
    main()
    logger.logger.info('Analysis pipeline done')

    end_time: float = time()
    execution_time: float = end_time - start_time

    logger.logger.info(f'Execution time:\n\
        {execution_time:.2f} seconds,\n\
        {execution_time / 60:.2f} minutes, \n\
        {execution_time / 60 / 60:.2f} hours.')
