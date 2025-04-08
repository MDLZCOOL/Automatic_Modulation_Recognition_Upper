import asyncio

from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtCore import QTimer, QObject, Signal, Slot
import PySide6.QtAsyncio as QtAsyncio
from time import strftime, localtime

import Automatic_Modulation_Recognition_Model.model_interface as model_interface
import numpy as np

import xsrp_interface

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class DataSource(QObject):
    dataUpdate = Signal(list)
    predictionUpdate = Signal(str)

    def total_predict(self, data):
        prediction = self.classifier.predict(data)
        return prediction

    async def async_update_data(self) -> None:
        """Update data and emit signal"""
        # Simulate data generation
        while True:
            try:
                data = await asyncio.to_thread(xsrp_interface.XSRPDeviceGetData, self.window_length)
                self.dataUpdate.emit([data[:1024], data[1024:]])
                prediction = await asyncio.to_thread(lambda: self.total_predict(data))
                self.predictionUpdate.emit(prediction)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error in async_update_data: {e}")

    @Slot()
    def start_recording(self):
        """Start the data generation"""
        loop = asyncio.get_event_loop()
        loop.create_task(self.async_update_data())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("DataSource initialized")
        self.window_length = 8
        self.classifier = model_interface.ModulationClassifier("Automatic_Modulation_Recognition_Model/model.pth")
