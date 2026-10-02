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

Pass a dotted package or module name, such as `uv run pypatree mypkg.parsers`, to
inspect that namespace without importing unrelated submodules. Python still runs
the requested module's parent package initializers. Unknown and excluded scopes
raise an error.

Use `uv run pypatree --flat` for fully qualified names, one module or callable
per line. Flat output has no terminal wrapping and works with `rg` and other
line-oriented tools. Both formats support `--color auto|always|never`; auto colors
terminal output and emits plain text when piped. Add `--docstrings none` to omit
module prose.

Pypatree imports project code. Use it on trusted projects in their own Python
environment. Imports can have side effects or require optional dependencies.
An import failure produces a diagnostic on stderr; the command retains any
available output and exits nonzero. A callable whose signature is unavailable
appears as `name(...)` with a warning. `--verbose` adds discovery details and
tracebacks for command failures.

Discovery uses local editable-install metadata. Run from the Python package's
project directory, including the relevant subproject in a monorepo. Install it
with `uv pip install -e .` if needed. Conventional package, `src`, namespace-only,
and single-module layouts are supported. Where the installer supplies no package
names, discovery prefers regular packages, then namespaces, then module files;
this keeps adjacent build scripts out of package trees.

Output lists public functions and classes defined in each module. Class methods,
constants, and imported re-exports are outside this view.

```
pypatree  pypatree - Pretty-print a project's module tree.
├── __main__
│   ├── main() -> int
│   └── run(cfg: pypatree.config.Config) -> None
├── config  Configuration types for pypatree.
│   ├── Config(
│   │       scope: str | None,
│   │       exclude: str | None,
│   │       docstrings: pypatree.config.DocstringMode,
│   │       show_defaults: bool,
│   │       flat: bool,
│   │       color: Literal['auto', 'always', 'never'],
│   │       verbose: bool,
│   │   ) -> None
│   └── DocstringMode(value, names, *, module, qualname, type, start)
├── discovery
│   └── get_packages(
│           exclude: str | None,
│           scope: str | None,
│       ) -> dict[str, list[str]]
├── display
│   ├── print_tree(
│   │       pkg_name: str,
│   │       tree: pypatree.tree.Tree,
│   │       cfg: pypatree.config.Config,
│   │   ) -> None
│   └── render_tree(tree: pypatree.tree.Tree, prefix: str) -> list[str]
├── introspection
│   ├── format_signature(
│   │       obj: Callable | type,
│   │       show_defaults: bool,
│   │       *,
│   │       max_width: int | None,
│   │       name: str | None,
│   │   ) -> str
│   ├── get_module_docstring(modname: str, short: bool) -> str | None
│   ├── get_module_items(
│   │       modname: str,
│   │       exclude: str | None,
│   │       show_defaults: bool,
│   │       *,
│   │       max_width: int | None,
│   │   ) -> list[str]
│   ├── import_module(modname: str) -> module
│   └── safe_import(modname: str) -> module | None
└── tree
    ├── Tree(
    │       items: list[str],
    │       children: dict[str, Tree],
    │       docstring: str | None,
    │       failed: bool,
    │   ) -> None
    ├── build_tree(
    │       submods: list[str],
    │       pkg_name: str,
    │       exclude: str | None,
    │       show_defaults: bool,
    │       *,
    │       max_width: int | None,
    │   ) -> pypatree.tree.Tree
    └── get_subtree(
            tree: pypatree.tree.Tree,
            path: list[str],
        ) -> pypatree.tree.Tree | None
```

Flat output for the introspection module:
```
pypatree.introspection
pypatree.introspection.format_signature(obj: Callable | type, show_defaults: bool, *, max_width: int | None, name: str | None) -> str
pypatree.introspection.get_module_docstring(modname: str, short: bool) -> str | None
pypatree.introspection.get_module_items(modname: str, exclude: str | None, show_defaults: bool, *, max_width: int | None) -> list[str]
pypatree.introspection.import_module(modname: str) -> module
pypatree.introspection.safe_import(modname: str) -> module | None
```

Run `pypatree --help` for options:
```
usage: pypatree [-h] [OPTIONS] [MODULE]

Display module tree with public functions/classes.

╭─ positional arguments ─────────────────────────────────────────────────────╮
│ [MODULE]                Module path to scope to (e.g., 'mypkg.submodule'). │
│                         (default: None)                                    │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ options ──────────────────────────────────────────────────────────────────╮
│ -h, --help              show this help message and exit                    │
│ --exclude {None}|STR    Regex to exclude module segments (default: test    │
│                         modules). Use '' for none. (default:               │
│                         '^tests?$|^test_')                                 │
│ --docstrings {none,short,full}                                             │
│                         Show module docstrings: none, short (first line),  │
│                         or full. (default: short)                          │
│ --show-defaults, --no-show-defaults                                        │
│                         Show default argument values in signatures.        │
│                         (default: False)                                   │
│ --flat, --no-flat       Print fully qualified names, one item per line,    │
│                         without tree guides or wrapping. (default: False)  │
│ --color {auto,always,never}                                                │
│                         Color policy for either output format. Auto        │
│                         detects the terminal. (default: auto)              │
│ --verbose, --no-verbose                                                    │
│                         Enable debug logging to stderr. (default: False)   │
╰────────────────────────────────────────────────────────────────────────────╯
```

