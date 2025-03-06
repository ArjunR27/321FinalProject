import os

def logout_mac():
    os.system('osascript -e \'tell application "System Events" to sleep\'')


logout_mac()