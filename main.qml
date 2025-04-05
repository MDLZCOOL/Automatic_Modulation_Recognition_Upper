import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtCharts 2.15
// import QtQuick.Controls.Material 2.15
import QtQuick.Dialogs

import io.qt.textproperties 1.0

ApplicationWindow {

    id: mainWindow  

    property string modelPath: ""
    property string deviceAddress: ""
    property double accuracy: 0.1
    property int sampleRate: 1000
    // property string name: value

    visible: true
    width: 600
    height: 400
    title: "信号波形显示"
    DataSource {
        id: dataSource
        onDataUpdate: data => {
            
            for (let point in data[0]) {
                // console.log("接收到数据: " + point);
                chartView.addPoint(data[0][point], data[1][point]);
                // axisY.applyNiceNumbers();
            }
        }
        onPredictionUpdate: data => {
            predictionLabel.text = "预测结果: " + data;
        }
    }
    FileDialog {
        id: fileDialog
        visible: false
        title: "选择文件"
        nameFilters: ["*.onnx"]
        onAccepted: {
            modelPath = fileDialog.currentFile;
            console.log("选择的文件: " + modelPath);
            // 这里可以添加加载模型的代码
        }
    }

    Timer {
        id: timer
        interval: 1
        repeat: true
        running: true
        onTriggered: {
            dataSource.update_data();
        }
    }



    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        ToolBar {
            Layout.fillWidth: true
            RowLayout {
                spacing: 10
                Layout.alignment: Qt.AlignHCenter
                anchors.fill: parent
                ToolButton {
                    text: "开始"
                    onClicked: {
                        // timer.running = true;
                        axisX.min = 0;
                        axisX.max = 1024;

                        realSeries.clear();
                        imaginarySeries.clear();
                    }
                }
                ToolButton {
                    text: "停止"
                    onClicked: timer.running = false
                }
                ToolButton {
                    text: "选择文件"
                    onClicked: {
                        fileDialog.open();
                    }
                }

                Label {
                    text: "设备地址:"
                }
                TextArea {
                    id: inputField
                    font.pixelSize: 15
                    Layout.fillWidth: true
                }
                ToolButton {
                    text: "连接"
                    
                }
            }
        }

        ChartView {
            id: chartView
            theme: ChartView.ChartThemeBlueNcs
            antialiasing: true
            animationOptions: ChartView.SeriesAnimations
            animationDuration: 500
            Layout.fillWidth: true
            Layout.fillHeight: true

            ValueAxis {
                id: axisX
                min: 0
                max: 256
                titleText: "时间"
            }
            ValueAxis {
                id: axisY
                
                titleText: "幅值"

                
            }

            LineSeries {
                id: realSeries
                name: "实部"
                axisX: axisX
                axisY: axisY
            }

            LineSeries {
                id: imaginarySeries
                name: "虚部"
                axisX: axisX
                axisY: axisY
            }

            function addPoint(realValue, imaginaryValue) {
                var x = realSeries.count;
                realSeries.append(x, realValue);
                imaginarySeries.append(x, imaginaryValue);
                if (realSeries.count > 256) {
                    axisX.min += 1;
                    axisX.max += 1;
                }

            }
        }
        ToolBar {
            Layout.fillWidth: true
            Row {
                spacing: 10
                Layout.alignment: Qt.AlignHCenter
                anchors.fill: parent
                Label {
                    text: "设备状态： %1".arg("正常")
                }
                Label {
                    id: predictionLabel
                    text: "预测值: %1".arg("AM")
                }
                Label {
                    text: "置信度: %1".arg("0.99")
                }
                Label {
                    text: "模型路径: %1".arg(modelPath)
                }
            }
        }
    }
}
