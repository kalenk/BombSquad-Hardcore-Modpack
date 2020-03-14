__revision__ = "$Id$"

import string, re

try:
    _unicode = unicode
except NameError:
    class _unicode(object):
        pass

__all__ = ['TextWrapper', 'wrap', 'fill', 'dedent']
_whitespace = '\t\n\x0b\x0c\r '

class TextWrapper:
    whitespace_trans = string.maketrans(_whitespace, ' ' * len(_whitespace))

    unicode_whitespace_trans = {}
    uspace = ord(u' ')
    for x in map(ord, _whitespace):
        unicode_whitespace_trans[x] = uspace
    wordsep_re = re.compile(
        r'(\s+|'                                  # any whitespace
        r'[^\s\w]*\w+[^0-9\W]-(?=\w+[^0-9\W])|'   # hyphenated words
        r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))')   # em-dash
    wordsep_simple_re = re.compile(r'(\s+)')
    sentence_end_re = re.compile(r'[%s]'              # lowercase letter
                                 r'[\.\!\?]'          # sentence-ending punct.
                                 r'[\"\']?'           # optional end-of-quote
                                 r'\Z'                # end of chunk
                                 % string.lowercase)


    def __init__(self,
                 width=70,
                 initial_indent="",
                 subsequent_indent="",
                 expand_tabs=True,
                 replace_whitespace=True,
                 fix_sentence_endings=False,
                 break_long_words=True,
                 drop_whitespace=True,
                 break_on_hyphens=True):
        self.width = width
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.expand_tabs = expand_tabs
        self.replace_whitespace = replace_whitespace
        self.fix_sentence_endings = fix_sentence_endings
        self.break_long_words = break_long_words
        self.drop_whitespace = drop_whitespace
        self.break_on_hyphens = break_on_hyphens
        self.wordsep_re_uni = re.compile(self.wordsep_re.pattern, re.U)
        self.wordsep_simple_re_uni = re.compile(
            self.wordsep_simple_re.pattern, re.U)

    def _munge_whitespace(self, text):
        if self.expand_tabs:
            text = text.expandtabs()
        if self.replace_whitespace:
            if isinstance(text, str):
                text = text.translate(self.whitespace_trans)
            elif isinstance(text, _unicode):
                text = text.translate(self.unicode_whitespace_trans)
        return text


    def _split(self, text):
        if isinstance(text, _unicode):
            if self.break_on_hyphens:
                pat = self.wordsep_re_uni
            else:
                pat = self.wordsep_simple_re_uni
        else:
            if self.break_on_hyphens:
                pat = self.wordsep_re
            else:
                pat = self.wordsep_simple_re
        chunks = pat.split(text)
        chunks = filter(None, chunks)  # remove empty chunks
        return chunks

    def _fix_sentence_endings(self, chunks):
        i = 0
        patsearch = self.sentence_end_re.search
        while i < len(chunks)-1:
            if chunks[i+1] == " " and patsearch(chunks[i]):
                chunks[i+1] = "  "
                i += 2
            else:
                i += 1

    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        if width < 1:
            space_left = 1
        else:
            space_left = width - cur_len
        if self.break_long_words:
            cur_line.append(reversed_chunks[-1][:space_left])
            reversed_chunks[-1] = reversed_chunks[-1][space_left:]
        elif not cur_line:
            cur_line.append(reversed_chunks.pop())

    def _wrap_chunks(self, chunks):
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        chunks.reverse()

        while chunks:
            cur_line = []
            cur_len = 0
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = len(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            # If the last chunk on this line is all whitespace, drop it.
            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                del cur_line[-1]

            # Convert current line back to a string and store it in list
            # of all lines (return value).
            if cur_line:
                lines.append(indent + ''.join(cur_line))

        return lines

    def wrap(self, text):
        text = self._munge_whitespace(text)
        chunks = self._split(text)
        if self.fix_sentence_endings:
            self._fix_sentence_endings(chunks)
        return self._wrap_chunks(chunks)

    def fill(self, text):
        """fill(text : string) -> string

        Reformat the single paragraph in 'text' to fit in lines of no
        more than 'self.width' columns, and return a new string
        containing the entire wrapped paragraph.
        """
        return "\n".join(self.wrap(text))


# -- Convenience interface ---------------------------------------------

def wrap(text, width=70, **kwargs):
    w = TextWrapper(width=width, **kwargs)
    return w.wrap(text)

def fill(text, width=70, **kwargs):
    w = TextWrapper(width=width, **kwargs)
    return w.fill(text)


# -- Loosely related functionality -------------------------------------

_whitespace_only_re = re.compile('^[ \t]+$', re.MULTILINE)
_leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)

def dedent(text):
    margin = None
    text = _whitespace_only_re.sub('', text)
    indents = _leading_whitespace_re.findall(text)
    for indent in indents:
        if margin is None:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner is still on top).
        elif indent.startswith(margin):
            pass

        # Current line consistent with and no deeper than previous winner:
        # it's the new winner.
        elif margin.startswith(indent):
            margin = indent

        # Find the largest common whitespace between current line and previous
        # winner.
        else:
            for i, (x, y) in enumerate(zip(margin, indent)):
                if x != y:
                    margin = margin[:i]
                    break
            else:
                margin = margin[:len(indent)]

    # sanity check (testing/debugging only)
    if 0 and margin:
        for line in text.split("\n"):
            assert not line or line.startswith(margin), \
                   "line = %r, margin = %r" % (line, margin)

    if margin:
        text = re.sub(r'(?m)^' + margin, '', text)
    return text

import re
import sys
import os
from collections import namedtuple
from contextlib import closing

import _ssl             # if we can't import it, let the error propagate

from _ssl import OPENSSL_VERSION_NUMBER, OPENSSL_VERSION_INFO, OPENSSL_VERSION
from _ssl import _SSLContext
from _ssl import (
    SSLError, SSLZeroReturnError, SSLWantReadError, SSLWantWriteError,
    SSLSyscallError, SSLEOFError,
    )
