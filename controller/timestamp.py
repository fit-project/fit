import os

# requires libeay.dll (openssl)
PATH_TO_FILE = 'path/to/file'
PATH_TO_TIMESTAMP = 'path/to/file.ots'


# Apply timestamp
command = "ots stamp " + PATH_TO_FILE
os.system(command)

# Verify timestamp, doc states that it takes a few hours for the blockchain to confirm the timestamp
command = 'ots verify ' + PATH_TO_TIMESTAMP
os.system(command)