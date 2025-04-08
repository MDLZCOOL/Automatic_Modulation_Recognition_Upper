import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtCharts 2.15
import QtQuick.Dialogs
import io.qt.textproperties 1.0

ApplicationWindow {
    id: mainWindow
    width: 1200
    height: 800
    visible: true
    title: qsTr("信号波形显示")

    property string modelPath: ""
    property string deviceAddress: ""
    property double accuracy: 0.1
    property int sampleRate: 1000

    DataSource {
        id: dataSource
        onDataUpdate: data => {
            for (let i = 0; i < data[0].length; ++i) {
                chartView.addPoint(data[0][i], data[1][i]);
            }
        }
        onPredictionUpdate: data => {
            predictionLabel.text = qsTr("预测结果: %1").arg(data);
        }
    }

    FileDialog {
        id: fileDialog
        title: qsTr("选择文件")
        nameFilters: ["*.onnx"]
        onAccepted: {
            modelPath = fileDialog.fileUrl;
            console.log("选择的文件: " + modelPath);
            // TODO: load your model here
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ——— Top toolbar ———
        ToolBar {
            Layout.fillWidth: true
            RowLayout {
                anchors.fill: parent
                spacing: 10
                Layout.alignment: Qt.AlignHCenter

                ToolButton {
                    text: qsTr("开始")
                    onClicked: {
                        axisX.min = 0;
                        axisX.max = 256;
                        realSeries.clear();
                        imaginarySeries.clear();
                        dataSource.start_recording();
                    }
                }
                ToolButton {
                    text: qsTr("停止")
                    onClicked: dataSource.stop_recording()
                }
                ToolButton {
                    text: qsTr("选择文件")
                    onClicked: fileDialog.open()
                }
                Label {
                    text: qsTr("设备地址:")
                }
            }
        }

        // ——— Tabs ———
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            TabButton {
                text: qsTr("信号波形")
            }
            TabButton {
                text: qsTr("设置")
            }
        }

        // ——— Tab content ———
        StackLayout {
            id: tabContent
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex

            // —— Page 0: Signal waveform ——
            Item {
                anchors.fill: parent
                ChartView {
                    id: chartView
                    anchors.fill: parent
                    theme: ChartView.ChartThemeBlueNcs
                    antialiasing: true
                    animationOptions: ChartView.SeriesAnimations
                    animationDuration: 500

                    ValueAxis {
                        id: axisX
                        min: 0
                        max: 256
                        titleText: qsTr("时间")
                    }
                    ValueAxis {
                        id: axisY
                        titleText: qsTr("幅值")
                    }

                    LineSeries {
                        id: realSeries
                        name: qsTr("实部")
                        axisX: axisX
                        axisY: axisY
                    }
                    LineSeries {
                        id: imaginarySeries
                        name: qsTr("虚部")
                        axisX: axisX
                        axisY: axisY
                    }

                    Text {
                        id: predictionLabel
                        anchors.left: parent.left
                        anchors.top: predictionLabel.top
                        text: qsTr("预测结果: %1").arg("AM")
                        font.pixelSize: 50
                        font.bold: true
                        color: "Red"
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
            }

            // —— Page 1: Settings ——
            ScrollView {
                anchors.fill: parent
                contentWidth: parent.width
                contentHeight: settingsGrid.implicitHeight
                
                RowLayout {
                    
                    GridLayout {
                        id: settingsGrid
                        columns: 2
                        rowSpacing: 10
                        columnSpacing: 20
                        anchors.margins: 20
                        Layout.alignment: Qt.AlignTop | Qt.AlignVCenter
                        Label {
                            text: qsTr("TX 频率")
                            horizontalAlignment: Text.AlignRight
                        }
                        TextField {
                            id: txFreqField
                            text: "935.6M"
                            placeholderText: qsTr("请输入 TX 频率")
                        }

                        Label {
                            text: qsTr("RX 频率")
                            horizontalAlignment: Text.AlignRight
                        }
                        TextField {
                            id: rxFreqField
                            text: "935.6M"
                            placeholderText: qsTr("请输入 RX 频率")
                        }

                        Label {
                            text: qsTr("TX 增益")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: txGainCombo
                            model: ["0 dB", "10 dB", "20 dB", "30 dB", "40 dB"]
                            currentIndex: 2
                        }

                        Label {
                            text: qsTr("RX 增益")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: rxGainCombo
                            model: ["0 dB", "10 dB", "20 dB", "30 dB", "40 dB"]
                            currentIndex: 2
                        }

                        Label {
                            text: qsTr("工作模式")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: workModeCombo
                            model: [qsTr("正常模式"), qsTr("测试模式")]
                            currentIndex: 0
                            onCurrentTextChanged: {
                                console.log("工作模式改变为: " + workModeCombo.currentText);
                            }
                        }

                        // … add more settings rows here …

                        Button {
                            text: qsTr("写入全部")
                            Layout.columnSpan: 2
                            onClicked: {
                                console.log("TX 频率 =", txFreqField.text);
                                console.log("RX 频率 =", rxFreqField.text);
                                console.log("TX 增益 =", txGainCombo.currentText);
                                console.log("RX 增益 =", rxGainCombo.currentText);
                                console.log("工作模式 =", workModeCombo.currentText);
                                // TODO: call your backend interface here
                            }
                        }
                    }
                
                    GridLayout {
                        id: dgsettingsGrid
                        columns: 2
                        rowSpacing: 10
                        columnSpacing: 20
                        anchors.margins: 20
                        

                        // 码元类型
                        Label {
                            text: qsTr("码元类型")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: symbolTypeCombo
                            model: [qsTr("全1"), qsTr("全0"), qsTr("PRBS")]
                            currentIndex: 0
                            onCurrentTextChanged: prbsTypeLabel.visible = prbsTypeCombo.visible = (currentText === qsTr("PRBS"))
                        }
                        Label {
                            id: prbsTypeLabel
                            text: qsTr("PRBS 类型")
                            horizontalAlignment: Text.AlignRight
                            visible: false
                        }
                        ComboBox {
                            id: prbsTypeCombo
                            model: ["PRBS9", "PRBS11", "PRBS15", "PRBS16", "PRBS20", "PRBS21", "PRBS23"]
                            visible: false
                        }

                        // 长度
                        Label {
                            text: qsTr("长度")
                            horizontalAlignment: Text.AlignRight
                        }
                        TextField {
                            id: lengthField
                            placeholderText: qsTr("10.00M")
                        }

                        // 码元速率
                        Label {
                            text: qsTr("码元速率")
                            horizontalAlignment: Text.AlignRight
                        }
                        TextField {
                            id: symbolRateField
                            placeholderText: qsTr("1.0000MSa/s")
                        }

                        // 调制类型
                        Label {
                            text: qsTr("调制类型")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: modulationCombo
                            model: [qsTr("AM"), qsTr("FM"), qsTr("BPSK"), qsTr("QPSK"), qsTr("8PSK"), qsTr("16QAM"), qsTr("32QAM"), qsTr("64QAM"), qsTr("128QAM"), qsTr("256QAM")]
                        }

                        // 编码类型
                        Label {
                            text: qsTr("编码类型")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: codingCombo
                            model: [qsTr("无编码"), qsTr("差分编码"), qsTr("差分+格雷编码"), qsTr("格雷码")]
                        }

                        // 过采样率
                        Label {
                            text: qsTr("过采样率")
                            horizontalAlignment: Text.AlignRight
                        }
                        TextField {
                            id: oversamplingField
                            placeholderText: qsTr("1")
                        }

                        // 滤波器
                        Label {
                            text: qsTr("滤波器")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: filterCombo
                            model: [qsTr("窗口滤波器"), qsTr("余弦滤波器"), qsTr("根生余弦滤波器")]
                            onCurrentTextChanged: {
                                filterAlphaLabel.visible = filterAlphaField.visible = (currentText === qsTr("余弦滤波器") || currentText === qsTr("根生余弦滤波器"));
                            }
                        }
                        Label {
                            id: filterAlphaLabel
                            text: qsTr("Alpha/BT")
                            horizontalAlignment: Text.AlignRight
                            visible: false
                        }
                        TextField {
                            id: filterAlphaField
                            placeholderText: qsTr("0.25")
                            visible: false
                        }

                        // 输出通道
                        Label {
                            text: qsTr("输出通道")
                            horizontalAlignment: Text.AlignRight
                        }
                        RowLayout {
                            CheckBox {
                                text: "CH1"
                            }
                            CheckBox {
                                text: "CH2"
                            }
                            CheckBox {
                                text: "CH3"
                            }
                            CheckBox {
                                text: "CH4"
                            }
                        }

                        // 中心频率
                        Label {
                            text: qsTr("中心频率")
                            horizontalAlignment: Text.AlignRight
                        }
                        TextField {
                            id: centerFreqField
                            placeholderText: qsTr("1.00 GHz")
                        }

                        // 输出模式
                        Label {
                            text: qsTr("输出模式")
                            horizontalAlignment: Text.AlignRight
                        }
                        ComboBox {
                            id: outputModeCombo
                            model: [qsTr("AC"), qsTr("DC HBW"), qsTr("DC AMP")]
                            currentIndex: 2
                        }

                        // 输出幅度
                        Label {
                            text: qsTr("输出幅度")
                            horizontalAlignment: Text.AlignRight
                        }
                        TextField {
                            id: outputAmpField
                            placeholderText: qsTr("100mV")
                        }

                        // 编译并下发
                        Button {
                            text: qsTr("编译并下发")
                            Layout.columnSpan: 2
                            onClicked: {
                                console.log("SymbolType=", symbolTypeCombo.currentText, "PRBS=", prbsTypeCombo.currentText, "Length=", lengthField.text, "Rate=", symbolRateField.text, "Modulation=", modulationCombo.currentText, "Coding=", codingCombo.currentText, "Oversample=", oversamplingField.text, "Filter=", filterCombo.currentText, "Alpha=", filterAlphaField.text, "Channels=CH1:" + ch1.checked + " CH2:" + ch2.checked + " CH3:" + ch3.checked + " CH4:" + ch4.checked, "CenterFreq=", centerFreqField.text, "OutMode=", outputModeCombo.currentText, "OutAmp=", outputAmpField.text);
                            }
                        }
                    }
                }
            }
        }

        // ——— Bottom status bar ———
        ToolBar {
            Layout.fillWidth: true
            RowLayout {
                anchors.fill: parent
                spacing: 20
                Layout.alignment: Qt.AlignHCenter

                Label {
                    text: qsTr("设备状态: XSRP %1 DG70004 %2 DS81304 %3").arg("🟢️").arg("🟢️").arg("🟢️")
                }
                Label {
                    text: qsTr("模型路径: %1").arg(modelPath)
                }
            }
        }
    }
}
