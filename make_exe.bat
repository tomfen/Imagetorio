rmdir /S dist
pyinstaller -F make_belt.py
copy items.txt dist\items.txt
rmdir /S build