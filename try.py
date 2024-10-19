def compare_path(endpoint, path):
    endpoint = endpoint.lstrip('/').split('/')
    path = path.lstrip('/').split('/')

    if len(endpoint) != len(path):
        return False

    for i, j in zip(endpoint, path):
        if i[0] != '{' and i != j:
            return False

    return True

import datetime
import time
a=datetime.datetime.now(datetime.UTC)
time.sleep(10)
b=datetime.datetime.now(datetime.UTC)
print(b-a)
