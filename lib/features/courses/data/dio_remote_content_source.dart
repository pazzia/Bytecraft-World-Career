import 'dart:developer' as developer;

import 'package:dio/dio.dart';

import 'content_sources.dart';

/// Fetches assembled course documents from `GET {baseUrl}/courses/{id}`.
///
/// Network failures return null: remote content is an optimisation,
/// bundled content is the source of truth when offline.
class DioRemoteContentSource implements RemoteContentSource {
  DioRemoteContentSource(this._dio);

  final Dio _dio;

  @override
  Future<Map<String, dynamic>?> fetchCourse(String courseId) async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>('/courses/$courseId');
      return response.data;
    } on DioException catch (error) {
      developer.log('Remote content unavailable: $error', name: 'content');
      return null;
    }
  }
}
