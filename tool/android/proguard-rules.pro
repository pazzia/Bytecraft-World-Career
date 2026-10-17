# Release builds are shrunk by R8. Some plugins (shared_preferences since its
# JNI-based Android API) call Java/Kotlin methods from native code by name:
# R8 can't see those calls and removes or renames the methods, and the app
# hangs on the splash screen (NoSuchMethodError in SharedPreferencesApiRegistrar).
# Keep plugin code and the Kotlin types used in their JNI signatures as is.
-keep class io.flutter.plugins.** { *; }
-keep class dev.flutter.** { *; }
-keep class com.github.dart_lang.jni.** { *; }
-keep class kotlin.coroutines.** { *; }
-keep class kotlin.jvm.functions.** { *; }
-keep class kotlinx.coroutines.** { *; }
-dontobfuscate