from _ssl import CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
from _ssl import txt2obj as _txt2obj, nid2obj as _nid2obj
from _ssl import RAND_status, RAND_add
try:
    from _ssl import RAND_egd
except ImportError:
    pass

def _import_symbols(prefix):
    for n in dir(_ssl):
        if n.startswith(prefix):
            globals()[n] = getattr(_ssl, n)

# some changes for compilator
try:
    from _ssl import OP_NO_SSLv2, OP_NO_SSLv3, OP_NO_TLSv1, OP_NO_TLSv1_1, PROTOCOL_SSLv23, \
        PROTOCOL_SSLv3, PROTOCOL_TLSv1, PROTOCOL_TLSv1_1, PROTOCOL_TLSv1_2, SSL_ERROR_EOF, \
        SSL_ERROR_INVALID_ERROR_CODE, SSL_ERROR_SSL, SSL_ERROR_SYSCALL, SSL_ERROR_WANT_CONNECT, \
        SSL_ERROR_WAND_READ, SSL_ERROR_WANT_WRITE, SSL_ERROR_WANT_X509_LOOKUP, SSL_ERROR_ZERO_RETURN
except ImportError: pass

_import_symbols('OP_')
_import_symbols('ALERT_DESCRIPTION_')
_import_symbols('SSL_ERROR_')
_import_symbols('PROTOCOL_')
_import_symbols('VERIFY_')

from _ssl import HAS_SNI, HAS_ECDH, HAS_NPN, HAS_ALPN

from _ssl import _OPENSSL_API_VERSION

_PROTOCOL_NAMES = {value: name for name, value in globals().items() if name.startswith('PROTOCOL_')}

try:
    _SSLv2_IF_EXISTS = PROTOCOL_SSLv2
except NameError:
    _SSLv2_IF_EXISTS = None

from socket import socket, _fileobject, _delegate_methods, error as socket_error
if sys.platform == "win32":
    from _ssl import enum_certificates, enum_crls

from socket import socket, AF_INET, SOCK_STREAM, create_connection
from socket import SOL_SOCKET, SO_TYPE
import base64        # for DER-to-PEM translation
import errno
import warnings

if _ssl.HAS_TLS_UNIQUE:
    CHANNEL_BINDING_TYPES = ['tls-unique']
else:
    CHANNEL_BINDING_TYPES = []

# Disable weak or insecure ciphers by default
# (OpenSSL's default setting is 'DEFAULT:!aNULL:!eNULL')
# Enable a better set of ciphers by default
# This list has been explicitly chosen to:
#   * Prefer cipher suites that offer perfect forward secrecy (DHE/ECDHE)
#   * Prefer ECDHE over DHE for better performance
#   * Prefer any AES-GCM over any AES-CBC for better performance and security
#   * Then Use HIGH cipher suites as a fallback
#   * Then Use 3DES as fallback which is secure but slow
#   * Disable NULL authentication, NULL encryption, and MD5 MACs for security
#     reasons
_DEFAULT_CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)

# Restricted and more secure ciphers for the server side
# This list has been explicitly chosen to:
#   * Prefer cipher suites that offer perfect forward secrecy (DHE/ECDHE)
#   * Prefer ECDHE over DHE for better performance
#   * Prefer any AES-GCM over any AES-CBC for better performance and security
#   * Then Use HIGH cipher suites as a fallback
#   * Then Use 3DES as fallback which is secure but slow
#   * Disable NULL authentication, NULL encryption, MD5 MACs, DSS, and RC4 for
#     security reasons
_RESTRICTED_SERVER_CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5:!DSS:!RC4'
)


class CertificateError(ValueError):
    pass


def _dnsname_match(dn, hostname, max_wildcards=1):
    """Matching according to RFC 6125, section 6.4.3

    http://tools.ietf.org/html/rfc6125#section-6.4.3
    """
    pats = []
    if not dn:
        return False

    pieces = dn.split(r'.')
    leftmost = pieces[0]
    remainder = pieces[1:]

    wildcards = leftmost.count('*')
    if wildcards > max_wildcards:
        # Issue #17980: avoid denials of service by refusing more
        # than one wildcard per fragment.  A survery of established
        # policy among SSL implementations showed it to be a
        # reasonable choice.
        raise CertificateError(
            "too many wildcards in certificate DNS name: " + repr(dn))

    # speed up common case w/o wildcards
    if not wildcards:
        return dn.lower() == hostname.lower()

    # RFC 6125, section 6.4.3, subitem 1.
    # The client SHOULD NOT attempt to match a presented identifier in which
    # the wildcard character comprises a label other than the left-most label.
    if leftmost == '*':
        # When '*' is a fragment by itself, it matches a non-empty dotless
        # fragment.
        pats.append('[^.]+')
    elif leftmost.startswith('xn--') or hostname.startswith('xn--'):
        # RFC 6125, section 6.4.3, subitem 3.
        # The client SHOULD NOT attempt to match a presented identifier
        # where the wildcard character is embedded within an A-label or
        # U-label of an internationalized domain name.
        pats.append(re.escape(leftmost))
    else:
        # Otherwise, '*' matches any dotless string, e.g. www*
        pats.append(re.escape(leftmost).replace(r'\*', '[^.]*'))

    # add the remaining fragments, ignore any wildcards
    for frag in remainder:
        pats.append(re.escape(frag))

    pat = re.compile(r'\A' + r'\.'.join(pats) + r'\Z', re.IGNORECASE)
    return pat.match(hostname)


