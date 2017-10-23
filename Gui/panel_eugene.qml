import QtQuick 2.6
import QtQuick.Controls 2.2

import "./components"
import "./components/userPane"

Rectangle {
    id: root
    
    width: 300
    height: parent.height

    Rectangle {
        anchors.fill: parent
        anchors.margins: 5

        // display window
        Rectangle {
            id: display
            width: 265
            height: parent.height
            // anchors.left: vtk.right
            border.color: "black"

            // results
            Rectangle {
                id: results
                anchors.fill: parent
                anchors.margins: 5
                visible: true

                Column {
                    Text {
                        text: "Results (结果):"
                    }

                    Text {
                        text: MainWindow.classification
                    }
                }

                // ListView {
                //     id: resultsListView
                //     width: parent.width
                //     height: 200
                //     anchors.top: parent.top
                //     anchors.topMargin: 25
                //     clip: true
                //     model: testModel
                //     // model: MainWindow.predictionsList
                //     delegate: resultsDelegate
                // }

                ListModel {
                    id: testModel
                    ListElement { disease: "tsjl"; result: "99%" }
                    ListElement { disease: "nml"; result: "99%" }
                    ListElement { disease: "bpynz"; result: "99%" }
                    ListElement { disease: "xxg"; result: "99%" }
                }

                Component {
                    id: resultsDelegate
                    Item {
                        width: resultsListView.width
                        height: 25

                        Rectangle {
                            width: parent.width
                            height: parent.height
                            color: index % 2 == 0 ? "lightgrey": "white" 
                            Text {
                                text: disease
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.left: parent.left
                                anchors.leftMargin: 5
                            }
                            Text {
                                text: result
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.right: parent.right
                                anchors.rightMargin: 5
                            }
                        }
                    }
                }
            }

            // modes
            Rectangle {
                id: modes
                anchors.fill: parent
                anchors.margins: 5
                color: "blue"
                visible: false
            }
        }

        // tabs window
        Rectangle {
            width: 25
            height: parent.height
            anchors.left: display.right
            border.color: "black"

            // pathology tab
            Tabs {
                id: pathologyTab
                height: 125
                tabVal: "Pathology (病理)"
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        results.visible = true
                        modes.visible = false
                    }
                }
            }

            // modes tab
            Tabs {
                id: modesTab
                y: pathologyTab.height - 1
                height: 75
                tabVal: "Modes"
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        results.visible = false
                        modes.visible = true
                    }
                }
            }
        } 
    }
}