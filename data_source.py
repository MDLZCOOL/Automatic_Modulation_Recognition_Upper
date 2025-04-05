import asyncio

from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtCore import QTimer, QObject, Signal, Slot
import PySide6.QtAsyncio as QtAsyncio
from time import strftime, localtime


model_interface = __import__("Automatic-Modulation-Recognition-Model").model_interface
import numpy as np

import xsrp_interface

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

@QmlElement
class DataSource(QObject):
    dataUpdate = Signal(list[list])
    predictionUpdate = Signal(str)

    @Slot()
    async def update_data(self) -> None:
        """Update data and emit signal"""
        # Simulate data generation
        data = await asyncio.to_thread(lambda :xsrp_interface.XSRPDeviceGetData(self.window_length))
        self.dataUpdate.emit([data.result_i, data.result_q])
        prediction = await asyncio.to_thread(lambda: self.classifier.predict(data.result))
        self.predictionUpdate.emit(prediction)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("DataSource initialized")
        self.window_length = 1024
        self.classifier = model_interface.ModulationClassifier("Automatic-Modulation-Recognition-Model/model.pth")
        