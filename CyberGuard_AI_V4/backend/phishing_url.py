"""Lexical URL subset of the project's phishing feature schema."""
import ipaddress
from urllib.parse import urlsplit
from backend.real_inputs import inspect_url

FEATURES = ['UsingIP','LongURL','ShortURL','Symbol@','Redirecting//','PrefixSuffix-','HTTPSDomainURL']
SHORTENERS = {'bit.ly','tinyurl.com','t.co','is.gd','cutt.ly','ow.ly','rb.gy','goo.gl','buff.ly','rebrand.ly','tiny.cc','shorturl.at'}


def extract(url):
    inspect_url(url)  # Strict syntax validation, no requests or DNS.
    url = url.strip()
    parsed = urlsplit(url)
    host = parsed.hostname.lower().rstrip('.')
    try:
        ipaddress.ip_address(host)
        using_ip = -1
    except ValueError:
        using_ip = 1
    return {'UsingIP': using_ip, 'LongURL': 1 if len(url) < 54 else (0 if len(url) <= 75 else -1),
            'ShortURL': -1 if host in SHORTENERS else 1,
            'Symbol@': -1 if '@' in url else 1,
            'Redirecting//': -1 if url.rfind('//') > 7 else 1,
            'PrefixSuffix-': -1 if '-' in host else 1,
            'HTTPSDomainURL': -1 if 'https' in host else 1}
