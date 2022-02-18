# PYNJECT STANDARD PAYLOAD COLLECTION - https://github.com/am-nobody/pynject/payloads
#
# Title: Status Check v1.0
# Author: am-nobody

import ctypes

# Retrieve the MessageBoxA function from the Windows API's User32 library.
MessageBoxA = ctypes.windll.user32.MessageBoxA

# Our window handle is NULL.
# Python uses UTF-8 encoding, our character pointer type is c_char_p. Value should be bytes.
# Our message box type is the 'MB_OK' constant.
hWnd = None
lpText = ctypes.c_char_p(b"Execution was successful.")
lpCaption = ctypes.c_char_p(b"Success")
uType = 0x00000000

# Call the function with our arguments.
MessageBoxA(hWnd, lpText, lpCaption, uType)