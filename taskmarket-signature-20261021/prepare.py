#!/usr/bin/env python3
"""Download integrity-pinned public archives; extract only hash-locked source.
No tar filesystem extraction, package entrypoint imports, or account access.
"""
import argparse, base64, hashlib, io, json, os, pathlib, tarfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
LOCK = json.loads((ROOT / 'SOURCES.json').read_text())

def excerpt(text, role):
    if role == 'command':
        start = text.index('var setWithdrawalAddressCommand =')
        end = text.index('\n// src/commands/wallet/get-withdrawal-address.ts', start)
        return text[start:end].rstrip()
    needle = {'builder': 'function buildSetWithdrawalAddressMessage', 'signer': 'async function signMessage(', 'transport': 'async function apiPost(', 'idempotent': 'async function withIdempotentWrite(', 'validator': 'function isValidAddress('}[role]
    start = text.index(needle)
    return text[start:text.index('\n}', start) + 2]

def prepare(offline=False):
    os.umask(0o077)
    scratch = ROOT / '.scratch'
    scratch.mkdir(mode=0o700, exist_ok=True)
    for version, package in LOCK['packages'].items():
        archive = scratch / (version + '.tgz')
        if not archive.exists():
            if offline:
                raise RuntimeError('Missing cached archive: ' + version)
            with urllib.request.urlopen(package['url'], timeout=45) as response:
                archive.write_bytes(response.read(32 * 1024 * 1024))
        raw = archive.read_bytes()
        actual = 'sha512-' + base64.b64encode(hashlib.sha512(raw).digest()).decode()
        if actual != package['integrity']:
            raise RuntimeError('Archive integrity mismatch: ' + version)
        extracted = {}
        with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
            for role, source in package['sources'].items():
                body = tar.extractfile(source['member']).read()
                if hashlib.sha256(body).hexdigest() != source['sha256']:
                    raise RuntimeError('Member hash mismatch: ' + version + '/' + role)
                text = excerpt(body.decode('utf-8'), role)
                if hashlib.sha256(text.encode()).hexdigest() != source['excerptSha256']:
                    raise RuntimeError('Excerpt hash mismatch: ' + version + '/' + role)
                extracted[role] = text
        (scratch / (version + '-source.json')).write_text(json.dumps(extracted))
        print('verified actual source', version)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    prepare(parser.parse_args().offline)
