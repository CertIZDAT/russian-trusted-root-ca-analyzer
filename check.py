import argparse
import signal
from time import sleep, time

from utils import common, logger, analyser, db

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
        logger.logger.warning(
            f'WARN: provided timeout – {timeout} lees or equals to zero')
        sleep(3)
        timeout = 30

    global db_name
    db_name = args.name

    global is_dataset_updated
    is_dataset_updated = args.updated

    link_batches: tuple = (
        common.read_links('dataset/government_domains.txt'),
        common.read_links('dataset/social.txt'),
        common.read_links('dataset/top-100.txt'))

    analyser.run_pipeline(link_batches=link_batches)

    exit(0)

    ssl_cert_err_filename = 'ssl_cert_err.txt'
    ssl_self_sign_err_filename = 'ssl_self_sign_err.txt'
    ssl_other_cert_err_filename = 'other_ssl_cert_err.txt'

    # Save results to sqlite database
    db.create_db_with_name(db_name)
    db.save_res_to_db(db_name=db_name,
                      timeout=timeout,
                      trusted_ca_path=ssl_cert_err_filename,
                      self_sign_path=ssl_self_sign_err_filename,
                      other_ssl_err_path=ssl_other_cert_err_filename,
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
