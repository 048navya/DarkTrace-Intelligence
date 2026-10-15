"""Authorized fixed-URL collector. No discovery, recursive crawling or active probing."""
import hashlib
import ipaddress
import json
import os
import re
import socket
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit
import requests
from bs4 import BeautifulSoup

MAX_BYTES = 1_000_000

def validate_url(url, allowed_hosts, tor=False):
    u = urlsplit(url)
    if u.username or u.password or u.fragment or not u.hostname:
        raise ValueError('Credentials/fragments are not allowed in source URLs')
    if u.hostname not in allowed_hosts:
        raise ValueError('Source hostname is not in the collector allowlist')
    if tor:
        if not re.fullmatch(r'[a-z2-7]{56}\.onion', u.hostname) or u.scheme not in ('http', 'https') or u.port:
            raise ValueError('Expected an approved v3 onion URL')
    else:
        if u.scheme != 'https' or (u.port and u.port != 443):
            raise ValueError('HTTPS on port 443 is required')
        addresses = socket.getaddrinfo(u.hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise ValueError('Publicly routable source addresses are required')
    return u

def html_record(html, url, headers):
    soup = BeautifulSoup(html, 'html.parser')
    for element in soup(['script', 'style', 'noscript']):
        element.decompose()
    # Capture the authorized page, not guessed personal identities.
    text = soup.get_text(' ', strip=True)[:12000]
    title = soup.title.get_text(' ', strip=True) if soup.title else urlsplit(url).hostname
    title = (title or 'Authorized source')[:100]
    wallets = sorted(set(re.findall(r'\b0x[a-fA-F0-9]{40}\b', text)))[:20]
    # PGP fingerprints must be explicitly labeled; raw key blocks are not guessed.
    pgp = re.findall(r'(?i)fingerprint\s*[:=]\s*((?:[a-f0-9]{4}\s*){10})', text)
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    indicators = []
    if headers.get('Server'):
        indicators.append({'type': 'banner', 'value': headers['Server'][:300]})
    return {'id': 'page-' + hashlib.sha256(url.encode()).hexdigest()[:24], 'handle': title,
            'platform': urlsplit(url).hostname[:100], 'category': 'Other', 'observedAt': now,
            'text': text, 'wallets': wallets, 'pgp': [re.sub(r'\s', '', p).upper() for p in pgp][:20],
            'trusts': [], 'service': urlsplit(url).hostname, 'indicators': indicators,
            'entityLead': '', 'synthetic': False}

def collect(job, allowed_hosts, tor_proxy, session=None):
    is_tor = job['adapter'].startswith('tor')
    validate_url(job['url'], allowed_hosts, is_tor)
    if is_tor and not tor_proxy.startswith('socks5h://'):
        raise ValueError('Tor requires a socks5h proxy for remote DNS')
    session = session or requests.Session()
    session.trust_env = False
    proxies = {'http': tor_proxy, 'https': tor_proxy} if is_tor else {}
    deadline = time.monotonic() + 60
    with session.get(job['url'], timeout=(15, 20), allow_redirects=False, stream=True,
                     proxies=proxies, headers={'User-Agent': 'DarkTrace-Authorized-Collector/2.0', 'Accept': 'application/json, text/html'}) as response:
        if response.status_code != 200:
            raise ValueError('Source returned HTTP ' + str(response.status_code))
        chunks, size = [], 0
        for chunk in response.iter_content(16384):
            size += len(chunk)
            if size > MAX_BYTES or time.monotonic() > deadline:
                raise ValueError('Source byte/time limit exceeded')
            chunks.append(chunk)
        body = b''.join(chunks).decode('utf-8', errors='replace')
        if job['adapter'] == 'tor-html':
            return [html_record(body, job['url'], response.headers)]
        records = json.loads(body)
        if not isinstance(records, list) or len(records) > 100:
            raise ValueError('JSON source must be an array with at most 100 records')
        return records

def run(once=False):
    base = os.environ['DARKTRACE_URL'].rstrip('/')
    token = os.environ['DARKTRACE_JOB_TOKEN']
    if not base.startswith('https://') or len(token) < 32:
        raise ValueError('Use a trusted HTTPS app URL and a job token of at least 32 characters')
    allowed = {s.strip().lower() for s in os.environ.get('COLLECTOR_ALLOWED_HOSTS', '').split(',') if s.strip()}
    headers = {'x-darktrace-job-token': token}
    if os.environ.get('OAI_SITES_SERVICE_TOKEN'):
        headers['OAI-Sites-Authorization'] = 'Bearer ' + os.environ['OAI_SITES_SERVICE_TOKEN']
    session = requests.Session()
    def post(payload):
        response = session.post(base + '/api/runner', json=payload, headers=headers, timeout=(15, 90), allow_redirects=False)
        response.raise_for_status()
        return response.json()
    while True:
        try:
            jobs = post({'action': 'claim'})['jobs']
            for job in jobs:
                records, error = None, None
                try:
                    records = collect(job, allowed, os.environ.get('TOR_PROXY', 'socks5h://127.0.0.1:9050'))
                except Exception as exc:
                    error = str(exc)[:1000]
                result = post({'action': 'finish', 'sourceId': job['source_id'], 'leaseToken': job['lease_token'], 'records': records, 'error': error})
                print(json.dumps({'sourceId': job['source_id'], 'status': result['status'], 'count': result['count']}), flush=True)
        except Exception as exc:
            # Do not log configured tokens or request headers.
            print(json.dumps({'status': 'runner-error', 'type': type(exc).__name__}), flush=True)
        if once:
            break
        time.sleep(30)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    run(args.once)
