@echo off
echo Migrating database schema...
.venv\Scripts\python.exe migrate_database.py
echo.

echo Cleaning up false positive charges...
.venv\Scripts\python.exe cleanup_false_positives.py
echo.

echo Classifying documents...
.venv\Scripts\python.exe classify_documents.py
echo.

echo Resetting processing status...
.venv\Scripts\python.exe reset_status.py
echo.

echo Reprocessing documents with improved charge extraction...
.venv\Scripts\python.exe process_documents.py
echo.

echo Done!
pause
