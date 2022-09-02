import hashlib
from flask_bcrypt import (
    generate_password_hash
)

password = '1234'

# @TODO is used ? => to del
if __name__ == '__main__':

    password_hash = generate_password_hash(password.encode('utf-8')).decode('utf-8')

    print(password.encode('utf-8'))
    print(generate_password_hash(password.encode('utf-8')))
    print(password_hash)

    password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    print(password_md5)