Example on [httpx](https://github.com/encode/httpx):
Source: commit `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`, Python 3.9.25.
```
httpx
├── ASGITransport(
│       app: _ASGIApp,
│       raise_app_exceptions: bool,
│       root_path: str,
│       client: tuple[str, int],
│   ) -> None
├── AsyncBaseTransport()
├── AsyncByteStream()
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
├── Auth()
├── BaseTransport()
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
├── SyncByteStream()
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
├── codes(value, names, *, module, qualname, type, start)
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
│   ├── ClientState(value, names, *, module, qualname, type, start)
│   └── UseClientDefault()
├── _config
│   └── UnsetType()
├── _content
│   ├── AsyncIteratorByteStream(stream: AsyncIterable[bytes]) -> None
│   ├── IteratorByteStream(stream: Iterable[bytes]) -> None
│   ├── UnattachedStream()
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
│   ├── ContentDecoder()
│   ├── DeflateDecoder() -> None
│   ├── GZipDecoder() -> None
│   ├── IdentityDecoder()
│   ├── LineDecoder() -> None
│   ├── MultiDecoder(children: typing.Sequence[ContentDecoder]) -> None
│   ├── TextChunker(chunk_size: int | None) -> None
│   ├── TextDecoder(encoding: str) -> None
│   └── ZStandardDecoder() -> None
├── _exceptions  Our exception hierarchy:
│   └── request_context(request: Request | None) -> typing.Iterator[None]
├── _main
│   ├── download_response(response: Response, download: typing.BinaryIO) -> None
│   ├── format_certificate(cert: _PeerCertRetDictType) -> str
│   ├── format_request_headers(request: httpcore.Request, http2: bool) -> str
│   ├── format_response_headers(
│   │       http_version: bytes,
│   │       status: int,
│   │       reason_phrase: bytes | None,
│   │       headers: list[tuple[bytes, bytes]],
│   │   ) -> str
│   ├── get_lexer_for_response(response: Response) -> str
│   ├── handle_help(
│   │       ctx: click.Context,
│   │       param: click.Option | click.Parameter,
│   │       value: typing.Any,
│   │   ) -> None
│   ├── print_help() -> None
│   ├── print_request_headers(request: httpcore.Request, http2: bool) -> None
│   ├── print_response(response: Response) -> None
│   ├── print_response_headers(
│   │       http_version: bytes,
│   │       status: int,
│   │       reason_phrase: bytes | None,
│   │       headers: list[tuple[bytes, bytes]],
│   │   ) -> None
│   ├── trace(
│   │       name: str,
│   │       info: typing.Mapping[str, typing.Any],
│   │       verbose: bool,
│   │   ) -> None
│   ├── validate_auth(
│   │       ctx: click.Context,
│   │       param: click.Option | click.Parameter,
│   │       value: typing.Any,
│   │   ) -> typing.Any
│   └── validate_json(
│           ctx: click.Context,
│           param: click.Option | click.Parameter,
│           value: typing.Any,
│       ) -> typing.Any
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
│   │   ├── AsyncResponseStream(
│   │   │       httpcore_stream: typing.AsyncIterable[bytes],
│   │   │   ) -> None
│   │   ├── ResponseStream(httpcore_stream: typing.Iterable[bytes]) -> None
│   │   └── map_httpcore_exceptions() -> typing.Iterator[None]
│   ├── mock
│   └── wsgi
│       └── WSGIByteStream(result: typing.Iterable[bytes]) -> None
├── _types  Type definitions for type checking purposes.
├── _urlparse  An implementation of `urlparse` that provides URL validation and
│   normalization
│   ├── PERCENT(string: str) -> str
│   ├── ParseResult(
│   │       scheme: ForwardRef('str'),
│   │       userinfo: ForwardRef('str'),
│   │       host: ForwardRef('str'),
│   │       port: ForwardRef('int | None'),
│   │       path: ForwardRef('str'),
│   │       query: ForwardRef('str | None'),
│   │       fragment: ForwardRef('str | None'),
│   │   )
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
    ├── to_bytes_or_str(
    │       value: str,
    │       match_type_of: typing.AnyStr,
    │   ) -> typing.AnyStr
    ├── to_str(value: str | bytes, encoding: str) -> str
    └── unquote(value: str) -> str
```

Python API: `build_tree()` returns a `Tree` dataclass with `items`, `children`,
`docstring`, and `failed` fields. In 0.5, this replaces the dictionary containing
the reserved `__items__` key. Read `tree.items` and `tree.children[name]` when
updating callers from 0.4.

Development commands live in `justfile`. Run `uv run just` for local checks and
README generation. Refresh the pinned showcase dependencies with
`uv run python scripts/regen_readme.py --update-constraints`.
