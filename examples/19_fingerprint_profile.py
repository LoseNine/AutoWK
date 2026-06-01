"""Verify a MiniBrowser fpfile against a local fingerprint test page."""

import argparse
import json
import math
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from _common import add_keep_open_arg, create_options_client, parse_with, safe_delete_and_close, wait_if_requested


DEFAULT_FPFILE = Path("C:/safari/fp.txt")
FINGERPRINT_HTML_PATH = Path(__file__).resolve().parent / "fixtures" / "fingerprint_profile.html"


FINGERPRINT_HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>AutoWK fingerprint check</title>
  <style>
    body { font: 14px/1.45 system-ui, sans-serif; margin: 24px; color: #202124; }
    code { background: #f1f3f4; padding: 2px 4px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>AutoWK fingerprint check</h1>
  <p>This local page exposes browser fingerprint values for the Python example.</p>
  <script>
    (function () {
      const values = {};
      const errors = [];

      function normalize(value) {
        if (value === undefined)
          return "undefined";
        if (value === null)
          return null;
        if (ArrayBuffer.isView(value))
          return Array.from(value);
        if (Array.isArray(value))
          return value.map(normalize);
        return value;
      }

      function hashBytes(bytes) {
        let hash = 2166136261 >>> 0;
        for (let i = 0; i < bytes.length; ++i) {
          hash ^= bytes[i] & 255;
          hash = Math.imul(hash, 16777619) >>> 0;
        }
        return ("00000000" + hash.toString(16)).slice(-8);
      }

      function sumAbsFinite(values) {
        let sum = 0;
        for (let i = 0; i < values.length; ++i) {
          const value = values[i];
          if (Number.isFinite(value))
            sum += Math.abs(value);
        }
        return sum;
      }

      function setIfDefined(key, value) {
        if (value !== undefined)
          values[key] = normalize(value);
      }

      function collectNavigator() {
        values.useragent = navigator.userAgent;
        values.language = navigator.language;
        values.languages = Array.from(navigator.languages || []);
        values.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
        values.hardware_concurrency = navigator.hardwareConcurrency;
        setIfDefined("device_memory", navigator.deviceMemory);
        values.dnt = navigator.doNotTrack === undefined ? "undefined" : navigator.doNotTrack;
        values.webdriver = navigator.webdriver === undefined ? "undefined" : navigator.webdriver;
      }

      function collectCanvas() {
        const canvas = document.createElement("canvas");
        canvas.width = 96;
        canvas.height = 48;
        const context = canvas.getContext("2d");
        if (!context) {
          values.canvas_supported = false;
          return;
        }
        values.canvas_supported = true;
        const gradient = context.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, "#1357c8");
        gradient.addColorStop(0.5, "#e5d45a");
        gradient.addColorStop(1, "#c6353d");
        context.fillStyle = gradient;
        context.fillRect(0, 0, canvas.width, canvas.height);
        context.fillStyle = "rgba(21, 57, 201, 0.82)";
        context.font = "18px serif";
        context.fillText("AutoWK fp", 8, 30);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height).data;
        values.canvas_image_hash = hashBytes(imageData);
        const url = canvas.toDataURL("image/png");
        values.canvas_data_url_length = url.length;
        values.canvas_data_url_hash = hashBytes(new TextEncoder().encode(url));
      }

      function collectWebGL() {
        const canvas = document.createElement("canvas");
        const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
        if (!gl) {
          values.webgl_supported = false;
          return;
        }
        values.webgl_supported = true;

        const extensionList = gl.getSupportedExtensions() || [];
        values.extensions = extensionList.slice();
        gl.getExtension("WEBGL_debug_renderer_info");
        gl.getExtension("EXT_texture_filter_anisotropic")
          || gl.getExtension("WEBKIT_EXT_texture_filter_anisotropic")
          || gl.getExtension("MOZ_EXT_texture_filter_anisotropic");
        gl.getExtension("WEBGL_draw_buffers");

        const parameters = {
          aliased_line_width_range: "ALIASED_LINE_WIDTH_RANGE",
          aliased_point_size_range: "ALIASED_POINT_SIZE_RANGE",
          alpha_bits: "ALPHA_BITS",
          blue_bits: "BLUE_BITS",
          depth_bits: "DEPTH_BITS",
          green_bits: "GREEN_BITS",
          max_combined_texture_image_units: "MAX_COMBINED_TEXTURE_IMAGE_UNITS",
          max_cube_map_texture_size: "MAX_CUBE_MAP_TEXTURE_SIZE",
          max_fragment_uniform_vectors: "MAX_FRAGMENT_UNIFORM_VECTORS",
          max_renderbuffer_size: "MAX_RENDERBUFFER_SIZE",
          max_texture_image_units: "MAX_TEXTURE_IMAGE_UNITS",
          max_texture_size: "MAX_TEXTURE_SIZE",
          max_varying_vectors: "MAX_VARYING_VECTORS",
          max_vertex_attribs: "MAX_VERTEX_ATTRIBS",
          max_vertex_texture_image_units: "MAX_VERTEX_TEXTURE_IMAGE_UNITS",
          max_vertex_uniform_vectors: "MAX_VERTEX_UNIFORM_VECTORS",
          max_viewport_dims: "MAX_VIEWPORT_DIMS",
          red_bits: "RED_BITS",
          renderer: "RENDERER",
          sample_buffers: "SAMPLE_BUFFERS",
          samples: "SAMPLES",
          shading_language_version: "SHADING_LANGUAGE_VERSION",
          stencil_bits: "STENCIL_BITS",
          subpixel_bits: "SUBPIXEL_BITS",
          vendor: "VENDOR",
          version: "VERSION"
        };
        for (const [key, constant] of Object.entries(parameters)) {
          try {
            values[key] = normalize(gl.getParameter(gl[constant]));
          } catch (error) {
            errors.push(key + ": " + error.message);
          }
        }

        const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
        if (debugInfo) {
          values.unmasked_renderer = normalize(gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL));
          values.unmasked_vendor = normalize(gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL));
        }

        const anisotropy = gl.getExtension("EXT_texture_filter_anisotropic")
          || gl.getExtension("WEBKIT_EXT_texture_filter_anisotropic")
          || gl.getExtension("MOZ_EXT_texture_filter_anisotropic");
        if (anisotropy)
          values.max_texture_max_anisotropy = normalize(gl.getParameter(anisotropy.MAX_TEXTURE_MAX_ANISOTROPY_EXT));

        const drawBuffers = gl.getExtension("WEBGL_draw_buffers");
        if (gl.MAX_COLOR_ATTACHMENTS !== undefined)
          values.max_color_attachments = normalize(gl.getParameter(gl.MAX_COLOR_ATTACHMENTS));
        else if (drawBuffers && drawBuffers.MAX_COLOR_ATTACHMENTS_WEBGL !== undefined)
          values.max_color_attachments = normalize(gl.getParameter(drawBuffers.MAX_COLOR_ATTACHMENTS_WEBGL));
        if (gl.MAX_DRAW_BUFFERS !== undefined)
          values.max_draw_buffers = normalize(gl.getParameter(gl.MAX_DRAW_BUFFERS));
        else if (drawBuffers && drawBuffers.MAX_DRAW_BUFFERS_WEBGL !== undefined)
          values.max_draw_buffers = normalize(gl.getParameter(drawBuffers.MAX_DRAW_BUFFERS_WEBGL));

        const attributes = gl.getContextAttributes() || {};
        values.context_alpha = attributes.alpha;
        values.context_antialias = attributes.antialias;
        values.context_depth = attributes.depth;
        values.context_failIfMajorPerformanceCaveat = attributes.failIfMajorPerformanceCaveat;
        values.context_powerPreference = attributes.powerPreference || "default";
        values.context_premultipliedAlpha = attributes.premultipliedAlpha;
        values.context_preserveDrawingBuffer = attributes.preserveDrawingBuffer;
        values.context_stencil = attributes.stencil;

        const shaders = { vs: gl.VERTEX_SHADER, fs: gl.FRAGMENT_SHADER };
        const precisions = {
          low_float: gl.LOW_FLOAT,
          medium_float: gl.MEDIUM_FLOAT,
          high_float: gl.HIGH_FLOAT,
          low_int: gl.LOW_INT,
          medium_int: gl.MEDIUM_INT,
          high_int: gl.HIGH_INT
        };
        for (const [shaderPrefix, shader] of Object.entries(shaders)) {
          for (const [precisionName, precision] of Object.entries(precisions)) {
            const format = gl.getShaderPrecisionFormat(shader, precision);
            if (format)
              values["shader_precision_" + shaderPrefix + "_" + precisionName] = [format.rangeMin, format.rangeMax, format.precision];
          }
        }
      }

      async function collectWebGPU() {
        values.webgpu_enabled = !!navigator.gpu;
        if (!navigator.gpu)
          return;

        values.webgpu_preferred_canvas_format = navigator.gpu.getPreferredCanvasFormat();
        try {
          values.webgpu_wgsl_language_features = Array.from(navigator.gpu.wgslLanguageFeatures || []).map(String);
        } catch (error) {
          errors.push("webgpu_wgsl_language_features: " + error.message);
        }

        const adapter = await navigator.gpu.requestAdapter();
        if (!adapter) {
          values.webgpu_adapter_available = false;
          return;
        }
        values.webgpu_adapter_available = true;
        setIfDefined("webgpu_adapter_name", adapter.name);
        values.webgpu_features = Array.from(adapter.features || []).map(String);
        values.webgpu_is_fallback_adapter = adapter.isFallbackAdapter;
        if (adapter.info) {
          values.webgpu_vendor = adapter.info.vendor;
          values.webgpu_architecture = adapter.info.architecture;
          values.webgpu_device = adapter.info.device;
          values.webgpu_description = adapter.info.description;
        }

        const limitMap = {
          webgpu_max_texture_dimension_1d: "maxTextureDimension1D",
          webgpu_max_texture_dimension_2d: "maxTextureDimension2D",
          webgpu_max_texture_dimension_3d: "maxTextureDimension3D",
          webgpu_max_texture_array_layers: "maxTextureArrayLayers",
          webgpu_max_bind_groups: "maxBindGroups",
          webgpu_max_bind_groups_plus_vertex_buffers: "maxBindGroupsPlusVertexBuffers",
          webgpu_max_bindings_per_bind_group: "maxBindingsPerBindGroup",
          webgpu_max_dynamic_uniform_buffers_per_pipeline_layout: "maxDynamicUniformBuffersPerPipelineLayout",
          webgpu_max_dynamic_storage_buffers_per_pipeline_layout: "maxDynamicStorageBuffersPerPipelineLayout",
          webgpu_max_sampled_textures_per_shader_stage: "maxSampledTexturesPerShaderStage",
          webgpu_max_samplers_per_shader_stage: "maxSamplersPerShaderStage",
          webgpu_max_storage_buffers_per_shader_stage: "maxStorageBuffersPerShaderStage",
          webgpu_max_storage_textures_per_shader_stage: "maxStorageTexturesPerShaderStage",
          webgpu_max_uniform_buffers_per_shader_stage: "maxUniformBuffersPerShaderStage",
          webgpu_max_uniform_buffer_binding_size: "maxUniformBufferBindingSize",
          webgpu_max_storage_buffer_binding_size: "maxStorageBufferBindingSize",
          webgpu_min_uniform_buffer_offset_alignment: "minUniformBufferOffsetAlignment",
          webgpu_min_storage_buffer_offset_alignment: "minStorageBufferOffsetAlignment",
          webgpu_max_vertex_buffers: "maxVertexBuffers",
          webgpu_max_buffer_size: "maxBufferSize",
          webgpu_max_vertex_attributes: "maxVertexAttributes",
          webgpu_max_vertex_buffer_array_stride: "maxVertexBufferArrayStride",
          webgpu_max_inter_stage_shader_variables: "maxInterStageShaderVariables",
          webgpu_max_inter_stage_shader_components: "maxInterStageShaderComponents",
          webgpu_max_color_attachments: "maxColorAttachments",
          webgpu_max_color_attachment_bytes_per_sample: "maxColorAttachmentBytesPerSample",
          webgpu_max_compute_workgroup_storage_size: "maxComputeWorkgroupStorageSize",
          webgpu_max_compute_invocations_per_workgroup: "maxComputeInvocationsPerWorkgroup",
          webgpu_max_compute_workgroup_size_x: "maxComputeWorkgroupSizeX",
          webgpu_max_compute_workgroup_size_y: "maxComputeWorkgroupSizeY",
          webgpu_max_compute_workgroup_size_z: "maxComputeWorkgroupSizeZ",
          webgpu_max_compute_workgroups_per_dimension: "maxComputeWorkgroupsPerDimension",
          webgpu_max_storage_buffers_in_fragment_stage: "maxStorageBuffersInFragmentStage",
          webgpu_max_storage_textures_in_fragment_stage: "maxStorageTexturesInFragmentStage",
          webgpu_max_storage_buffers_in_vertex_stage: "maxStorageBuffersInVertexStage",
          webgpu_max_storage_textures_in_vertex_stage: "maxStorageTexturesInVertexStage"
        };
        for (const [key, property] of Object.entries(limitMap)) {
          if (adapter.limits && adapter.limits[property] !== undefined)
            values[key] = Number(adapter.limits[property]);
        }
      }

      async function collectWebAudio() {
        const OfflineContext = window.OfflineAudioContext || window.webkitOfflineAudioContext;
        values.webaudio_enabled = !!OfflineContext;
        if (!OfflineContext)
          return;

        const context = new OfflineContext(1, 5000, 44100);
        const oscillator = context.createOscillator();
        const analyser = context.createAnalyser();
        const compressor = context.createDynamicsCompressor ? context.createDynamicsCompressor() : null;
        analyser.fftSize = 2048;
        oscillator.type = "triangle";
        oscillator.frequency.value = 1000;
        oscillator.connect(analyser);
        if (compressor) {
          analyser.connect(compressor);
          compressor.connect(context.destination);
        } else {
          analyser.connect(context.destination);
        }
        oscillator.start(0);
        const buffer = await context.startRendering();
        values.webaudio_target_sample_sum = sumAbsFinite(buffer.getChannelData(0));
        if (compressor)
          values.webaudio_target_reduction = compressor.reduction;
        try {
          const frequencyData = new Float32Array(analyser.frequencyBinCount);
          analyser.getFloatFrequencyData(frequencyData);
          values.webaudio_target_frequency_sum = sumAbsFinite(frequencyData);
        } catch (error) {
          errors.push("webaudio_target_frequency_sum: " + error.message);
        }
        try {
          const timeData = new Float32Array(analyser.fftSize);
          analyser.getFloatTimeDomainData(timeData);
          values.webaudio_target_time_sum = sumAbsFinite(timeData);
        } catch (error) {
          errors.push("webaudio_target_time_sum: " + error.message);
        }
      }

      window.__autowkFingerprintResult = { done: false, values, errors };
      (async function () {
        try {
          collectNavigator();
          collectCanvas();
          collectWebGL();
          await collectWebGPU();
          await collectWebAudio();
        } catch (error) {
          errors.push("collector: " + error.message);
        } finally {
          window.__autowkFingerprintResult.done = true;
        }
      })();
    })();
  </script>
