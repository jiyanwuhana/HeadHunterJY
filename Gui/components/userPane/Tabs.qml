import QtQuick 2.6

Rectangle {
    id: tab
    width: parent.width
    border.color: "black"
    
    property alias tabVal: tabName.text

    Text {
        id: tabName
        anchors.centerIn: parent
        rotation: 90
    }
}