def match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 and RFC 6125
    rules are followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    if not cert:
        raise ValueError("empty or no certificate, match_hostname needs a "
                         "SSL socket or SSL context with either "
                         "CERT_OPTIONAL or CERT_REQUIRED")
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_match(value, hostname):
                return
            dnsnames.append(value)
    if not dnsnames:
        # The subject is only checked when there is no dNSName entry
        # in subjectAltName
        for sub in cert.get('subject', ()):
            for key, value in sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                if key == 'commonName':
                    if _dnsname_match(value, hostname):
                        return
                    dnsnames.append(value)
    if len(dnsnames) > 1:
        raise CertificateError("hostname %r "
            "doesn't match either of %s"
            % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError("hostname %r "
            "doesn't match %r"
            % (hostname, dnsnames[0]))
    else:
        raise CertificateError("no appropriate commonName or "
            "subjectAltName fields were found")


DefaultVerifyPaths = namedtuple("DefaultVerifyPaths",
    "cafile capath openssl_cafile_env openssl_cafile openssl_capath_env "
    "openssl_capath")

def get_default_verify_paths():
    """Return paths to default cafile and capath.
    """
    parts = _ssl.get_default_verify_paths()

    # environment vars shadow paths
    cafile = os.environ.get(parts[0], parts[1])
    capath = os.environ.get(parts[2], parts[3])

    return DefaultVerifyPaths(cafile if os.path.isfile(cafile) else None,
                              capath if os.path.isdir(capath) else None,
                              *parts)


class _ASN1Object(namedtuple("_ASN1Object", "nid shortname longname oid")):
    """ASN.1 object identifier lookup
    """
    __slots__ = ()

    def __new__(cls, oid):
        return super(_ASN1Object, cls).__new__(cls, *_txt2obj(oid, name=False))

    @classmethod
    def fromnid(cls, nid):
        """Create _ASN1Object from OpenSSL numeric ID
        """
        return super(_ASN1Object, cls).__new__(cls, *_nid2obj(nid))

    @classmethod
    def fromname(cls, name):
        """Create _ASN1Object from short name, long name or OID
        """
        return super(_ASN1Object, cls).__new__(cls, *_txt2obj(name, name=True))


class Purpose(_ASN1Object):
    """SSLContext purpose flags with X509v3 Extended Key Usage objects
    """

Purpose.SERVER_AUTH = Purpose('1.3.6.1.5.5.7.3.1')
Purpose.CLIENT_AUTH = Purpose('1.3.6.1.5.5.7.3.2')


class SSLContext(_SSLContext):
    """An SSLContext holds various SSL-related configuration options and
    data, such as certificates and possibly a private key."""

    __slots__ = ('protocol', '__weakref__')
    _windows_cert_stores = ("CA", "ROOT")

    def __new__(cls, protocol, *args, **kwargs):
        self = _SSLContext.__new__(cls, protocol)
        if protocol != _SSLv2_IF_EXISTS:
            self.set_ciphers(_DEFAULT_CIPHERS)
        return self

    def __init__(self, protocol):
        self.protocol = protocol

    def wrap_socket(self, sock, server_side=False,
                    do_handshake_on_connect=True,
                    suppress_ragged_eofs=True,
                    server_hostname=None):
        return SSLSocket(sock=sock, server_side=server_side,
                         do_handshake_on_connect=do_handshake_on_connect,
                         suppress_ragged_eofs=suppress_ragged_eofs,
                         server_hostname=server_hostname,
                         _context=self)

    def set_npn_protocols(self, npn_protocols):
        protos = bytearray()
        for protocol in npn_protocols:
            b = protocol.encode('ascii')
            if len(b) == 0 or len(b) > 255:
                raise SSLError('NPN protocols must be 1 to 255 in length')
            protos.append(len(b))
            protos.extend(b)

        self._set_npn_protocols(protos)

    def set_alpn_protocols(self, alpn_protocols):
        protos = bytearray()
        for protocol in alpn_protocols:
            b = protocol.encode('ascii')
            if len(b) == 0 or len(b) > 255:
                raise SSLError('ALPN protocols must be 1 to 255 in length')
            protos.append(len(b))
            protos.extend(b)

        self._set_alpn_protocols(protos)

    def _load_windows_store_certs(self, storename, purpose):
        certs = bytearray()
        try:
            for cert, encoding, trust in enum_certificates(storename):
                # CA certs are never PKCS#7 encoded
                if encoding == "x509_asn":
                    if trust is True or purpose.oid in trust:
                        certs.extend(cert)
        except OSError:
            warnings.warn("unable to enumerate Windows certificate store")
        if certs:
            self.load_verify_locations(cadata=certs)
        return certs

    def load_default_certs(self, purpose=Purpose.SERVER_AUTH):
        if not isinstance(purpose, _ASN1Object):
            raise TypeError(purpose)
        if sys.platform == "win32":
            for storename in self._windows_cert_stores:
                self._load_windows_store_certs(storename, purpose)
        self.set_default_verify_paths()


def create_default_context(purpose=Purpose.SERVER_AUTH, cafile=None,
                           capath=None, cadata=None):
    """Create a SSLContext object with default settings.

    NOTE: The protocol and settings may change anytime without prior
          deprecation. The values represent a fair balance between maximum
          compatibility and security.
    """
    if not isinstance(purpose, _ASN1Object):
        raise TypeError(purpose)

    context = SSLContext(PROTOCOL_SSLv23)

    # SSLv2 considered harmful.
    context.options |= OP_NO_SSLv2

    # SSLv3 has problematic security and is only required for really old
    # clients such as IE6 on Windows XP
    context.options |= OP_NO_SSLv3

    # disable compression to prevent CRIME attacks (OpenSSL 1.0+)
    context.options |= getattr(_ssl, "OP_NO_COMPRESSION", 0)

    if purpose == Purpose.SERVER_AUTH:
        # verify certs and host name in client mode
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = True
    elif purpose == Purpose.CLIENT_AUTH:
        # Prefer the server's ciphers by default so that we get stronger
        # encryption
        context.options |= getattr(_ssl, "OP_CIPHER_SERVER_PREFERENCE", 0)

        # Use single use keys in order to improve forward secrecy
        context.options |= getattr(_ssl, "OP_SINGLE_DH_USE", 0)
        context.options |= getattr(_ssl, "OP_SINGLE_ECDH_USE", 0)

        # disallow ciphers with known vulnerabilities
        context.set_ciphers(_RESTRICTED_SERVER_CIPHERS)

    if cafile or capath or cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elif context.verify_mode != CERT_NONE:
        # no explicit cafile, capath or cadata but the verify mode is
        # CERT_OPTIONAL or CERT_REQUIRED. Let's try to load default system
        # root CA certificates for the given purpose. This may fail silently.
        context.load_default_certs(purpose)
    return context

def _create_unverified_context(protocol=PROTOCOL_SSLv23, cert_reqs=None,
                           check_hostname=False, purpose=Purpose.SERVER_AUTH,
                           certfile=None, keyfile=None,
                           cafile=None, capath=None, cadata=None):
    """Create a SSLContext object for Python stdlib modules

    All Python stdlib modules shall use this function to create SSLContext
    objects in order to keep common settings in one place. The configuration
    is less restrict than create_default_context()'s to increase backward
    compatibility.
    """
    if not isinstance(purpose, _ASN1Object):
        raise TypeError(purpose)

    context = SSLContext(protocol)
    # SSLv2 considered harmful.
    context.options |= OP_NO_SSLv2
    # SSLv3 has problematic security and is only required for really old
    # clients such as IE6 on Windows XP
    context.options |= OP_NO_SSLv3

    if cert_reqs is not None:
        context.verify_mode = cert_reqs
    context.check_hostname = check_hostname

    if keyfile and not certfile:
        raise ValueError("certfile must be specified")
    if certfile or keyfile:
        context.load_cert_chain(certfile, keyfile)

    # load CA root certs
    if cafile or capath or cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elif context.verify_mode != CERT_NONE:
        # no explicit cafile, capath or cadata but the verify mode is
        # CERT_OPTIONAL or CERT_REQUIRED. Let's try to load default system
        # root CA certificates for the given purpose. This may fail silently.
        context.load_default_certs(purpose)

    return context

# Backwards compatibility alias, even though it's not a public name.
_create_stdlib_context = _create_unverified_context

# PEP 493: Verify HTTPS by default, but allow envvar to override that
_https_verify_envvar = 'PYTHONHTTPSVERIFY'

def _get_https_context_factory():
    if not sys.flags.ignore_environment:
        config_setting = os.environ.get(_https_verify_envvar)
        if config_setting == '0':
            return _create_unverified_context
    return create_default_context

_create_default_https_context = _get_https_context_factory()

# PEP 493: "private" API to configure HTTPS defaults without monkeypatching
def _https_verify_certificates(enable=True):
    """Verify server HTTPS certificates by default?"""
    global _create_default_https_context
    if enable:
        _create_default_https_context = create_default_context
    else:
        _create_default_https_context = _create_unverified_context


class SSLSocket(socket):
    """This class implements a subtype of socket.socket that wraps
    the underlying OS socket in an SSL context when necessary, and
    provides read and write methods over that channel."""

    def __init__(self, sock=None, keyfile=None, certfile=None,
                 server_side=False, cert_reqs=CERT_NONE,
                 ssl_version=PROTOCOL_SSLv23, ca_certs=None,
                 do_handshake_on_connect=True,
                 family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None,
                 suppress_ragged_eofs=True, npn_protocols=None, ciphers=None,
                 server_hostname=None,
                 _context=None):

        self._makefile_refs = 0
        if _context:
            self._context = _context
        else:
            if server_side and not certfile:
                raise ValueError("certfile must be specified for server-side "
                                 "operations")
            if keyfile and not certfile:
                raise ValueError("certfile must be specified")
            if certfile and not keyfile:
                keyfile = certfile
            self._context = SSLContext(ssl_version)
            self._context.verify_mode = cert_reqs
            if ca_certs:
                self._context.load_verify_locations(ca_certs)
            if certfile:
                self._context.load_cert_chain(certfile, keyfile)
            if npn_protocols:
                self._context.set_npn_protocols(npn_protocols)
            if ciphers:
                self._context.set_ciphers(ciphers)
            self.keyfile = keyfile
            self.certfile = certfile
            self.cert_reqs = cert_reqs
            self.ssl_version = ssl_version
            self.ca_certs = ca_certs
            self.ciphers = ciphers
        # Can't use sock.type as other flags (such as SOCK_NONBLOCK) get
        # mixed in.
        if sock.getsockopt(SOL_SOCKET, SO_TYPE) != SOCK_STREAM:
            raise NotImplementedError("only stream sockets are supported")
        import socket
        socket.socket.__init__(self, _sock=sock._sock)
        # The initializer for socket overrides the methods send(), recv(), etc.
        # in the instancce, which we don't need -- but we want to provide the
        # methods defined in SSLSocket.
        for attr in _delegate_methods:
            try:
                delattr(self, attr)
            except AttributeError:
                pass
        if server_side and server_hostname:
            raise ValueError("server_hostname can only be specified "
                             "in client mode")
        if self._context.check_hostname and not server_hostname:
            raise ValueError("check_hostname requires server_hostname")
        self.server_side = server_side
        self.server_hostname = server_hostname
        self.do_handshake_on_connect = do_handshake_on_connect
        self.suppress_ragged_eofs = suppress_ragged_eofs

        # See if we are connected
        try:
            self.getpeername()
        except socket_error as e:
            if e.errno != errno.ENOTCONN:
                raise
            connected = False
        else:
            connected = True

        self._closed = False
        self._sslobj = None
        self._connected = connected
        if connected:
            # create the SSL object
            try:
                self._sslobj = self._context._wrap_socket(self._sock, server_side,
                                                          server_hostname, ssl_sock=self)
                if do_handshake_on_connect:
                    timeout = self.gettimeout()
                    if timeout == 0.0:
                        # non-blocking
                        raise ValueError("do_handshake_on_connect should not be specified for non-blocking sockets")
                    self.do_handshake()

            except (OSError, ValueError):
                self.close()
                raise

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, ctx):
        self._context = ctx
        self._sslobj.context = ctx

    def dup(self):
        raise NotImplemented("Can't dup() %s instances" %
                             self.__class__.__name__)

    def _checkClosed(self, msg=None):
        # raise an exception here if you wish to check for spurious closes
        pass

    def _check_connected(self):
        if not self._connected:
            # getpeername() will raise ENOTCONN if the socket is really
            # not connected; note that we can be connected even without
            # _connected being set, e.g. if connect() first returned
            # EAGAIN.
            self.getpeername()

    def read(self, len=1024, buffer=None):
        """Read up to LEN bytes and return them.
        Return zero-length string on EOF."""

        self._checkClosed()
        if not self._sslobj:
            raise ValueError("Read on closed or unwrapped SSL socket.")
        try:
            if buffer is not None:
                v = self._sslobj.read(len, buffer)
            else:
                v = self._sslobj.read(len)
            return v
        except SSLError as x:
            if x.args[0] == SSL_ERROR_EOF and self.suppress_ragged_eofs:
                if buffer is not None:
                    return 0
                else:
                    return b''
            else:
                raise

    def write(self, data):
        """Write DATA to the underlying SSL channel.  Returns
        number of bytes of DATA actually transmitted."""

        self._checkClosed()
        if not self._sslobj:
            raise ValueError("Write on closed or unwrapped SSL socket.")
        return self._sslobj.write(data)

    def getpeercert(self, binary_form=False):
        """Returns a formatted version of the data in the
        certificate provided by the other end of the SSL channel.
        Return None if no certificate was provided, {} if a
        certificate was provided, but not validated."""

        self._checkClosed()
        self._check_connected()
        return self._sslobj.peer_certificate(binary_form)

    def selected_npn_protocol(self):
        self._checkClosed()
        if not self._sslobj or not _ssl.HAS_NPN:
            return None
        else:
            return self._sslobj.selected_npn_protocol()

    def selected_alpn_protocol(self):
        self._checkClosed()
        if not self._sslobj or not _ssl.HAS_ALPN:
            return None
        else:
            return self._sslobj.selected_alpn_protocol()

    def cipher(self):
        self._checkClosed()
        if not self._sslobj:
            return None
        else:
            return self._sslobj.cipher()

    def compression(self):
        self._checkClosed()
        if not self._sslobj:
            return None
        else:
            return self._sslobj.compression()

    def send(self, data, flags=0):
        self._checkClosed()
        if self._sslobj:
            if flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to send() on %s" %
                    self.__class__)
            try:
                v = self._sslobj.write(data)
            except SSLError as x:
                if x.args[0] == SSL_ERROR_WANT_READ:
                    return 0
                elif x.args[0] == SSL_ERROR_WANT_WRITE:
                    return 0
                else:
                    raise
            else:
                return v
        else:
            return self._sock.send(data, flags)

    def sendto(self, data, flags_or_addr, addr=None):
        self._checkClosed()
        if self._sslobj:
            raise ValueError("sendto not allowed on instances of %s" %
                             self.__class__)
        elif addr is None:
            return self._sock.sendto(data, flags_or_addr)
        else:
            return self._sock.sendto(data, flags_or_addr, addr)


    def sendall(self, data, flags=0):
        self._checkClosed()
        if self._sslobj:
            if flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to sendall() on %s" %
                    self.__class__)
            amount = len(data)
            count = 0
            while (count < amount):
                v = self.send(data[count:])
                count += v
            return amount
        else:
            return socket.sendall(self, data, flags)

    def recv(self, buflen=1024, flags=0):
        self._checkClosed()
        if self._sslobj:
            if flags != 0:
                raise ValueError(
                    "non-zero flags not allowed in calls to recv() on %s" %
                    self.__class__)
            return self.read(buflen)
        else:
            return self._sock.recv(buflen, flags)

    def recv_into(self, buffer, nbytes=None, flags=0):
        self._checkClosed()
        if buffer and (nbytes is None):
            nbytes = len(buffer)
        elif nbytes is None:
            nbytes = 1024
        if self._sslobj:
            if flags != 0:
                raise ValueError(
                  "non-zero flags not allowed in calls to recv_into() on %s" %
                  self.__class__)
            return self.read(nbytes, buffer)
        else:
            return self._sock.recv_into(buffer, nbytes, flags)

    def recvfrom(self, buflen=1024, flags=0):
        self._checkClosed()
        if self._sslobj:
            raise ValueError("recvfrom not allowed on instances of %s" %
                             self.__class__)
        else:
            return self._sock.recvfrom(buflen, flags)

    def recvfrom_into(self, buffer, nbytes=None, flags=0):
        self._checkClosed()
        if self._sslobj:
            raise ValueError("recvfrom_into not allowed on instances of %s" %
                             self.__class__)
        else:
            return self._sock.recvfrom_into(buffer, nbytes, flags)


    def pending(self):
        self._checkClosed()
        if self._sslobj:
            return self._sslobj.pending()
        else:
            return 0

    def shutdown(self, how):
        self._checkClosed()
        self._sslobj = None
        socket.shutdown(self, how)

    def close(self):
        if self._makefile_refs < 1:
            self._sslobj = None
            socket.socket.close(self)
        else:
            self._makefile_refs -= 1

    def unwrap(self):
        if self._sslobj:
            s = self._sslobj.shutdown()
            self._sslobj = None
            return s
        else:
            raise ValueError("No SSL wrapper around " + str(self))

    def _real_close(self):
        self._sslobj = None
        socket._real_close(self)

    def do_handshake(self, block=False):
        """Perform a TLS/SSL handshake."""
        self._check_connected()
        timeout = self.gettimeout()
        try:
            if timeout == 0.0 and block:
                self.settimeout(None)
            self._sslobj.do_handshake()
        finally:
            self.settimeout(timeout)

        if self.context.check_hostname:
            if not self.server_hostname:
                raise ValueError("check_hostname needs server_hostname "
                                 "argument")
            match_hostname(self.getpeercert(), self.server_hostname)

    def _real_connect(self, addr, connect_ex):
        if self.server_side:
            raise ValueError("can't connect in server-side mode")
        # Here we assume that the socket is client-side, and not
        # connected at the time of the call.  We connect it, then wrap it.
        if self._connected:
            raise ValueError("attempt to connect already-connected SSLSocket!")
        self._sslobj = self.context._wrap_socket(self._sock, False, self.server_hostname, ssl_sock=self)
        try:
            if connect_ex:
                rc = socket.connect_ex(self, addr)
            else:
                rc = None
                socket.connect(self, addr)
            if not rc:
                self._connected = True
                if self.do_handshake_on_connect:
                    self.do_handshake()
            return rc
        except (OSError, ValueError):
            self._sslobj = None
            raise

    def connect(self, addr):
        """Connects to remote ADDR, and then wraps the connection in
        an SSL channel."""
        self._real_connect(addr, False)

    def connect_ex(self, addr):
        """Connects to remote ADDR, and then wraps the connection in
        an SSL channel."""
        return self._real_connect(addr, True)

    def accept(self):
        """Accepts a new connection from a remote client, and returns
        a tuple containing that new connection wrapped with a server-side
        SSL channel, and the address of the remote client."""

        newsock, addr = socket.accept(self)
        newsock = self.context.wrap_socket(newsock,
                    do_handshake_on_connect=self.do_handshake_on_connect,
                    suppress_ragged_eofs=self.suppress_ragged_eofs,
                    server_side=True)
        return newsock, addr

    def makefile(self, mode='r', bufsize=-1):

        """Make and return a file-like object that
        works with the SSL connection.  Just use the code
        from the socket module."""

        self._makefile_refs += 1
        # close=True so as to decrement the reference count when done with
        # the file-like object.
        return _fileobject(self, mode, bufsize, close=True)

    def get_channel_binding(self, cb_type="tls-unique"):
        """Get channel binding data for current connection.  Raise ValueError
        if the requested `cb_type` is not supported.  Return bytes of the data
        or None if the data is not available (e.g. before the handshake).
        """
        if cb_type not in CHANNEL_BINDING_TYPES:
            raise ValueError("Unsupported channel binding type")
        if cb_type != "tls-unique":
            raise NotImplementedError(
                            "{0} channel binding type not implemented"
                            .format(cb_type))
        if self._sslobj is None:
            return None
        return self._sslobj.tls_unique_cb()

    def version(self):
        """
        Return a string identifying the protocol version used by the
        current SSL channel, or None if there is no established channel.
        """
        if self._sslobj is None:
            return None
        return self._sslobj.version()


