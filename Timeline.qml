import QtQuick 2.14
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.1

Item {
    id:timeline

    property int fps: 2
    property int duration: 10 // sec

    property alias implicitWidth: timeline_slider.implicitWidth

    //property var data

    Slider {
        id:timeline_slider
        width:implicitWidth
        x: timeline.x
        snapMode: Slider.SnapAlways
        from:0
        to: timeline.duration
        stepSize: 1/timeline.fps
        background: Item {
            x: parent.leftPadding + 13
            y: parent.topPadding + parent.availableHeight / 2
            width: parent.availableWidth - 26
            Repeater {
                model: timeline.duration + 1
                delegate: Column {
                    x: index * parent.width / timeline.duration - width / 2
                    y: 0
                    spacing: 2
                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: 2
                        height: 4
                        color: (index == 0 || index == timeline.duration) ? "transparent":Material.foreground
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: index + "s"
                        color: Material.foreground
                    }
                }
            }
            Rectangle {
                y: -height / 2
                width: parent.width
                height: 4
                radius: 2
                color: Material.foreground
                Rectangle {
                    width: timeline.visualPosition * parent.width
                    height: parent.height +1
                    radius:parent.radius
                    color: Material.accent
                }
            }
        }
    }

}