</body>
</html>
"""


SENSITIVE_KEY_PARTS = ("proxy", "password", "username", "credential", "secret", "token")
STARTUP_ONLY_KEYS = {
    "auto_accept_server_trust",
    "accept_server_trust",
    "ignore_certificate_errors",
    "ignore_tls_errors",
    "suppress_http_error_dialogs",
    "suppress_http_errors",
    "ignore_http_error_dialogs",
    "no_http_error_dialogs",
    "suppress_navigation_error_dialogs",
    "suppress_network_error_dialogs",
    "ignore_navigation_error_dialogs",
    "ignore_network_error_dialogs",
    "http_proxy",
    "https_proxy",
    "proxy",
    "proxy_url",
    "proxy_type",
    "socks5_proxy",
}
CANVAS_OBSERVATION_KEYS = {"canvas_noise"}
INFERRED_OR_NOT_EXPOSED_KEYS = {"webaudio_creepjs_pass", "webgpu_adapter_name", "languages", "extensions"}

LEGACY_ACTUAL_ALIASES = {
    "useragent": ("useragent", "navigator.userAgent"),
    "languages": ("languages", "navigator.languages"),
    "language": ("language", "navigator.language"),
    "timezone": ("timezone", "intl.timeZone"),
    "hardware_concurrency": ("hardware_concurrency", "navigator.hardwareConcurrency"),
    "device_memory": ("device_memory", "navigator.deviceMemory"),
    "dnt": ("dnt", "navigator.doNotTrack"),
    "do_not_track": ("dnt", "navigator.doNotTrack"),
    "webdriver": ("webdriver", "navigator.webdriver"),
}


class FingerprintRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/fingerprint.html"):
            body = FINGERPRINT_HTML_PATH.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/fp-profile.json":
            payload = {"source": str(self.server.fpfile), "profile": self.server.profile}
            body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        self.send_error(404)

    def log_message(self, format, *args):
        return


class LocalFingerprintServer:
    def __init__(self, profile, fpfile):
        self.profile = profile
        self.fpfile = fpfile

    def __enter__(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FingerprintRequestHandler)
        self.server.profile = self.profile
        self.server.fpfile = self.fpfile
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.url = f"http://{host}:{port}/fingerprint.html"
        return self

    def __exit__(self, exc_type, exc, tb):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Check an fpfile against a local fingerprint page.")
    parser.add_argument("--fpfile", type=Path, default=DEFAULT_FPFILE, help="MiniBrowser fpfile path.")
    parser.add_argument("--timeout", type=float, default=25.0, help="Seconds to wait for async page probes.")
    parser.add_argument("--poll-interval", type=float, default=0.25, help="Seconds between result polls.")
    add_keep_open_arg(parser)
    return parse_with(parser, argv)


def load_fp_profile(path):
    profile = {}
    if not path or not Path(path).exists():
        return profile

    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        delimiter_positions = [pos for pos in (line.find("="), line.find(":")) if pos >= 0]
        if not delimiter_positions:
            continue
        delimiter = min(delimiter_positions)
        key = line[:delimiter].strip()
        value = line[delimiter + 1 :].strip()
        if key:
            profile[key] = value
    return profile


def collect_fingerprint_values(client, timeout, poll_interval):
    client.execute_script("return document.readyState;")
    client.execute_script("return 'collector-page-ready';")
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = client.execute_script("return window.__autowkFingerprintResult || null;")
        if isinstance(result, dict) and result.get("done"):
            return result
        if result is not None and not isinstance(result, dict):
            return {"done": True, "values": {}, "errors": ["execute_script did not return a result object"]}
        time.sleep(poll_interval)
    return {"done": False, "values": {}, "errors": ["timed out waiting for fingerprint result"]}


def is_sensitive_key(key):
    lowered = key.lower()
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def get_actual_value(actual_values, key):
    if key in actual_values:
        return actual_values[key]
    for alias in LEGACY_ACTUAL_ALIASES.get(key, ()):
        if alias in actual_values:
            return actual_values[alias]
    return None


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "on"):
        return True
    if text in ("0", "false", "no", "off"):
        return False
    return None


def parse_number(value):
    try:
        if isinstance(value, bool):
            return None
        number = float(str(value).strip())
        if math.isfinite(number):
            return number
    except (TypeError, ValueError):
        return None
    return None


def parse_list(value):
    if isinstance(value, (list, tuple)):
        return list(value)
    return [part.strip() for part in str(value).split(",") if part.strip()]


def values_match(key, expected, actual):
    if key == "webdriver" and str(expected).strip().lower() in ("0", "false", "no", "off"):
        return actual in (False, "false", "0", "undefined", None)

    expected_bool = parse_bool(expected)
    actual_bool = parse_bool(actual)
    if expected_bool is not None and actual_bool is not None:
        return expected_bool == actual_bool

    if isinstance(actual, (list, tuple)) or "," in str(expected):
        expected_list = parse_list(expected)
        actual_list = parse_list(actual)
        if len(expected_list) != len(actual_list):
            return False
        return all(values_match(key, left, right) for left, right in zip(expected_list, actual_list))

    expected_number = parse_number(expected)
    actual_number = parse_number(actual)
    if expected_number is not None and actual_number is not None:
        tolerance = 0.0001 if not key.startswith("webaudio_") else 0.05
        return abs(expected_number - actual_number) <= tolerance

    return str(expected) == str(actual)


def format_value(key, value):
    if is_sensitive_key(key):
        return "<sensitive>"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    if isinstance(value, (list, tuple)):
        return ",".join(format_value(key, item) for item in value)
    if value is None:
        return "<missing>"
    return str(value)


def build_fingerprint_report(profile, collected):
    actual_values = collected.get("values", collected) if isinstance(collected, dict) else {}
    report = []

    for key, expected in profile.items():
        if key in STARTUP_ONLY_KEYS or is_sensitive_key(key):
            report.append(
                {
                    "key": key,
                    "status": "SKIP",
                    "expected": format_value(key, expected),
                    "actual": "<startup-only>",
                    "detail": "not page-readable",
                }
            )
            continue

        if key in CANVAS_OBSERVATION_KEYS:
            canvas_hash = actual_values.get("canvas_image_hash")
            report.append(
                {
                    "key": key,
                    "status": "SKIP",
                    "expected": format_value(key, expected),
                    "actual": f"canvas_image_hash={canvas_hash or '<missing>'}",
                    "detail": "canvas is observed by hash, not a direct setting",
                }
            )
            continue

        if key in INFERRED_OR_NOT_EXPOSED_KEYS:
            actual = get_actual_value(actual_values, key)
            actual_text = format_value(key, actual) if actual is not None else "<not exposed>"
            detail = "covered indirectly or not exposed to JS"
            if key == "languages":
                detail = "current WebKit exposes only navigator.language in navigator.languages"
            elif key == "extensions":
                detail = "WebGL reports the supported intersection of fpfile extensions and platform capabilities"
            report.append(
                {
                    "key": key,
                    "status": "SKIP",
                    "expected": format_value(key, expected),
                    "actual": actual_text,
                    "detail": detail,
                }
            )
            continue

        actual = get_actual_value(actual_values, key)
        if actual is None:
            if key.startswith("webgpu_") and actual_values.get("webgpu_enabled") is False:
                detail = "WebGPU is unavailable"
            elif key.startswith("webaudio_") and actual_values.get("webaudio_enabled") is False:
                detail = "WebAudio is unavailable"
            else:
                detail = "not exposed by this page/API"
            report.append(
                {
                    "key": key,
                    "status": "SKIP",
                    "expected": format_value(key, expected),
                    "actual": "<missing>",
                    "detail": detail,
                }
            )
            continue

        passed = values_match(key, expected, actual)
        report.append(
            {
                "key": key,
                "status": "PASS" if passed else "FAIL",
                "expected": format_value(key, expected),
                "actual": format_value(key, actual),
                "detail": "",
            }
        )

    return report


def print_report(report, collected):
    for item in report:
        suffix = f" ({item['detail']})" if item["detail"] else ""
        print(f"{item['status']:4} {item['key']}: expected={item['expected']} actual={item['actual']}{suffix}")

    errors = collected.get("errors", []) if isinstance(collected, dict) else []
    for error in errors:
        print("INFO collector:", error)

    passed = sum(1 for item in report if item["status"] == "PASS")
    failed = sum(1 for item in report if item["status"] == "FAIL")
    skipped = sum(1 for item in report if item["status"] == "SKIP")
    print(f"Summary: PASS={passed} FAIL={failed} SKIP={skipped}")


def run(client, args):
    profile = load_fp_profile(args.fpfile)

    with LocalFingerprintServer(profile, args.fpfile) as server:
        client.create_session()
        try:
            client.navigate(server.url)
            client.document_onload()
            collected = collect_fingerprint_values(client, args.timeout, args.poll_interval)
            report = build_fingerprint_report(profile, collected)

            print("Local fingerprint page:", server.url)
            print("fpfile:", args.fpfile)
            if not profile:
                print("INFO: fpfile was not found or contained no fingerprint keys.")
            print_report(report, collected)
            wait_if_requested(args.keep_open)
            return sum(1 for item in report if item["status"] == "FAIL")
        finally:
            safe_delete_and_close(client)


def main(argv=None):
    args = parse_args(argv)
    raise SystemExit(run(create_options_client(args), args))


if __name__ == "__main__":
    main()