def wrap_socket(sock, keyfile=None, certfile=None,
                server_side=False, cert_reqs=CERT_NONE,
                ssl_version=PROTOCOL_SSLv23, ca_certs=None,
                do_handshake_on_connect=True,
                suppress_ragged_eofs=True,
                ciphers=None):

    return SSLSocket(sock=sock, keyfile=keyfile, certfile=certfile,
                     server_side=server_side, cert_reqs=cert_reqs,
                     ssl_version=ssl_version, ca_certs=ca_certs,
                     do_handshake_on_connect=do_handshake_on_connect,
                     suppress_ragged_eofs=suppress_ragged_eofs,
                     ciphers=ciphers)

# some utility functions

def cert_time_to_seconds(cert_time):
    """Return the time in seconds since the Epoch, given the timestring
    representing the "notBefore" or "notAfter" date from a certificate
    in ``"%b %d %H:%M:%S %Y %Z"`` strptime format (C locale).

    "notBefore" or "notAfter" dates must use UTC (RFC 5280).

    Month is one of: Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
    UTC should be specified as GMT (see ASN1_TIME_print())
    """
    from time import strptime
    from calendar import timegm

    months = (
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    )
    time_format = ' %d %H:%M:%S %Y GMT' # NOTE: no month, fixed GMT
    try:
        month_number = months.index(cert_time[:3].title()) + 1
    except ValueError:
        raise ValueError('time data %r does not match '
                         'format "%%b%s"' % (cert_time, time_format))
    else:
        # found valid month
        tt = strptime(cert_time[3:], time_format)
        # return an integer, the previous mktime()-based implementation
        # returned a float (fractional seconds are always zero here).
        return timegm((tt[0], month_number) + tt[2:6])

