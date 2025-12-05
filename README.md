# pypatree

[![CI](https://github.com/yberreby/pypatree/actions/workflows/ci.yml/badge.svg)](https://github.com/yberreby/pypatree/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pypatree)](https://pypi.org/project/pypatree/)
[![Python](https://img.shields.io/pypi/pyversions/pypatree)](https://pypi.org/project/pypatree/)
[![License](https://img.shields.io/pypi/l/pypatree?v=2)](https://github.com/yberreby/pypatree/blob/main/LICENSE)

Pretty-print a project's module tree with syntax-highlighted signatures.

```bash
uv add --dev pypatree
uv run pypatree
```

```
pypatree  pypatree - Pretty-print a project's module tree.
├── __main__
│   ├── main() -> None
│   └── run(cfg: pypatree.config.Config) -> None
├── config  Configuration types for pypatree.
│   ├── Config(exclude: Optional[str] = '^test$|^test_', docstrings: 
│   │   pypatree.config.DocstringMode = <DocstringMode.short: 'short'>) -> None
│   └── DocstringMode(*args, **kwargs)
├── discovery
│   └── get_packages(exclude: Optional[str] = None) -> dict[str, list[str]]
├── display
│   ├── print_tree(pkg_name: str, tree: dict[str, typing.Any], cfg: 
│   │   pypatree.config.Config) -> None
│   └── render_tree(tree: dict[str, typing.Any], prefix: str = '') -> list[str]
├── introspection
│   ├── format_signature(obj: Union[Callable, type]) -> str
│   ├── get_module_docstring(modname: str, short: bool = True) -> Optional[str]
│   └── get_module_items(modname: str, exclude: Optional[str] = None) -> 
│       list[str]
└── tree
    └── build_tree(submods: list[str], pkg_name: str, exclude: Optional[str] = 
        None) -> dict[str, typing.Any]
```

Run `pypatree --help` for options:
```
usage: pypatree [-h] [--exclude {None}|STR] [--docstrings {none,short,full}]

Display module tree with public functions/classes.

╭─ options ──────────────────────────────────────────────────────────────────╮
│ -h, --help              show this help message and exit                    │
│ --exclude {None}|STR    Regex to exclude module segments (default: test    │
│                         modules). Use '' for none. (default:               │
│                         '^test$|^test_')                                   │
│ --docstrings {none,short,full}                                             │
│                         Show module docstrings: none, short (first line),  │
│                         or full. (default: short)                          │
╰────────────────────────────────────────────────────────────────────────────╯
```

Example on [httpx](https://github.com/encode/httpx):
```
httpx
├── ASGITransport(app: '_ASGIApp', raise_app_exceptions: 'bool' = True, 
│   root_path: 'str' = '', client: 'tuple[str, int]' = ('127.0.0.1', 123)) -> 
│   'None'
├── AsyncBaseTransport(*args, **kwargs)
├── AsyncByteStream(*args, **kwargs)
├── AsyncClient(*, auth: 'AuthTypes | None' = None, params: 'QueryParamTypes | 
│   None' = None, headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | 
│   None' = None, verify: 'ssl.SSLContext | str | bool' = True, cert: 'CertTypes
│   | None' = None, http1: 'bool' = True, http2: 'bool' = False, proxy: 
│   'ProxyTypes | None' = None, mounts: 'None | typing.Mapping[str, 
│   AsyncBaseTransport | None]' = None, timeout: 'TimeoutTypes' = 
│   Timeout(timeout=5.0), follow_redirects: 'bool' = False, limits: 'Limits' = 
│   Limits(max_connections=100, max_keepalive_connections=20, 
│   keepalive_expiry=5.0), max_redirects: 'int' = 20, event_hooks: 'None | 
│   typing.Mapping[str, list[EventHook]]' = None, base_url: 'URL | str' = '', 
│   transport: 'AsyncBaseTransport | None' = None, trust_env: 'bool' = True, 
│   default_encoding: 'str | typing.Callable[[bytes], str]' = 'utf-8') -> 'None'
├── AsyncHTTPTransport(verify: 'ssl.SSLContext | str | bool' = True, cert: 
│   'CertTypes | None' = None, trust_env: 'bool' = True, http1: 'bool' = True, 
│   http2: 'bool' = False, limits: 'Limits' = Limits(max_connections=100, 
│   max_keepalive_connections=20, keepalive_expiry=5.0), proxy: 'ProxyTypes | 
│   None' = None, uds: 'str | None' = None, local_address: 'str | None' = None, 
│   retries: 'int' = 0, socket_options: 'typing.Iterable[SOCKET_OPTION] | None' 
│   = None) -> 'None'
├── Auth(*args, **kwargs)
├── BaseTransport(*args, **kwargs)
├── BasicAuth(username: 'str | bytes', password: 'str | bytes') -> 'None'
├── ByteStream(stream: 'bytes') -> 'None'
├── Client(*, auth: 'AuthTypes | None' = None, params: 'QueryParamTypes | None' 
│   = None, headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' 
│   = None, verify: 'ssl.SSLContext | str | bool' = True, cert: 'CertTypes | 
│   None' = None, trust_env: 'bool' = True, http1: 'bool' = True, http2: 'bool' 
│   = False, proxy: 'ProxyTypes | None' = None, mounts: 'None | 
│   typing.Mapping[str, BaseTransport | None]' = None, timeout: 'TimeoutTypes' =
│   Timeout(timeout=5.0), follow_redirects: 'bool' = False, limits: 'Limits' = 
│   Limits(max_connections=100, max_keepalive_connections=20, 
│   keepalive_expiry=5.0), max_redirects: 'int' = 20, event_hooks: 'None | 
│   typing.Mapping[str, list[EventHook]]' = None, base_url: 'URL | str' = '', 
│   transport: 'BaseTransport | None' = None, default_encoding: 'str | 
│   typing.Callable[[bytes], str]' = 'utf-8') -> 'None'
├── CloseError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── ConnectError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── ConnectTimeout(message: 'str', *, request: 'Request | None' = None) -> 
│   'None'
├── CookieConflict(message: 'str') -> 'None'
├── Cookies(cookies: 'CookieTypes | None' = None) -> 'None'
├── DecodingError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── DigestAuth(username: 'str | bytes', password: 'str | bytes') -> 'None'
├── HTTPError(message: 'str') -> 'None'
├── HTTPStatusError(message: 'str', *, request: 'Request', response: 'Response')
│   -> 'None'
├── HTTPTransport(verify: 'ssl.SSLContext | str | bool' = True, cert: 'CertTypes
│   | None' = None, trust_env: 'bool' = True, http1: 'bool' = True, http2: 
│   'bool' = False, limits: 'Limits' = Limits(max_connections=100, 
│   max_keepalive_connections=20, keepalive_expiry=5.0), proxy: 'ProxyTypes | 
│   None' = None, uds: 'str | None' = None, local_address: 'str | None' = None, 
│   retries: 'int' = 0, socket_options: 'typing.Iterable[SOCKET_OPTION] | None' 
│   = None) -> 'None'
├── Headers(headers: 'HeaderTypes | None' = None, encoding: 'str | None' = None)
│   -> 'None'
├── InvalidURL(message: 'str') -> 'None'
├── Limits(*, max_connections: 'int | None' = None, max_keepalive_connections: 
│   'int | None' = None, keepalive_expiry: 'float | None' = 5.0) -> 'None'
├── LocalProtocolError(message: 'str', *, request: 'Request | None' = None) -> 
│   'None'
├── MockTransport(handler: 'SyncHandler | AsyncHandler') -> 'None'
├── NetRCAuth(file: 'str | None' = None) -> 'None'
├── NetworkError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── PoolTimeout(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── ProtocolError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── Proxy(url: 'URL | str', *, ssl_context: 'ssl.SSLContext | None' = None, 
│   auth: 'tuple[str, str] | None' = None, headers: 'HeaderTypes | None' = None)
│   -> 'None'
├── ProxyError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── QueryParams(*args: 'QueryParamTypes | None', **kwargs: 'typing.Any') -> 
│   'None'
├── ReadError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── ReadTimeout(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── RemoteProtocolError(message: 'str', *, request: 'Request | None' = None) -> 
│   'None'
├── Request(method: 'str', url: 'URL | str', *, params: 'QueryParamTypes | None'
│   = None, headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' 
│   = None, content: 'RequestContent | None' = None, data: 'RequestData | None' 
│   = None, files: 'RequestFiles | None' = None, json: 'typing.Any | None' = 
│   None, stream: 'SyncByteStream | AsyncByteStream | None' = None, extensions: 
│   'RequestExtensions | None' = None) -> 'None'
├── RequestError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── RequestNotRead() -> 'None'
├── Response(status_code: 'int', *, headers: 'HeaderTypes | None' = None, 
│   content: 'ResponseContent | None' = None, text: 'str | None' = None, html: 
│   'str | None' = None, json: 'typing.Any' = None, stream: 'SyncByteStream | 
│   AsyncByteStream | None' = None, request: 'Request | None' = None, 
│   extensions: 'ResponseExtensions | None' = None, history: 'list[Response] | 
│   None' = None, default_encoding: 'str | typing.Callable[[bytes], str]' = 
│   'utf-8') -> 'None'
├── ResponseNotRead() -> 'None'
├── StreamClosed() -> 'None'
├── StreamConsumed() -> 'None'
├── StreamError(message: 'str') -> 'None'
├── SyncByteStream(*args, **kwargs)
├── Timeout(timeout: 'TimeoutTypes | UnsetType' = <httpx._config.UnsetType 
│   object>, *, connect: 'None | float | UnsetType' = <httpx._config.UnsetType 
│   object>, read: 'None | float | UnsetType' = <httpx._config.UnsetType 
│   object>, write: 'None | float | UnsetType' = <httpx._config.UnsetType 
│   object>, pool: 'None | float | UnsetType' = <httpx._config.UnsetType 
│   object>) -> 'None'
├── TimeoutException(message: 'str', *, request: 'Request | None' = None) -> 
│   'None'
├── TooManyRedirects(message: 'str', *, request: 'Request | None' = None) -> 
│   'None'
├── TransportError(message: 'str', *, request: 'Request | None' = None) -> 
│   'None'
├── URL(url: 'URL | str' = '', **kwargs: 'typing.Any') -> 'None'
├── UnsupportedProtocol(message: 'str', *, request: 'Request | None' = None) -> 
│   'None'
├── WSGITransport(app: 'WSGIApplication', raise_app_exceptions: 'bool' = True, 
│   script_name: 'str' = '', remote_addr: 'str' = '127.0.0.1', wsgi_errors: 
│   'typing.TextIO | None' = None) -> 'None'
├── WriteError(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── WriteTimeout(message: 'str', *, request: 'Request | None' = None) -> 'None'
├── codes(*args, **kwargs)
├── create_ssl_context(verify: 'ssl.SSLContext | str | bool' = True, cert: 
│   'CertTypes | None' = None, trust_env: 'bool' = True) -> 'ssl.SSLContext'
├── delete(url: 'URL | str', *, params: 'QueryParamTypes | None' = None, 
│   headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, 
│   auth: 'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   follow_redirects: 'bool' = False, timeout: 'TimeoutTypes' = 
│   Timeout(timeout=5.0), verify: 'ssl.SSLContext | str | bool' = True, 
│   trust_env: 'bool' = True) -> 'Response'
├── get(url: 'URL | str', *, params: 'QueryParamTypes | None' = None, headers: 
│   'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, auth: 
│   'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   follow_redirects: 'bool' = False, verify: 'ssl.SSLContext | str | bool' = 
│   True, timeout: 'TimeoutTypes' = Timeout(timeout=5.0), trust_env: 'bool' = 
│   True) -> 'Response'
├── head(url: 'URL | str', *, params: 'QueryParamTypes | None' = None, headers: 
│   'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, auth: 
│   'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   follow_redirects: 'bool' = False, verify: 'ssl.SSLContext | str | bool' = 
│   True, timeout: 'TimeoutTypes' = Timeout(timeout=5.0), trust_env: 'bool' = 
│   True) -> 'Response'
├── main() -> None
├── options(url: 'URL | str', *, params: 'QueryParamTypes | None' = None, 
│   headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, 
│   auth: 'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   follow_redirects: 'bool' = False, verify: 'ssl.SSLContext | str | bool' = 
│   True, timeout: 'TimeoutTypes' = Timeout(timeout=5.0), trust_env: 'bool' = 
│   True) -> 'Response'
├── patch(url: 'URL | str', *, content: 'RequestContent | None' = None, data: 
│   'RequestData | None' = None, files: 'RequestFiles | None' = None, json: 
│   'typing.Any | None' = None, params: 'QueryParamTypes | None' = None, 
│   headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, 
│   auth: 'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   follow_redirects: 'bool' = False, verify: 'ssl.SSLContext | str | bool' = 
│   True, timeout: 'TimeoutTypes' = Timeout(timeout=5.0), trust_env: 'bool' = 
│   True) -> 'Response'
├── post(url: 'URL | str', *, content: 'RequestContent | None' = None, data: 
│   'RequestData | None' = None, files: 'RequestFiles | None' = None, json: 
│   'typing.Any | None' = None, params: 'QueryParamTypes | None' = None, 
│   headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, 
│   auth: 'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   follow_redirects: 'bool' = False, verify: 'ssl.SSLContext | str | bool' = 
│   True, timeout: 'TimeoutTypes' = Timeout(timeout=5.0), trust_env: 'bool' = 
│   True) -> 'Response'
├── put(url: 'URL | str', *, content: 'RequestContent | None' = None, data: 
│   'RequestData | None' = None, files: 'RequestFiles | None' = None, json: 
│   'typing.Any | None' = None, params: 'QueryParamTypes | None' = None, 
│   headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = None, 
│   auth: 'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   follow_redirects: 'bool' = False, verify: 'ssl.SSLContext | str | bool' = 
│   True, timeout: 'TimeoutTypes' = Timeout(timeout=5.0), trust_env: 'bool' = 
│   True) -> 'Response'
├── request(method: 'str', url: 'URL | str', *, params: 'QueryParamTypes | None'
│   = None, content: 'RequestContent | None' = None, data: 'RequestData | None' 
│   = None, files: 'RequestFiles | None' = None, json: 'typing.Any | None' = 
│   None, headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = 
│   None, auth: 'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   timeout: 'TimeoutTypes' = Timeout(timeout=5.0), follow_redirects: 'bool' = 
│   False, verify: 'ssl.SSLContext | str | bool' = True, trust_env: 'bool' = 
│   True) -> 'Response'
├── stream(method: 'str', url: 'URL | str', *, params: 'QueryParamTypes | None' 
│   = None, content: 'RequestContent | None' = None, data: 'RequestData | None' 
│   = None, files: 'RequestFiles | None' = None, json: 'typing.Any | None' = 
│   None, headers: 'HeaderTypes | None' = None, cookies: 'CookieTypes | None' = 
│   None, auth: 'AuthTypes | None' = None, proxy: 'ProxyTypes | None' = None, 
│   timeout: 'TimeoutTypes' = Timeout(timeout=5.0), follow_redirects: 'bool' = 
│   False, verify: 'ssl.SSLContext | str | bool' = True, trust_env: 'bool' = 
│   True) -> 'typing.Iterator[Response]'
├── __version__
├── _api
├── _auth
│   └── FunctionAuth(func: 'typing.Callable[[Request], Request]') -> 'None'
├── _client
│   ├── BaseClient(*, auth: 'AuthTypes | None' = None, params: 'QueryParamTypes 
│   │   | None' = None, headers: 'HeaderTypes | None' = None, cookies: 
│   │   'CookieTypes | None' = None, timeout: 'TimeoutTypes' = 
│   │   Timeout(timeout=5.0), follow_redirects: 'bool' = False, max_redirects: 
│   │   'int' = 20, event_hooks: 'None | typing.Mapping[str, list[EventHook]]' =
│   │   None, base_url: 'URL | str' = '', trust_env: 'bool' = True, 
│   │   default_encoding: 'str | typing.Callable[[bytes], str]' = 'utf-8') -> 
│   │   'None'
│   ├── BoundAsyncStream(stream: 'AsyncByteStream', response: 'Response', start:
│   │   'float') -> 'None'
│   ├── BoundSyncStream(stream: 'SyncByteStream', response: 'Response', start: 
│   │   'float') -> 'None'
│   ├── ClientState(*args, **kwargs)
│   └── UseClientDefault(*args, **kwargs)
├── _config
│   └── UnsetType(*args, **kwargs)
├── _content
│   ├── AsyncIteratorByteStream(stream: 'AsyncIterable[bytes]') -> 'None'
│   ├── IteratorByteStream(stream: 'Iterable[bytes]') -> 'None'
│   ├── UnattachedStream(*args, **kwargs)
│   ├── encode_content(content: 'str | bytes | Iterable[bytes] | 
│   │   AsyncIterable[bytes]') -> 'tuple[dict[str, str], SyncByteStream | 
│   │   AsyncByteStream]'
│   ├── encode_html(html: 'str') -> 'tuple[dict[str, str], ByteStream]'
│   ├── encode_json(json: 'Any') -> 'tuple[dict[str, str], ByteStream]'
│   ├── encode_multipart_data(data: 'RequestData', files: 'RequestFiles', 
│   │   boundary: 'bytes | None') -> 'tuple[dict[str, str], MultipartStream]'
│   ├── encode_request(content: 'RequestContent | None' = None, data: 
│   │   'RequestData | None' = None, files: 'RequestFiles | None' = None, json: 
│   │   'Any | None' = None, boundary: 'bytes | None' = None) -> 
│   │   'tuple[dict[str, str], SyncByteStream | AsyncByteStream]'
│   ├── encode_response(content: 'ResponseContent | None' = None, text: 'str | 
│   │   None' = None, html: 'str | None' = None, json: 'Any | None' = None) -> 
│   │   'tuple[dict[str, str], SyncByteStream | AsyncByteStream]'
│   ├── encode_text(text: 'str') -> 'tuple[dict[str, str], ByteStream]'
│   └── encode_urlencoded_data(data: 'RequestData') -> 'tuple[dict[str, str], 
│       ByteStream]'
├── _decoders  Handlers for Content-Encoding.
│   ├── BrotliDecoder() -> 'None'
│   ├── ByteChunker(chunk_size: 'int | None' = None) -> 'None'
│   ├── ContentDecoder(*args, **kwargs)
│   ├── DeflateDecoder() -> 'None'
│   ├── GZipDecoder() -> 'None'
│   ├── IdentityDecoder(*args, **kwargs)
│   ├── LineDecoder() -> 'None'
│   ├── MultiDecoder(children: 'typing.Sequence[ContentDecoder]') -> 'None'
│   ├── TextChunker(chunk_size: 'int | None' = None) -> 'None'
│   ├── TextDecoder(encoding: 'str' = 'utf-8') -> 'None'
│   └── ZStandardDecoder() -> 'None'
├── _exceptions  Our exception hierarchy:
│   └── request_context(request: 'Request | None' = None) -> 
│       'typing.Iterator[None]'
├── _main
├── _models
├── _multipart
│   ├── DataField(name: 'str', value: 'str | bytes | int | float | None') -> 
│   │   'None'
│   ├── FileField(name: 'str', value: 'FileTypes') -> 'None'
│   ├── MultipartStream(data: 'RequestData', files: 'RequestFiles', boundary: 
│   │   'bytes | None' = None) -> 'None'
│   └── get_multipart_boundary_from_content_type(content_type: 'bytes | None') 
│       -> 'bytes | None'
├── _status_codes
├── _transports
│   ├── asgi
│   │   ├── ASGIResponseStream(body: 'list[bytes]') -> 'None'
│   │   ├── create_event() -> 'Event'
│   │   └── is_running_trio() -> 'bool'
│   ├── base
│   ├── default  Custom transports, with nicely configured defaults.
│   │   ├── AsyncResponseStream(httpcore_stream: 'typing.AsyncIterable[bytes]') 
│   │   │   -> 'None'
│   │   ├── ResponseStream(httpcore_stream: 'typing.Iterable[bytes]') -> 'None'
│   │   └── map_httpcore_exceptions() -> 'typing.Iterator[None]'
│   ├── mock
│   └── wsgi
│       └── WSGIByteStream(result: 'typing.Iterable[bytes]') -> 'None'
├── _types  Type definitions for type checking purposes.
├── _urlparse  An implementation of `urlparse` that provides URL validation and 
│   normalization
│   ├── PERCENT(string: 'str') -> 'str'
│   ├── ParseResult(*args, **kwargs)
│   ├── encode_host(host: 'str') -> 'str'
│   ├── normalize_path(path: 'str') -> 'str'
│   ├── normalize_port(port: 'str | int | None', scheme: 'str') -> 'int | None'
│   ├── percent_encoded(string: 'str', safe: 'str') -> 'str'
│   ├── quote(string: 'str', safe: 'str') -> 'str'
│   ├── urlparse(url: 'str' = '', **kwargs: 'str | None') -> 'ParseResult'
│   └── validate_path(path: 'str', has_scheme: 'bool', has_authority: 'bool') ->
│       'None'
├── _urls
└── _utils
    ├── URLPattern(pattern: 'str') -> 'None'
    ├── get_environment_proxies() -> 'dict[str, str | None]'
    ├── is_ipv4_hostname(hostname: 'str') -> 'bool'
    ├── is_ipv6_hostname(hostname: 'str') -> 'bool'
    ├── peek_filelike_length(stream: 'typing.Any') -> 'int | None'
    ├── primitive_value_to_str(value: 'PrimitiveData') -> 'str'
    ├── to_bytes(value: 'str | bytes', encoding: 'str' = 'utf-8') -> 'bytes'
    ├── to_bytes_or_str(value: 'str', match_type_of: 'typing.AnyStr') -> 
    │   'typing.AnyStr'
    ├── to_str(value: 'str | bytes', encoding: 'str' = 'utf-8') -> 'str'
    └── unquote(value: 'str') -> 'str'
```
