from utils import db
from utils import support

db_name = 'test.db'
db.create_db_with_name(db_name)

ssl_cert_err_filename = 'ssl_cert_err.txt'
ssl_self_sign_err_filename = 'ssl_self_sign_err.txt'

trusted_count = support.count_strings_in_file(ssl_cert_err_filename)
self_count = support.count_strings_in_file(ssl_self_sign_err_filename)

db.write_batch(db_name, trusted_count, self_count,
               ssl_cert_err_filename, ssl_self_sign_err_filename, is_new_dataset=False)
