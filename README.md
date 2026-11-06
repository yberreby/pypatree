# pypatree

[![CI](https://github.com/yberreby/pypatree/actions/workflows/ci.yml/badge.svg)](https://github.com/yberreby/pypatree/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pypatree)](https://pypi.org/project/pypatree/)
[![Python](https://img.shields.io/pypi/pyversions/pypatree)](https://pypi.org/project/pypatree/)
[![License](https://img.shields.io/pypi/l/pypatree?v=2)](https://github.com/yberreby/pypatree/blob/main/LICENSE)

Pretty-print a project's module tree with syntax-highlighted signatures.

```bash
uvx pypatree@latest
uvx pypatree@latest --flat
```

Run from a Python project or a repository containing Python subprojects.
Pypatree reads local source with [Griffe](https://mkdocstrings.github.io/griffe/).
The project and its dependencies do not need to be installed, and its code is
not executed. Pass a dotted package or module name, such as
`uvx pypatree@latest mypkg.parsers`, to inspect one subtree. Unknown scopes and
scopes inside excluded modules raise an error.

Use `uv run pypatree --flat` for fully qualified names, one module or callable
per line. Flat output has no terminal wrapping and works with `rg` and other
line-oriented tools. Both formats support `--color auto|always|never`; auto colors
terminal output and emits plain text when piped. Add `--docstrings none` to omit
module prose.

Source inspection shows declared functions, classes, and dataclass constructors.
Defaults remain source expressions; decorators and metaclasses can change the
runtime API. Classes without a local or synthesized constructor appear as `name(...)`.
Parsing requires a Python version that supports the project's syntax; select it
with `uvx --python 3.14 pypatree@latest` when needed. A parse failure produces a
diagnostic on stderr, preserves available output, and exits nonzero.

Discovery supports conventional package, `src`, namespace-only, and single-module
layouts. From a repository root, it searches for subprojects with `pyproject.toml`,
`setup.py`, or `setup.cfg`, stopping at each project boundary. The search skips
hidden, Git-ignored, and test directories, `node_modules`, and virtual
environments. Within each project, discovery selects the modules its build would
ship: those declared in hatch, setuptools, flit, uv, poetry, pdm, or maturin
configuration; else the contents of `src` or a declared source directory; else
the module named after the project; else, as setuptools does, its packages, then
namespaces, then module files, passing over names such as `docs` and `examples`.
Duplicate package names require running from the intended subproject.

Use `uv run pypatree --runtime` for APIs created dynamically. Install pypatree and
the inspected project into the same environment (`uv add --dev pypatree` and
`uv pip install -e .`). Runtime discovery uses editable-install metadata and
imports trusted project code, including parent package initializers but not
`__main__` scripts. Imports can have side effects or require optional
dependencies. Modules that fail to import are marked `[inspection failed]` and
reported on stderr; the rest of the output is kept and pypatree exits nonzero.
Unavailable signatures appear as `name(...)` with a warning. `--verbose` adds
discovery details and tracebacks.

Output lists public functions and classes defined in each module. Class methods,
constants, and imported re-exports are outside this view.

```
pypatree  pypatree - Pretty-print a project's module tree.
├── __main__
│   ├── main() -> int
│   └── run(cfg: Config) -> bool
├── build_config  Read what a project's build configuration declares about its
│   top-level modules.
│   ├── BuildConfig(
│   │       name: Optional[str] = ...,
│   │       include: tuple[str, ...] = ...,
│   │       roots: tuple[PurePosixPath, ...] = ...,
│   │   )
│   ├── normalize(name: str) -> str
│   └── read_build_config(project: Path) -> BuildConfig
├── config  Command-line options and the module selection they describe.
│   ├── Config(
│   │       scope: Optional[str] = ...,
│   │       exclude: str = ...,
│   │       docstrings: Literal['none', 'short', 'full'] = ...,
│   │       show_defaults: bool = ...,
│   │       flat: bool = ...,
│   │       color: Literal['auto', 'always', 'never'] = ...,
│   │       verbose: bool = ...,
│   │       runtime: bool = ...,
│   │   )
│   ├── Exclusion(regex: str = ...)
│   └── select_modules(
│           packages: Collection[str],
│           scope: Optional[str],
│           exclude: Exclusion,
│       ) -> list[str]
├── display  Render module trees as Rich trees or as qualified lines.
│   └── print_tree(name: str, tree: Tree, cfg: Config) -> None
├── introspection  Signatures of live functions and classes.
│   ├── module_items(
│   │       module: ModuleType,
│   │       *,
│   │       exclude: Exclusion,
│   │       show_defaults: bool,
│   │   ) -> list[Signature]
│   └── signature_of(
│           obj: Union[Callable[..., object], type],
│           *,
│           name: Optional[str] = ...,
│           show_defaults: bool,
│       ) -> Signature
├── layout  Locate Python modules on disk without importing them.
│   ├── is_package(directory: Path) -> bool
│   ├── modules(directory: Path) -> dict[str, Path]
│   └── project_packages(project: Path) -> dict[str, Path]
├── runtime  Inspect editable-installed packages by importing them.
│   ├── editable_packages(project: Path) -> list[str]
│   ├── import_module(name: str) -> ModuleType
│   └── runtime_trees(
│           root: Path,
│           *,
│           scope: Optional[str] = ...,
│           exclude: Exclusion = ...,
│           show_defaults: bool = ...,
│       ) -> dict[str, Tree]
├── signature  Call signatures, independent of how they were inspected.
│   ├── Parameter(
│   │       name: str,
│   │       kind: Kind,
│   │       annotation: Optional[str] = ...,
│   │       default: Optional[str] = ...,
│   │   )
│   └── Signature(
│           name: str,
│           parameters: Optional[tuple[Parameter, ...]],
│           returns: Optional[str] = ...,
│       )
├── source  Read local Python source with Griffe, without importing it.
│   ├── source_packages(root: Path) -> dict[str, Path]
│   └── source_trees(
│           root: Path,
│           *,
│           scope: Optional[str] = ...,
│           exclude: Exclusion = ...,
│           show_defaults: bool = ...,
│       ) -> dict[str, Tree]
└── tree  Inspection results shared by the source and runtime backends.
    └── Tree(
            items: list[Signature] = ...,
            children: dict[str, Tree] = ...,
            docstring: Optional[str] = ...,
            error: Optional[str] = ...,
        )
```

Flat output for the introspection module:
```
pypatree.introspection  Signatures of live functions and classes.
pypatree.introspection.module_items(module: ModuleType, *, exclude: Exclusion, show_defaults: bool) -> list[Signature]
pypatree.introspection.signature_of(obj: Union[Callable[..., object], type], *, name: Optional[str] = ..., show_defaults: bool) -> Signature
```

Run `pypatree --help` for options:
```
usage: pypatree [-h] [OPTIONS] [MODULE]

Display module tree with public functions/classes.

╭─ positional arguments ─────────────────────────────────────────────────────╮
│ [MODULE]                                                                   │
│     Dotted module to inspect, such as 'mypkg.parsers'. (default: None)     │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ options ──────────────────────────────────────────────────────────────────╮
│ -h, --help                                                                 │
│     show this help message and exit                                        │
│ --exclude STR                                                              │
│     Regex excluding matching module segments and item names. '' disables   │
│     it. (default: '^tests?$|^test_')                                       │
│ --docstrings {none,short,full}                                             │
│     Module docstrings to show: none, the first line, or all of it.         │
│     (default: short)                                                       │
│ --show-defaults, --no-show-defaults                                        │
│     Show default values in signatures. Otherwise, = ... marks optional     │
│     parameters. (default: False)                                           │
│ --flat, --no-flat                                                          │
│     Print fully qualified names, one item per line, without tree guides or │
│     wrapping. (default: False)                                             │
│ --color {auto,always,never}                                                │
│     Color policy for either output format. Auto detects the terminal.      │
│     (default: auto)                                                        │
│ --verbose, --no-verbose                                                    │
│     Log discovery details and tracebacks to stderr. (default: False)       │
│ --runtime, --no-runtime                                                    │
│     Import editable-installed code in this environment. Default: read      │
│     local source. (default: False)                                         │
╰────────────────────────────────────────────────────────────────────────────╯
```

Example on [httpx](https://github.com/encode/httpx):
Source: commit `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`, Python 3.9.25.
```
httpx
├── main() -> None
├── __version__
├── _api
│   ├── delete(
│   │       url: URL | str,
│   │       *,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       follow_redirects: bool = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   ├── get(
│   │       url: URL | str,
│   │       *,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       follow_redirects: bool = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   ├── head(
│   │       url: URL | str,
│   │       *,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       follow_redirects: bool = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   ├── options(
│   │       url: URL | str,
│   │       *,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       follow_redirects: bool = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   ├── patch(
│   │       url: URL | str,
│   │       *,
│   │       content: RequestContent | None = ...,
│   │       data: RequestData | None = ...,
│   │       files: RequestFiles | None = ...,
│   │       json: typing.Any | None = ...,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       follow_redirects: bool = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   ├── post(
│   │       url: URL | str,
│   │       *,
│   │       content: RequestContent | None = ...,
│   │       data: RequestData | None = ...,
│   │       files: RequestFiles | None = ...,
│   │       json: typing.Any | None = ...,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       follow_redirects: bool = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   ├── put(
│   │       url: URL | str,
│   │       *,
│   │       content: RequestContent | None = ...,
│   │       data: RequestData | None = ...,
│   │       files: RequestFiles | None = ...,
│   │       json: typing.Any | None = ...,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       follow_redirects: bool = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   ├── request(
│   │       method: str,
│   │       url: URL | str,
│   │       *,
│   │       params: QueryParamTypes | None = ...,
│   │       content: RequestContent | None = ...,
│   │       data: RequestData | None = ...,
│   │       files: RequestFiles | None = ...,
│   │       json: typing.Any | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       auth: AuthTypes | None = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       follow_redirects: bool = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       trust_env: bool = ...,
│   │   ) -> Response
│   └── stream(
│           method: str,
│           url: URL | str,
│           *,
│           params: QueryParamTypes | None = ...,
│           content: RequestContent | None = ...,
│           data: RequestData | None = ...,
│           files: RequestFiles | None = ...,
│           json: typing.Any | None = ...,
│           headers: HeaderTypes | None = ...,
│           cookies: CookieTypes | None = ...,
│           auth: AuthTypes | None = ...,
│           proxy: ProxyTypes | None = ...,
│           timeout: TimeoutTypes = ...,
│           follow_redirects: bool = ...,
│           verify: ssl.SSLContext | str | bool = ...,
│           trust_env: bool = ...,
│       ) -> typing.Iterator[Response]
├── _auth
│   ├── Auth(...)
│   ├── BasicAuth(username: str | bytes, password: str | bytes)
│   ├── DigestAuth(username: str | bytes, password: str | bytes)
│   ├── FunctionAuth(func: typing.Callable[[Request], Request])
│   └── NetRCAuth(file: str | None = ...)
├── _client
│   ├── AsyncClient(
│   │       *,
│   │       auth: AuthTypes | None = ...,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       cert: CertTypes | None = ...,
│   │       http1: bool = ...,
│   │       http2: bool = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       mounts: None | typing.Mapping[str, AsyncBaseTransport | None] = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       follow_redirects: bool = ...,
│   │       limits: Limits = ...,
│   │       max_redirects: int = ...,
│   │       event_hooks: None | typing.Mapping[str, list[EventHook]] = ...,
│   │       base_url: URL | str = ...,
│   │       transport: AsyncBaseTransport | None = ...,
│   │       trust_env: bool = ...,
│   │       default_encoding: str | typing.Callable[[bytes], str] = ...,
│   │   )
│   ├── BaseClient(
│   │       *,
│   │       auth: AuthTypes | None = ...,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       follow_redirects: bool = ...,
│   │       max_redirects: int = ...,
│   │       event_hooks: None | typing.Mapping[str, list[EventHook]] = ...,
│   │       base_url: URL | str = ...,
│   │       trust_env: bool = ...,
│   │       default_encoding: str | typing.Callable[[bytes], str] = ...,
│   │   )
│   ├── BoundAsyncStream(
│   │       stream: AsyncByteStream,
│   │       response: Response,
│   │       start: float,
│   │   )
│   ├── BoundSyncStream(
│   │       stream: SyncByteStream,
│   │       response: Response,
│   │       start: float,
│   │   )
│   ├── Client(
│   │       *,
│   │       auth: AuthTypes | None = ...,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       verify: ssl.SSLContext | str | bool = ...,
│   │       cert: CertTypes | None = ...,
│   │       trust_env: bool = ...,
│   │       http1: bool = ...,
│   │       http2: bool = ...,
│   │       proxy: ProxyTypes | None = ...,
│   │       mounts: None | typing.Mapping[str, BaseTransport | None] = ...,
│   │       timeout: TimeoutTypes = ...,
│   │       follow_redirects: bool = ...,
│   │       limits: Limits = ...,
│   │       max_redirects: int = ...,
│   │       event_hooks: None | typing.Mapping[str, list[EventHook]] = ...,
│   │       base_url: URL | str = ...,
│   │       transport: BaseTransport | None = ...,
│   │       default_encoding: str | typing.Callable[[bytes], str] = ...,
│   │   )
│   ├── ClientState(...)
│   └── UseClientDefault(...)
├── _config
│   ├── Limits(
│   │       *,
│   │       max_connections: int | None = ...,
│   │       max_keepalive_connections: int | None = ...,
│   │       keepalive_expiry: float | None = ...,
│   │   )
│   ├── Proxy(
│   │       url: URL | str,
│   │       *,
│   │       ssl_context: ssl.SSLContext | None = ...,
│   │       auth: tuple[str, str] | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │   )
│   ├── Timeout(
│   │       timeout: TimeoutTypes | UnsetType = ...,
│   │       *,
│   │       connect: None | float | UnsetType = ...,
│   │       read: None | float | UnsetType = ...,
│   │       write: None | float | UnsetType = ...,
│   │       pool: None | float | UnsetType = ...,
│   │   )
│   ├── UnsetType(...)
│   └── create_ssl_context(
│           verify: ssl.SSLContext | str | bool = ...,
│           cert: CertTypes | None = ...,
│           trust_env: bool = ...,
│       ) -> ssl.SSLContext
├── _content
│   ├── AsyncIteratorByteStream(stream: AsyncIterable[bytes])
│   ├── ByteStream(stream: bytes)
│   ├── IteratorByteStream(stream: Iterable[bytes])
│   ├── UnattachedStream(...)
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
│   │       content: RequestContent | None = ...,
│   │       data: RequestData | None = ...,
│   │       files: RequestFiles | None = ...,
│   │       json: Any | None = ...,
│   │       boundary: bytes | None = ...,
│   │   ) -> tuple[dict[str, str], SyncByteStream | AsyncByteStream]
│   ├── encode_response(
│   │       content: ResponseContent | None = ...,
│   │       text: str | None = ...,
│   │       html: str | None = ...,
│   │       json: Any | None = ...,
│   │   ) -> tuple[dict[str, str], SyncByteStream | AsyncByteStream]
│   ├── encode_text(text: str) -> tuple[dict[str, str], ByteStream]
│   └── encode_urlencoded_data(
│           data: RequestData,
│       ) -> tuple[dict[str, str], ByteStream]
├── _decoders  Handlers for Content-Encoding.
│   ├── BrotliDecoder()
│   ├── ByteChunker(chunk_size: int | None = ...)
│   ├── ContentDecoder(...)
│   ├── DeflateDecoder()
│   ├── GZipDecoder()
│   ├── IdentityDecoder(...)
│   ├── LineDecoder()
│   ├── MultiDecoder(children: typing.Sequence[ContentDecoder])
│   ├── TextChunker(chunk_size: int | None = ...)
│   ├── TextDecoder(encoding: str = ...)
│   └── ZStandardDecoder()
├── _exceptions  Our exception hierarchy:
│   ├── CloseError(...)
│   ├── ConnectError(...)
│   ├── ConnectTimeout(...)
│   ├── CookieConflict(message: str)
│   ├── DecodingError(...)
│   ├── HTTPError(message: str)
│   ├── HTTPStatusError(message: str, *, request: Request, response: Response)
│   ├── InvalidURL(message: str)
│   ├── LocalProtocolError(...)
│   ├── NetworkError(...)
│   ├── PoolTimeout(...)
│   ├── ProtocolError(...)
│   ├── ProxyError(...)
│   ├── ReadError(...)
│   ├── ReadTimeout(...)
│   ├── RemoteProtocolError(...)
│   ├── RequestError(message: str, *, request: Request | None = ...)
│   ├── RequestNotRead()
│   ├── ResponseNotRead()
│   ├── StreamClosed()
│   ├── StreamConsumed()
│   ├── StreamError(message: str)
│   ├── TimeoutException(...)
│   ├── TooManyRedirects(...)
│   ├── TransportError(...)
│   ├── UnsupportedProtocol(...)
│   ├── WriteError(...)
│   ├── WriteTimeout(...)
│   └── request_context(request: Request | None = ...) -> typing.Iterator[None]
├── _main
│   ├── download_response(response: Response, download: typing.BinaryIO) -> None
│   ├── format_certificate(cert: _PeerCertRetDictType) -> str
│   ├── format_request_headers(
│   │       request: httpcore.Request,
│   │       http2: bool = ...,
│   │   ) -> str
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
│   ├── main(
│   │       url: str,
│   │       method: str,
│   │       params: list[tuple[str, str]],
│   │       content: str,
│   │       data: list[tuple[str, str]],
│   │       files: list[tuple[str, click.File]],
│   │       json: str,
│   │       headers: list[tuple[str, str]],
│   │       cookies: list[tuple[str, str]],
│   │       auth: tuple[str, str] | None,
│   │       proxy: str,
│   │       timeout: float,
│   │       follow_redirects: bool,
│   │       verify: bool,
│   │       http2: bool,
│   │       download: typing.BinaryIO | None,
│   │       verbose: bool,
│   │   ) -> None
│   ├── print_help() -> None
│   ├── print_request_headers(
│   │       request: httpcore.Request,
│   │       http2: bool = ...,
│   │   ) -> None
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
│   │       verbose: bool = ...,
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
│   ├── Cookies(cookies: CookieTypes | None = ...)
│   ├── Headers(headers: HeaderTypes | None = ..., encoding: str | None = ...)
│   ├── Request(
│   │       method: str,
│   │       url: URL | str,
│   │       *,
│   │       params: QueryParamTypes | None = ...,
│   │       headers: HeaderTypes | None = ...,
│   │       cookies: CookieTypes | None = ...,
│   │       content: RequestContent | None = ...,
│   │       data: RequestData | None = ...,
│   │       files: RequestFiles | None = ...,
│   │       json: typing.Any | None = ...,
│   │       stream: SyncByteStream | AsyncByteStream | None = ...,
│   │       extensions: RequestExtensions | None = ...,
│   │   )
│   └── Response(
│           status_code: int,
│           *,
│           headers: HeaderTypes | None = ...,
│           content: ResponseContent | None = ...,
│           text: str | None = ...,
│           html: str | None = ...,
│           json: typing.Any = ...,
│           stream: SyncByteStream | AsyncByteStream | None = ...,
│           request: Request | None = ...,
│           extensions: ResponseExtensions | None = ...,
│           history: list[Response] | None = ...,
│           default_encoding: str | typing.Callable[[bytes], str] = ...,
│       )
├── _multipart
│   ├── DataField(name: str, value: str | bytes | int | float | None)
│   ├── FileField(name: str, value: FileTypes)
│   ├── MultipartStream(
│   │       data: RequestData,
│   │       files: RequestFiles,
│   │       boundary: bytes | None = ...,
│   │   )
│   └── get_multipart_boundary_from_content_type(
│           content_type: bytes | None,
│       ) -> bytes | None
├── _status_codes
│   └── codes(value: int, phrase: str = ...)
├── _transports
│   ├── asgi
│   │   ├── ASGIResponseStream(body: list[bytes])
│   │   ├── ASGITransport(
│   │   │       app: _ASGIApp,
│   │   │       raise_app_exceptions: bool = ...,
│   │   │       root_path: str = ...,
│   │   │       client: tuple[str, int] = ...,
│   │   │   )
│   │   ├── create_event() -> Event
│   │   └── is_running_trio() -> bool
│   ├── base
│   │   ├── AsyncBaseTransport(...)
│   │   └── BaseTransport(...)
│   ├── default  Custom transports, with nicely configured defaults.
│   │   ├── AsyncHTTPTransport(
│   │   │       verify: ssl.SSLContext | str | bool = ...,
│   │   │       cert: CertTypes | None = ...,
│   │   │       trust_env: bool = ...,
│   │   │       http1: bool = ...,
│   │   │       http2: bool = ...,
│   │   │       limits: Limits = ...,
│   │   │       proxy: ProxyTypes | None = ...,
│   │   │       uds: str | None = ...,
│   │   │       local_address: str | None = ...,
│   │   │       retries: int = ...,
│   │   │       socket_options: typing.Iterable[SOCKET_OPTION] | None = ...,
│   │   │   )
│   │   ├── AsyncResponseStream(httpcore_stream: typing.AsyncIterable[bytes])
│   │   ├── HTTPTransport(
│   │   │       verify: ssl.SSLContext | str | bool = ...,
│   │   │       cert: CertTypes | None = ...,
│   │   │       trust_env: bool = ...,
│   │   │       http1: bool = ...,
│   │   │       http2: bool = ...,
│   │   │       limits: Limits = ...,
│   │   │       proxy: ProxyTypes | None = ...,
│   │   │       uds: str | None = ...,
│   │   │       local_address: str | None = ...,
│   │   │       retries: int = ...,
│   │   │       socket_options: typing.Iterable[SOCKET_OPTION] | None = ...,
│   │   │   )
│   │   ├── ResponseStream(httpcore_stream: typing.Iterable[bytes])
│   │   └── map_httpcore_exceptions() -> typing.Iterator[None]
│   ├── mock
│   │   └── MockTransport(handler: SyncHandler | AsyncHandler)
│   └── wsgi
│       ├── WSGIByteStream(result: typing.Iterable[bytes])
│       └── WSGITransport(
│               app: WSGIApplication,
│               raise_app_exceptions: bool = ...,
│               script_name: str = ...,
│               remote_addr: str = ...,
│               wsgi_errors: typing.TextIO | None = ...,
│           )
├── _types  Type definitions for type checking purposes.
│   ├── AsyncByteStream(...)
│   └── SyncByteStream(...)
├── _urlparse  An implementation of `urlparse` that provides URL validation and
│   normalization
│   ├── PERCENT(string: str) -> str
│   ├── ParseResult(...)
│   ├── encode_host(host: str) -> str
│   ├── normalize_path(path: str) -> str
│   ├── normalize_port(port: str | int | None, scheme: str) -> int | None
│   ├── percent_encoded(string: str, safe: str) -> str
│   ├── quote(string: str, safe: str) -> str
│   ├── urlparse(url: str = ..., **kwargs: str | None) -> ParseResult
│   └── validate_path(path: str, has_scheme: bool, has_authority: bool) -> None
├── _urls
│   ├── QueryParams(*args: QueryParamTypes | None, **kwargs: typing.Any)
│   └── URL(url: URL | str = ..., **kwargs: typing.Any)
└── _utils
    ├── URLPattern(pattern: str)
    ├── get_environment_proxies() -> dict[str, str | None]
    ├── is_ipv4_hostname(hostname: str) -> bool
    ├── is_ipv6_hostname(hostname: str) -> bool
    ├── peek_filelike_length(stream: typing.Any) -> int | None
    ├── primitive_value_to_str(value: PrimitiveData) -> str
    ├── to_bytes(value: str | bytes, encoding: str = ...) -> bytes
    ├── to_bytes_or_str(
    │       value: str,
    │       match_type_of: typing.AnyStr,
    │   ) -> typing.AnyStr
    ├── to_str(value: str | bytes, encoding: str = ...) -> str
    └── unquote(value: str) -> str
```

Python API: `source_trees(root)` and `runtime_trees(root)` accept the CLI's
`scope`, `exclude` (an `Exclusion`), and `show_defaults` options and return a
`Tree` for each inspected package. A `Tree` has `items` (`Signature` objects in
definition order), `children`, `docstring`, and `error`, which explains why a
module could not be fully inspected. `str(signature)` is its one-line form.
These replace `build_tree()`, `get_packages()`, `get_module_items()`, and
`format_signature()` from 0.6.

Development commands live in `justfile`. Run `uv run just` for local checks and
README generation. README examples run with the locked dependencies in `uv.lock`.
