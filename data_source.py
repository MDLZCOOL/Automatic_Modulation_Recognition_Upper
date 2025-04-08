import asyncio

from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtCore import QTimer, QObject, Signal, Slot
import PySide6.QtAsyncio as QtAsyncio
from time import strftime, localtime

import model_interface
import numpy as np

import xsrp_interface

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class DataSource(QObject):
    dataUpdate = Signal(list)
    predictionUpdate = Signal(str)

    @Slot()
    def update_data(self) -> None:
        """Update data and emit signal"""
        asyncio.ensure_future(self.async_update_data())

    def total_predict(self, data):
        predictionA = self.classifierA.predict(data)
        predictionB = self.classifierB.predict(data)
        prediction = predictionA
        if prediction not in ['am', 'fm']:
            prediction = predictionB
        return prediction

    async def async_update_data(self) -> None:
        """Update data and emit signal"""
        # Simulate data generation
        data = await asyncio.to_thread(xsrp_interface.XSRPDeviceGetData, self.window_length)
        self.dataUpdate.emit([data[:1024], data[1024:]])
        await asyncio.sleep(3)
        prediction = await asyncio.to_thread(lambda: self.total_predict(data))
        self.predictionUpdate.emit(prediction)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("DataSource initialized")
        self.window_length = 8
        self.classifierA = model_interface.ModulationClassifierA("model_3.pth")
        self.classifierB = model_interface.ModulationClassifierB("model_2.pth")