PEM_HEADER = "-----BEGIN CERTIFICATE-----"
PEM_FOOTER = "-----END CERTIFICATE-----"

def DER_cert_to_PEM_cert(der_cert_bytes):
    """Takes a certificate in binary DER format and returns the
    PEM version of it as a string."""

    f = base64.standard_b64encode(der_cert_bytes).decode('ascii')
    return (PEM_HEADER + '\n' +
            fill(f, 64) + '\n' +
            PEM_FOOTER + '\n')

def PEM_cert_to_DER_cert(pem_cert_string):
    """Takes a certificate in ASCII PEM format and returns the
    DER-encoded version of it as a byte sequence"""

    if not pem_cert_string.startswith(PEM_HEADER):
        raise ValueError("Invalid PEM encoding; must start with %s"
                         % PEM_HEADER)
    if not pem_cert_string.strip().endswith(PEM_FOOTER):
        raise ValueError("Invalid PEM encoding; must end with %s"
                         % PEM_FOOTER)
    d = pem_cert_string.strip()[len(PEM_HEADER):-len(PEM_FOOTER)]
    return base64.decodestring(d.encode('ASCII', 'strict'))

def get_server_certificate(addr, ssl_version=PROTOCOL_SSLv23, ca_certs=None):
    """Retrieve the certificate from the server at the specified address,
    and return it as a PEM-encoded string.
    If 'ca_certs' is specified, validate the server cert against it.
    If 'ssl_version' is specified, use it in the connection attempt."""

    host, port = addr
    if ca_certs is not None:
        cert_reqs = CERT_REQUIRED
    else:
        cert_reqs = CERT_NONE
    context = _create_stdlib_context(ssl_version,
                                     cert_reqs=cert_reqs,
                                     cafile=ca_certs)
    with closing(create_connection(addr)) as sock:
        with closing(context.wrap_socket(sock)) as sslsock:
            dercert = sslsock.getpeercert(True)
    return DER_cert_to_PEM_cert(dercert)

