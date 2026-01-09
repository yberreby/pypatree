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
│   ├── Config(
│   │       scope: Optional[str],
│   │       exclude: Optional[str],
│   │       docstrings: pypatree.config.DocstringMode,
│   │       show_defaults: bool,
│   │   ) -> None
│   └── DocstringMode(*args, **kwargs)
├── discovery
│   └── get_packages(exclude: Optional[str]) -> dict[str, list[str]]
├── display
│   ├── print_tree(
│   │       pkg_name: str,
│   │       tree: dict[str, typing.Any],
│   │       cfg: pypatree.config.Config,
│   │   ) -> None
│   └── render_tree(tree: dict[str, typing.Any], prefix: str) -> list[str]
├── introspection
│   ├── format_signature(obj: Union[Callable, type], show_defaults: bool) -> str
│   ├── get_module_docstring(modname: str, short: bool) -> Optional[str]
│   ├── get_module_items(
│   │       modname: str,
│   │       exclude: Optional[str],
│   │       show_defaults: bool,
│   │   ) -> list[str]
│   └── safe_import(modname: str) -> Optional[module]
└── tree
    ├── build_tree(
    │       submods: list[str],
    │       pkg_name: str,
    │       exclude: Optional[str],
    │       show_defaults: bool,
    │   ) -> dict[str, typing.Any]
    └── get_subtree(
            tree: dict[str, typing.Any],
            path: list[str],
        ) -> Optional[dict[str, Any]]
```

Run `pypatree --help` for options:
```
usage: pypatree [-h] [OPTIONS] [MODULE]

Display module tree with public functions/classes.

