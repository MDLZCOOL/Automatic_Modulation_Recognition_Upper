import sys
import asyncio
import PySide6.QtAsyncio as QtAsyncio

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from time import strftime, localtime


async def sleep(seconds: int):
	"""Asynchronous sleep function"""
	await asyncio.sleep(seconds)


app = QApplication(sys.argv)

engine = QQmlApplicationEngine()
engine.load('main.qml')


curr_time = strftime("%H:%M:%S", localtime())


QtAsyncio.run()

