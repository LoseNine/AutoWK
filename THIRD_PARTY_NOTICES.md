# Third-Party Notices

AutoWK bundles a Windows WebKit runtime under `autowk/bin` so the package can
run without a separate browser installation.

AutoWK's Python code is licensed under the BSD 2-Clause License in `LICENSE`.
Bundled runtime files remain under their respective upstream licenses. This
file is a notice summary and is not a substitute for the referenced license
texts.

## WebKit Runtime

The bundled runtime includes WebKit components and helper executables such as:

- `JavaScriptCore.dll`
- `WebCore.dll`
- `WebKit2.dll`
- `MiniBrowser.exe`
- `WebDriver.exe`
- `WebKitNetworkProcess.exe`
- `WebKitWebProcess.exe`
- `WebKitGPUProcess.exe`

The WebKit project uses BSD-style and LGPL-family licenses across its source
tree. Copies of the primary WebKit license texts used by the bundled runtime
are included here:

- `licenses/WebKit-LICENSE-APPLE.txt`
- `licenses/WebKit-LGPL-2.1.txt`
- `licenses/JavaScriptCore-COPYING.LIB.txt`

Upstream project information: https://webkit.org/

## WebInspector Resources

The bundled WebInspector resources include third-party assets with their own
license files:

- `autowk/bin/WebKit.resources/WebInspectorUI/External/CodeMirror/LICENSE`
- `autowk/bin/WebKit.resources/WebInspectorUI/External/CSSDocumentation/LICENSE`
- `autowk/bin/WebKit.resources/WebInspectorUI/External/Esprima/LICENSE`
- `autowk/bin/WebKit.resources/WebInspectorUI/External/three.js/LICENSE`

## Runtime DLLs

The runtime directory also contains supporting DLLs such as ICU, OpenSSL,
libcurl, libxml2, libxslt, zlib, Brotli, libpng, libjpeg, WebP, JPEG XL,
HarfBuzz, SQLite, ANGLE/OpenGL ES, nghttp2, nghttp3, ngtcp2, and libpsl.
Their license obligations follow the upstream projects that produced the
bundled binaries. Keep this notice file updated whenever the runtime contents
change.