╭─ positional arguments ─────────────────────────────────────────────────────╮
│ [MODULE]                                                                   │
│     Module path to scope to (e.g., 'mypkg.submodule'). (default: None)     │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ options ──────────────────────────────────────────────────────────────────╮
│ -h, --help                                                                 │
│     show this help message and exit                                        │
│ --exclude {None}|STR                                                       │
│     Regex to exclude module segments (default: test modules). Use '' for   │
│     none. (default: '^test$|^test_')                                       │
│ --docstrings {none,short,full}                                             │
│     Show module docstrings: none, short (first line), or full. (default:   │
│     short)                                                                 │
│ --show-defaults, --no-show-defaults                                        │
│     Show default argument values in signatures. (default: False)           │
╰────────────────────────────────────────────────────────────────────────────╯
```

Example on [httpx](https://github.com/encode/httpx):
```
httpx
├── ASGITransport(
│       app: _ASGIApp,
│       raise_app_exceptions: bool,
│       root_path: str,
│       client: tuple[str, int],
│   ) -> None
├── AsyncBaseTransport(*args, **kwargs)
├── AsyncByteStream(*args, **kwargs)
├── AsyncClient(
│       *,
│       auth: AuthTypes | None,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       verify: ssl.SSLContext | str | bool,
│       cert: CertTypes | None,
│       http1: bool,
│       http2: bool,
│       proxy: ProxyTypes | None,
│       mounts: None | typing.Mapping[str, AsyncBaseTransport | None],
│       timeout: TimeoutTypes,
│       follow_redirects: bool,
│       limits: Limits,
│       max_redirects: int,
│       event_hooks: None | typing.Mapping[str, list[EventHook]],
│       base_url: URL | str,
│       transport: AsyncBaseTransport | None,
│       trust_env: bool,
│       default_encoding: str | typing.Callable[[bytes], str],
│   ) -> None
├── AsyncHTTPTransport(
│       verify: ssl.SSLContext | str | bool,
│       cert: CertTypes | None,
│       trust_env: bool,
│       http1: bool,
│       http2: bool,
│       limits: Limits,
│       proxy: ProxyTypes | None,
│       uds: str | None,
│       local_address: str | None,
│       retries: int,
│       socket_options: typing.Iterable[SOCKET_OPTION] | None,
│   ) -> None
├── Auth(*args, **kwargs)
├── BaseTransport(*args, **kwargs)
├── BasicAuth(username: str | bytes, password: str | bytes) -> None
├── ByteStream(stream: bytes) -> None
├── Client(
│       *,
│       auth: AuthTypes | None,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       verify: ssl.SSLContext | str | bool,
│       cert: CertTypes | None,
│       trust_env: bool,
│       http1: bool,
│       http2: bool,
│       proxy: ProxyTypes | None,
│       mounts: None | typing.Mapping[str, BaseTransport | None],
│       timeout: TimeoutTypes,
│       follow_redirects: bool,
│       limits: Limits,
│       max_redirects: int,
│       event_hooks: None | typing.Mapping[str, list[EventHook]],
│       base_url: URL | str,
│       transport: BaseTransport | None,
│       default_encoding: str | typing.Callable[[bytes], str],
│   ) -> None
├── CloseError(message: str, *, request: Request | None) -> None
├── ConnectError(message: str, *, request: Request | None) -> None
├── ConnectTimeout(message: str, *, request: Request | None) -> None
├── CookieConflict(message: str) -> None
├── Cookies(cookies: CookieTypes | None) -> None
├── DecodingError(message: str, *, request: Request | None) -> None
├── DigestAuth(username: str | bytes, password: str | bytes) -> None
├── FunctionAuth(func: typing.Callable[[Request], Request]) -> None
├── HTTPError(message: str) -> None
├── HTTPStatusError(
│       message: str,
│       *,
│       request: Request,
│       response: Response,
│   ) -> None
├── HTTPTransport(
│       verify: ssl.SSLContext | str | bool,
│       cert: CertTypes | None,
│       trust_env: bool,
│       http1: bool,
│       http2: bool,
│       limits: Limits,
│       proxy: ProxyTypes | None,
│       uds: str | None,
│       local_address: str | None,
│       retries: int,
│       socket_options: typing.Iterable[SOCKET_OPTION] | None,
│   ) -> None
├── Headers(headers: HeaderTypes | None, encoding: str | None) -> None
├── InvalidURL(message: str) -> None
├── Limits(
│       *,
│       max_connections: int | None,
│       max_keepalive_connections: int | None,
│       keepalive_expiry: float | None,
│   ) -> None
├── LocalProtocolError(message: str, *, request: Request | None) -> None
├── MockTransport(handler: SyncHandler | AsyncHandler) -> None
├── NetRCAuth(file: str | None) -> None
├── NetworkError(message: str, *, request: Request | None) -> None
├── PoolTimeout(message: str, *, request: Request | None) -> None
├── ProtocolError(message: str, *, request: Request | None) -> None
├── Proxy(
│       url: URL | str,
│       *,
│       ssl_context: ssl.SSLContext | None,
│       auth: tuple[str, str] | None,
│       headers: HeaderTypes | None,
│   ) -> None
├── ProxyError(message: str, *, request: Request | None) -> None
├── QueryParams(*args: QueryParamTypes | None, **kwargs: typing.Any) -> None
├── ReadError(message: str, *, request: Request | None) -> None
├── ReadTimeout(message: str, *, request: Request | None) -> None
├── RemoteProtocolError(message: str, *, request: Request | None) -> None
├── Request(
│       method: str,
│       url: URL | str,
│       *,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       content: RequestContent | None,
│       data: RequestData | None,
│       files: RequestFiles | None,
│       json: typing.Any | None,
│       stream: SyncByteStream | AsyncByteStream | None,
│       extensions: RequestExtensions | None,
│   ) -> None
├── RequestError(message: str, *, request: Request | None) -> None
├── RequestNotRead() -> None
├── Response(
│       status_code: int,
│       *,
│       headers: HeaderTypes | None,
│       content: ResponseContent | None,
│       text: str | None,
│       html: str | None,
│       json: typing.Any,
│       stream: SyncByteStream | AsyncByteStream | None,
│       request: Request | None,
│       extensions: ResponseExtensions | None,
│       history: list[Response] | None,
│       default_encoding: str | typing.Callable[[bytes], str],
│   ) -> None
├── ResponseNotRead() -> None
├── StreamClosed() -> None
├── StreamConsumed() -> None
├── StreamError(message: str) -> None
├── SyncByteStream(*args, **kwargs)
├── Timeout(
│       timeout: TimeoutTypes | UnsetType,
│       *,
│       connect: None | float | UnsetType,
│       read: None | float | UnsetType,
│       write: None | float | UnsetType,
│       pool: None | float | UnsetType,
│   ) -> None
├── TimeoutException(message: str, *, request: Request | None) -> None
├── TooManyRedirects(message: str, *, request: Request | None) -> None
├── TransportError(message: str, *, request: Request | None) -> None
├── URL(url: URL | str, **kwargs: typing.Any) -> None
├── UnsupportedProtocol(message: str, *, request: Request | None) -> None
├── WSGITransport(
│       app: WSGIApplication,
│       raise_app_exceptions: bool,
│       script_name: str,
│       remote_addr: str,
│       wsgi_errors: typing.TextIO | None,
│   ) -> None
├── WriteError(message: str, *, request: Request | None) -> None
├── WriteTimeout(message: str, *, request: Request | None) -> None
├── codes(*args, **kwds)
├── create_ssl_context(
│       verify: ssl.SSLContext | str | bool,
│       cert: CertTypes | None,
│       trust_env: bool,
│   ) -> ssl.SSLContext
├── delete(
│       url: URL | str,
│       *,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       follow_redirects: bool,
│       timeout: TimeoutTypes,
│       verify: ssl.SSLContext | str | bool,
│       trust_env: bool,
│   ) -> Response
├── get(
│       url: URL | str,
│       *,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       timeout: TimeoutTypes,
│       trust_env: bool,
│   ) -> Response
├── head(
│       url: URL | str,
│       *,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       timeout: TimeoutTypes,
│       trust_env: bool,
│   ) -> Response
├── main() -> None
├── options(
│       url: URL | str,
│       *,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       timeout: TimeoutTypes,
│       trust_env: bool,
│   ) -> Response
├── patch(
│       url: URL | str,
│       *,
│       content: RequestContent | None,
│       data: RequestData | None,
│       files: RequestFiles | None,
│       json: typing.Any | None,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       timeout: TimeoutTypes,
│       trust_env: bool,
│   ) -> Response
├── post(
│       url: URL | str,
│       *,
│       content: RequestContent | None,
│       data: RequestData | None,
│       files: RequestFiles | None,
│       json: typing.Any | None,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       timeout: TimeoutTypes,
│       trust_env: bool,
│   ) -> Response
├── put(
│       url: URL | str,
│       *,
│       content: RequestContent | None,
│       data: RequestData | None,
│       files: RequestFiles | None,
│       json: typing.Any | None,
│       params: QueryParamTypes | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       timeout: TimeoutTypes,
│       trust_env: bool,
│   ) -> Response
├── request(
│       method: str,
│       url: URL | str,
│       *,
│       params: QueryParamTypes | None,
│       content: RequestContent | None,
│       data: RequestData | None,
│       files: RequestFiles | None,
│       json: typing.Any | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       timeout: TimeoutTypes,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       trust_env: bool,
│   ) -> Response
├── stream(
│       method: str,
│       url: URL | str,
│       *,
│       params: QueryParamTypes | None,
│       content: RequestContent | None,
│       data: RequestData | None,
│       files: RequestFiles | None,
│       json: typing.Any | None,
│       headers: HeaderTypes | None,
│       cookies: CookieTypes | None,
│       auth: AuthTypes | None,
│       proxy: ProxyTypes | None,
│       timeout: TimeoutTypes,
│       follow_redirects: bool,
│       verify: ssl.SSLContext | str | bool,
│       trust_env: bool,
│   ) -> typing.Iterator[Response]
├── __version__
├── _api
├── _auth
├── _client
│   ├── BaseClient(
│   │       *,
│   │       auth: AuthTypes | None,
│   │       params: QueryParamTypes | None,
│   │       headers: HeaderTypes | None,
│   │       cookies: CookieTypes | None,
│   │       timeout: TimeoutTypes,
│   │       follow_redirects: bool,
│   │       max_redirects: int,
│   │       event_hooks: None | typing.Mapping[str, list[EventHook]],
│   │       base_url: URL | str,
│   │       trust_env: bool,
│   │       default_encoding: str | typing.Callable[[bytes], str],
│   │   ) -> None
│   ├── BoundAsyncStream(
│   │       stream: AsyncByteStream,
│   │       response: Response,
│   │       start: float,
│   │   ) -> None
│   ├── BoundSyncStream(
│   │       stream: SyncByteStream,
│   │       response: Response,
│   │       start: float,
│   │   ) -> None
│   ├── ClientState(*args, **kwds)
│   └── UseClientDefault(*args, **kwargs)
├── _config
│   └── UnsetType(*args, **kwargs)
├── _content
│   ├── AsyncIteratorByteStream(stream: AsyncIterable[bytes]) -> None
│   ├── IteratorByteStream(stream: Iterable[bytes]) -> None
│   ├── UnattachedStream(*args, **kwargs)
│   ├── encode_content(
│   │       content: str | bytes | Iterable[bytes] | AsyncIterable[bytes],
│   │   ) -> tuple[dict[str, str], SyncByteStream | AsyncByteStream]
│   ├── encode_html(html: str) -> tuple[dict[str, str], ByteStream]
│   ├── encode_json(json: Any) -> tuple[dict[str, str], ByteStream]
│   ├── encode_multipart_data(
│   │       data: RequestData,
│   │       files: RequestFiles,
│   │       boundary: bytes | None,
│   │   ) -> tuple[dict[str, str], MultipartStream]
│   ├── encode_request(
│   │       content: RequestContent | None,
│   │       data: RequestData | None,
│   │       files: RequestFiles | None,
│   │       json: Any | None,
│   │       boundary: bytes | None,
│   │   ) -> tuple[dict[str, str], SyncByteStream | AsyncByteStream]
│   ├── encode_response(
│   │       content: ResponseContent | None,
│   │       text: str | None,
│   │       html: str | None,
│   │       json: Any | None,
│   │   ) -> tuple[dict[str, str], SyncByteStream | AsyncByteStream]
│   ├── encode_text(text: str) -> tuple[dict[str, str], ByteStream]
│   └── encode_urlencoded_data(
│           data: RequestData,
│       ) -> tuple[dict[str, str], ByteStream]
├── _decoders  Handlers for Content-Encoding.
│   ├── BrotliDecoder() -> None
│   ├── ByteChunker(chunk_size: int | None) -> None
│   ├── ContentDecoder(*args, **kwargs)
│   ├── DeflateDecoder() -> None
│   ├── GZipDecoder() -> None
│   ├── IdentityDecoder(*args, **kwargs)
│   ├── LineDecoder() -> None
│   ├── MultiDecoder(children: typing.Sequence[ContentDecoder]) -> None
│   ├── TextChunker(chunk_size: int | None) -> None
│   ├── TextDecoder(encoding: str) -> None
│   └── ZStandardDecoder() -> None
├── _exceptions  Our exception hierarchy:
│   └── request_context(request: Request | None) -> typing.Iterator[None]
├── _main
├── _models
├── _multipart
│   ├── DataField(name: str, value: str | bytes | int | float | None) -> None
│   ├── FileField(name: str, value: FileTypes) -> None
│   ├── MultipartStream(
│   │       data: RequestData,
│   │       files: RequestFiles,
│   │       boundary: bytes | None,
│   │   ) -> None
│   └── get_multipart_boundary_from_content_type(
│           content_type: bytes | None,
│       ) -> bytes | None
├── _status_codes
├── _transports
│   ├── asgi
│   │   ├── ASGIResponseStream(body: list[bytes]) -> None
│   │   ├── create_event() -> Event
│   │   └── is_running_trio() -> bool
│   ├── base
│   ├── default  Custom transports, with nicely configured defaults.
│   │   ├── AsyncResponseStream(httpcore_stream: typing.AsyncIterable[bytes]) ->
│   │   │   None
│   │   ├── ResponseStream(httpcore_stream: typing.Iterable[bytes]) -> None
│   │   └── map_httpcore_exceptions() -> typing.Iterator[None]
│   ├── mock
│   └── wsgi
│       └── WSGIByteStream(result: typing.Iterable[bytes]) -> None
├── _types  Type definitions for type checking purposes.
├── _urlparse  An implementation of `urlparse` that provides URL validation and 
│   normalization
│   ├── PERCENT(string: str) -> str
│   ├── ParseResult(*args, **kwargs)
│   ├── encode_host(host: str) -> str
│   ├── normalize_path(path: str) -> str
│   ├── normalize_port(port: str | int | None, scheme: str) -> int | None
│   ├── percent_encoded(string: str, safe: str) -> str
│   ├── quote(string: str, safe: str) -> str
│   ├── urlparse(url: str, **kwargs: str | None) -> ParseResult
│   └── validate_path(path: str, has_scheme: bool, has_authority: bool) -> None
├── _urls
└── _utils
    ├── URLPattern(pattern: str) -> None
    ├── get_environment_proxies() -> dict[str, str | None]
    ├── is_ipv4_hostname(hostname: str) -> bool
    ├── is_ipv6_hostname(hostname: str) -> bool
    ├── peek_filelike_length(stream: typing.Any) -> int | None
    ├── primitive_value_to_str(value: PrimitiveData) -> str
    ├── to_bytes(value: str | bytes, encoding: str) -> bytes
    ├── to_bytes_or_str(value: str, match_type_of: typing.AnyStr) -> 
    │   typing.AnyStr
    ├── to_str(value: str | bytes, encoding: str) -> str
    └── unquote(value: str) -> str
tests
├── client
├── common
├── concurrency
├── conftest
└── models
```
