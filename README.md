# AutoWK

AutoWK is a Windows-only Python automation wrapper for a bundled WebKit-based
browser runtime. It exposes a small WebDriver-style Python API and ships the
required `MiniBrowser.exe` and `WebDriver.exe` binaries inside the package.

## Install

```bash
pip install autowk==0.4.3
```

AutoWK currently targets 64-bit Windows. The wheel includes native Windows
executables and DLLs, so it is not intended for Linux or macOS.

## Quick Start

```python
from autowk import AutoWK

client = AutoWK(lang="en-US", timezone="America/Chicago")
try:
    client.create_session()
    client.navigate("https://example.com/")
    print(client.get_title())
finally:
    try:
        client.delete_session()
    finally:
        client.close()
```

The legacy import paths remain supported:

```python
from autowk.AutoWkDriverClient import AutoWK
from autowk.AutoWKOptions import Options
```

## Diagnostics

AutoWK 0.4.3 adds a lightweight command line interface:

```bash
python -m autowk
autowk --version
autowk doctor
autowk paths
```

`autowk doctor` checks that the bundled browser binaries exist and that the
default local ports are available. It does not launch the browser.

## Safety Notes

- `close()` only terminates processes started by the current `AutoWK` instance.
- Network listener output is redacted by default to avoid printing credentials.
- Proxy credentials are still passed to the bundled browser as startup
  arguments because that is the current MiniBrowser interface. Avoid using
  shared machines or process-list logging when passing proxy passwords.

## License

AutoWK's Python code is distributed under the BSD 2-Clause License. The package
also bundles WebKit runtime files, supporting DLLs, and WebInspector
third-party resources under their respective upstream licenses. See `NOTICE`,
`THIRD_PARTY_NOTICES.md`, and the bundled license files for details before
redistributing the wheel.
