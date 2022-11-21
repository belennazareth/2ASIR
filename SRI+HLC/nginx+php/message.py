# Explosión masiva de mensajitos por whatsapp web :)

import pyautogui as pt
import time

limit = input ("·.* Cantidad de mensajitos: ")
message = input ("·.* Mensajito: ")
i = 0

while i < int(limit):
	pt.typewrite(message)
	pt.press("enter")
	i += 1
