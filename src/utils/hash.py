import hashlib


def file_hash(path: str) -> str:
    h = hashlib.sha3_256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