def get_protocol_name(protocol_code):
    return _PROTOCOL_NAMES.get(protocol_code, '<unknown>')


# a replacement for the old socket.ssl function

def sslwrap_simple(sock, keyfile=None, certfile=None):
    """A replacement for the old socket.ssl function.  Designed
    for compability with Python 2.5 and earlier.  Will disappear in
    Python 3.0."""
    if hasattr(sock, "_sock"):
        sock = sock._sock

    ctx = SSLContext(PROTOCOL_SSLv23)
    if keyfile or certfile:
        ctx.load_cert_chain(certfile, keyfile)
    ssl_sock = ctx._wrap_socket(sock, server_side=False)
    try:
        sock.getpeername()
    except socket_error:
        # no, no connection yet
        pass
    else:
        # yes, do the handshake
        ssl_sock.do_handshake()

    return ssl_sock

import httplib, socket

class HTTPSConnection(httplib.HTTPConnection):
    default_port = 443
    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None, context=None):
        httplib.HTTPConnection.__init__(self, host, port, strict, timeout, source_address)
        self.key_file = key_file
        self.cert_file = cert_file
        if context is None:
            context = _create_default_https_context()
        if key_file or cert_file:
            context.load_cert_chain(cert_file, key_file)
        self._context = context

    def connect(self):
        httplib.HTTPConnection.connect(self)
        if self._tunnel_host:
            server_hostname = self._tunnel_host
        else:
            server_hostname = self.host
        self.sock = self._context.wrap_socket(self.sock, server_hostname=server_hostname)

