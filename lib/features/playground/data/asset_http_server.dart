import 'dart:async';
import 'dart:io';

import 'package:flutter/services.dart';

/// Serves bundled assets to the in-app WebView over http://127.0.0.1.
///
/// Pyodide needs real URLs (it fetches its wasm and stdlib), correct MIME
/// types and, for interrupting programs, cross-origin isolation headers.
/// Only the Python runner and Pyodide folders are served, read-only.
class AssetHttpServer {
  AssetHttpServer._(this._server, this._bundle);

  /// A fixed port keeps the origin stable between launches, so the WebView
  /// can reuse its cache of compiled WebAssembly. Falls back to any port.
  static const int preferredPort = 38137;

  static const List<String> servedFolders = ['python_runner/', 'pyodide/'];

  static const Map<String, String> _mimeTypes = {
    'html': 'text/html; charset=utf-8',
    'js': 'text/javascript; charset=utf-8',
    'mjs': 'text/javascript; charset=utf-8',
    'wasm': 'application/wasm',
    'json': 'application/json',
    'zip': 'application/zip',
    'whl': 'application/zip',
    'tar': 'application/x-tar',
    'data': 'application/octet-stream',
  };

  final HttpServer _server;
  final AssetBundle _bundle;

  int get port => _server.port;

  Uri get origin => Uri.parse('http://127.0.0.1:$port');

  static Future<AssetHttpServer> start(AssetBundle bundle) async {
    HttpServer server;
    try {
      server = await HttpServer.bind(InternetAddress.loopbackIPv4, preferredPort);
    } on SocketException {
      server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    }
    final instance = AssetHttpServer._(server, bundle);
    server.listen(instance._handle, onError: (_) {});
    return instance;
  }

  Future<void> close() => _server.close(force: true);

  static String? assetPathFor(String requestPath) {
    final relative = Uri.decodeComponent(
      requestPath.startsWith('/') ? requestPath.substring(1) : requestPath,
    );
    if (relative.contains('..') || relative.contains('\\')) return null;
    if (!servedFolders.any(relative.startsWith)) return null;
    return 'assets/$relative';
  }

  static String mimeTypeFor(String path) {
    final dot = path.lastIndexOf('.');
    final extension = dot < 0 ? '' : path.substring(dot + 1).toLowerCase();
    return _mimeTypes[extension] ?? 'application/octet-stream';
  }

  Future<void> _handle(HttpRequest request) async {
    final response = request.response;
    try {
      final asset = assetPathFor(request.uri.path);
      if (request.method != 'GET' || asset == null) {
        response.statusCode = HttpStatus.notFound;
        await response.close();
        return;
      }
      final ByteData data;
      try {
        data = await _bundle.load(asset);
      } catch (_) {
        response.statusCode = HttpStatus.notFound;
        await response.close();
        return;
      }
      response.headers
        ..set(HttpHeaders.contentTypeHeader, mimeTypeFor(asset))
        ..set('Cross-Origin-Opener-Policy', 'same-origin')
        ..set('Cross-Origin-Embedder-Policy', 'require-corp')
        ..set('Cross-Origin-Resource-Policy', 'same-origin')
        ..set(
          HttpHeaders.cacheControlHeader,
          asset.contains('/pyodide/')
              ? 'public, max-age=31536000, immutable'
              : 'no-cache',
        );
      response.contentLength = data.lengthInBytes;
      response.add(
        data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes),
      );
      await response.close();
    } catch (_) {
      try {
        await response.close();
      } catch (_) {}
    }
  }
}
