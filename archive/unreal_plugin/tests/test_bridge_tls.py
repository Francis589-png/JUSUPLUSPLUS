import subprocess
import sys
import socket
import json
import time
import os
from pathlib import Path

BRIDGE = Path('projects') / 'unreal_plugin' / 'jusu_unreal_bridge.py'
EXAMPLE_SCRIPT = Path('projects') / 'unreal_plugin' / 'examples' / 'platformer.jusu'


def gen_self_signed(cert_path: Path, key_path: Path):
    """Attempt to generate a self-signed cert using the cryptography package; fall back to openssl if needed."""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Example Org"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]), critical=False)
            .sign(key, hashes.SHA256())
        )

        # Write key
        key_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        cert_bytes = cert.public_bytes(serialization.Encoding.PEM)
        cert_path.write_bytes(cert_bytes)
        key_path.write_bytes(key_bytes)
        return True
    except Exception:
        # Fallback to openssl CLI if available
        try:
            subprocess.check_call(['openssl', 'req', '-x509', '-nodes', '-newkey', 'rsa:2048', '-days', '1', '-keyout', str(key_path), '-out', str(cert_path), '-subj', '/CN=localhost'])
            return True
        except Exception:
            return False


def test_bridge_tls_accepts_connection(tmp_path):
    ok = gen_self_signed(tmp_path / 'cert.pem', tmp_path / 'key.pem')
    if not ok:
        import pytest
        pytest.skip('Could not generate a self-signed cert (cryptography or openssl not available)')

    cert = tmp_path / 'cert.pem'
    key = tmp_path / 'key.pem'

    proc = subprocess.Popen([sys.executable, str(BRIDGE), '--port', '8893', '--tls-cert', str(cert), '--tls-key', str(key)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        time.sleep(0.5)
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(socket.socket(socket.AF_INET), server_hostname='localhost')
        s.connect(('127.0.0.1', 8893))
        req = {'cmd': 'run_script_path', 'script_path': str(EXAMPLE_SCRIPT)}
        s.sendall((json.dumps(req) + '\n').encode('utf-8'))
        data = s.recv(8192)
        s.close()
        resp = json.loads(data.decode('utf-8'))
        assert resp['ok']
    finally:
        proc.terminate()
        proc.wait(timeout=2)