from httplib import HTTP

class HTTPS(HTTP):
    _connection_class = HTTPSConnection
    def __init__(self, host='', port=None, key_file=None, cert_file=None, strict=None, context=None):
        if port == 0: port = None
        self._setup(self._connection_class(host, port, key_file, cert_file, strict, context=context))
        self.key_file = key_file
        self.cert_file = cert_file

    def FakeSocket (sock, sslobj):
        warnings.warn("FakeSocket is deprecated, and won't be in 3.x.  " +
                      "Use the result of ssl.wrap_socket() directly instead.",
                      DeprecationWarning, stacklevel=2)
        return sslobj

from urllib2 import AbstractHTTPHandler

class HTTPSHandler(AbstractHTTPHandler):
    def __init__(self, debuglevel=0, context=None):
        AbstractHTTPHandler.__init__(self, debuglevel)
        self._context = context

    def https_open(self, req):
        return self.do_open(HTTPSConnection, req,
            context=self._context)

    https_request = AbstractHTTPHandler.do_request_

import bs
import bsInternal
import os
import shutil
import json
import urllib2
import urllib
install_modules=[]
for i in ["zipfile", "io", "string", "re"]:
    try: __import__(i)
    except ImportError: install_modules.append(i+".py")

class InstallError(Exception):
    def __init__(self):
        pass
class DownloadError(Exception):
    def __init__(self):
        pass

from urllib2 import OpenerDirector, ProxyHandler, UnknownHandler, HTTPHandler, \
    HTTPDefaultErrorHandler, HTTPRedirectHandler, \
    FTPHandler, FileHandler, HTTPErrorProcessor

def build_opener(*handlers):
    import types
    def isclass(obj):
        return isinstance(obj, (types.ClassType, type))

    opener = OpenerDirector()
    default_classes = [ProxyHandler, UnknownHandler, HTTPHandler,
                       HTTPDefaultErrorHandler, HTTPRedirectHandler,
                       FTPHandler, FileHandler, HTTPErrorProcessor]
    default_classes.append(HTTPSHandler)
    skip = set()
    for klass in default_classes:
        for check in handlers:
            if isclass(check):
                if issubclass(check, klass):
                    skip.add(klass)
            elif isinstance(check, klass):
                skip.add(klass)
    for klass in skip:
        default_classes.remove(klass)

    for klass in default_classes:
        opener.add_handler(klass())

    for h in handlers:
        if isclass(h):
            h = h()
        opener.add_handler(h)
    return opener

_opener = None
def urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            cafile=None, capath=None, cadefault=False, context=None):
    global _opener
    if cafile or capath or cadefault:
        if context is not None:
            raise ValueError(
                "You can't pass both context and any of cafile, capath, and "
                "cadefault"
            )
        context = create_default_context(purpose=Purpose.SERVER_AUTH,
                                             cafile=cafile,
                                             capath=capath)
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    elif context:
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    elif _opener is None:
        _opener = opener = build_opener()
    else:
        opener = _opener
    return opener.open(url, data, timeout)

env=bs.getEnvironment()
gInstallPath=str(env["userScriptsDirectory"])
gDownloadPath="https://github.com/DrovGamedev/BombSquad-Hardcore-Modpack/raw/master/"
#str(env["configFilePath"].split("/")[0:-2]) if env["platform"] == "android" else str(env["userScriptsDirectory"])

