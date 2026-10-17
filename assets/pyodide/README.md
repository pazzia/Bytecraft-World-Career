Pyodide (CPython compiled to WebAssembly) is downloaded here by CI before
the build (see .github/workflows/android.yml) and is not stored in git.
Without it the app works, only the Python sandbox reports that the
interpreter is unavailable.
