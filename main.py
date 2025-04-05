import sys
import asyncio

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtCore import QTimer, QObject, Signal, Slot
import PySide6.QtAsyncio as QtAsyncio
from time import strftime, localtime

import data_source

async def sleep(seconds: int):
	"""Asynchronous sleep function"""
	await asyncio.sleep(seconds)


app = QApplication(sys.argv)

engine = QQmlApplicationEngine()
engine.load('main.qml')


curr_time = strftime("%H:%M:%S", localtime())


QtAsyncio.run()