def download(url, path, reload_files=True):
    print("try to open url: "+url)
    try:
        u = urlopen(url.replace(" ", "%20"))
        print("opened successfully")
    except Exception as E:
        print("cann\'t open url: "+url+"; connection aborted")
        print(str(E))
        return False
    print("creating file "+path.split(os.sep)[-1])
    if not os.path.exists(path) or reload_files:
        fp = open(path, 'wb')
        info, cnt = 0, 0
        print("reading chunks...")
        while True:
            try: chunk = u.read(8192)
            except:
                print("error reading chunk "+str(cnt))
                return False
            if not chunk:
                print("download complete; bytes: "+ str(info) + " ("+str(float(info/1048576))+"mb); chunks count: "+str(cnt))
                break
            fp.write(chunk)
            info += len(bytes(chunk))
            cnt += 1
        fp.close()
        print("file created.")
        return True
    else: raise ValueError("path already exists: " + path)

if len(install_modules) > 0:
    for i in install_modules:
        if not download(gDownloadPath+i, os.path.join(gInstallPath, i)): break

def get_local_versions():
    path = os.path.join(gInstallPath, "versions.json")
    def write_path():
        data = {}
        json.dump(data, open(path, "w+"))
        return data
    if os.path.exists(path):
        try: data=json.load(open(path))
        except Exception: data=write_path()
    else: data=write_path()
    if "install.py" in data: data.pop("install.py")
    return data

def reloadScripts():
    a=globals().keys()
    for i in a:
        if "__package__" in dir(globals()[i]):
            try: reload(__import__(i))
            except: pass

def get_versions_from_source(last=False):
    file = "versions.json"
    path = str(os.path.join(gInstallPath, file))
    url = gDownloadPath+file
    data = {}
    if download(url=url, path=path):
        try:
            if os.path.exists(path): data=json.load(open(path))
        except Exception:
            data={}
            json.dump(data, open(path, "w+"))
            print("versions-file was broken")
        if last:
            if len(data) > 0:
                a={"None": 0}
                for i in data:
                    if data.get(i) > a.values()[0]: a={i: data.get(i)}
                if a.values()[0] > 0: data=a
    return data

import zipfile

def make_versions():
    path = os.path.join(gInstallPath, "about_modpack.json")
    if os.path.exists(path):
        try: installed_version = json.load(open(path)).get("versions", {"v": 0}).get("v")
        except Exception: installed_version = 0
    else: installed_version = 0
    versions = get_versions_from_source()
    if len(versions) < 1: versions = get_local_versions()
    last_version = None
    if len(versions) > 0:
        last_version = {"None": 0}
        for i in versions:
            if versions.get(i) > last_version.values()[0]: last_version = {i: versions.get(i)}
        if last_version.values()[0] < 1: last_version = None
    return versions, last_version, installed_version

versions, last_version, installed_version = make_versions()

def format_version(file):
    path = os.path.join(gInstallPath, file)
    result = 0
    try: modpack=zipfile.ZipFile(file=path)
    except Exception: modpack=None
    if modpack is not None:
        if "about_modpack.json" in modpack.namelist():
            path=(os.path.join(os.path.join(gInstallPath, "temp_path"), file))
            modpack.extract("about_modpack.json", path)
            try: result=int(json.load(open(os.path.join(path, "about_modpack.json"), "r")).get("version", {"v":0}).get("v"))
            except Exception as E: bsInternal._log("error reading version-file: "+str(E))
        modpack.close()
    return result

def update(version=None, ignore_old_versions=True):
    if version is None and last_version is not None: version = last_version.values()[0]
    path=(os.path.join(gInstallPath, "about_modpack.json"))
    if isinstance(version, int):
        if version in versions.values(): version = {"version": {"name": i, "v": versions.get(i)} for i in versions if versions.get(i) == version}
    if isinstance(version, dict):
        if len(version) > 0:
            def inst():
                json.dump(version, open(path, "w+"))
                extract_file(data=version)
            if ignore_old_versions:
                if installed_version < version["version"]["v"]: inst()
            else: inst()

def load(version=None):
    path = gInstallPath
    if version is None and last_version is not None: version = last_version
    else:
        if len(versions) > 0:
            version = {i: versions.get(i) for i in versions if versions.get(i) == version}
    if isinstance(version, dict) and len(version) == 1:
        version = str(version.keys()[0])
        path = os.path.join(path, version)
        if not os.path.exists(path): download(gDownloadPath+version, path)

def get_loaded_versions(last=False):
    path=gInstallPath
    if len(os.listdir(path))>0:
        zipfile_namelist=[i for i in os.listdir(path) if zipfile.is_zipfile(os.path.join(path, i))]
        versions={}
        for i in zipfile_namelist:
            a=format_version(file=i)
            if a > 0: versions.update({i: a})
        if last:
            if len(versions) > 0:
                version = {"None": 0}
                for i in versions:
                    if versions.get(i) > version.values()[0]: version={i: versions.get(i)}
                versions = version if version.values()[0] > 0 else None
    if os.path.exists(os.path.join(path, "temp_path")): shutil.rmtree(os.path.join(path, "temp_path"))
    return versions

def extract_file(data={}):
    try:
        path=os.path.join(gInstallPath, str(data["version"]["name"]))
        if os.path.exists(path) and zipfile.is_zipfile(path):
            zipfile.ZipFile(path).extractall(gInstallPath)
            reloadScripts()
    except Exception:
        raise InstallError

def update_modpack(net=False, version=None):
    if version is None and last_version is not None: version = last_version.values()[0]
    if version is not None and isinstance(version, int):
        if version in versions.values():
            if version not in get_loaded_versions().values(): load(version=version)
            a = get_loaded_versions()
            if version in a.values(): update(version=version, ignore_old_versions=False)

if "get_setting" not in dir(bs): update_modpack(True)