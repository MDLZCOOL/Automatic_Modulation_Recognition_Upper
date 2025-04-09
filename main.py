import sys
import asyncio
import PySide6.QtAsyncio as QtAsyncio
import data_source

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from time import strftime, localtime
from PySide6.QtCore import QTimer, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication


async def sleep(seconds: int):
	"""Asynchronous sleep function"""
	await asyncio.sleep(seconds)


app = QApplication(sys.argv)

engine = QQmlApplicationEngine()
engine.load('main.qml')


curr_time = strftime("%H:%M:%S", localtime())


QtAsyncio.run()

