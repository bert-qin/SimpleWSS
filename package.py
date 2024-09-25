import os

# build exe
print('Begin to build exe...')
os.system('pyinstaller -w -i myico\icon.png -F main.py -n "simplewss"')
os.system('explorer dist')
