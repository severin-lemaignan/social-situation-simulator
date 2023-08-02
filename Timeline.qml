import QtQuick 2.14
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.1

Item {
    id:timeline

    property int fps: 2
    property int duration: 10 // sec

    property alias implicitWidth: timeline_slider.implicitWidth
    property alias value: timeline_slider.value

    property var timeline_data: new Object();
    property var timeline_data_model: [];

    Slider {
        id:timeline_slider
        width:implicitWidth
        x: timeline.x
        snapMode: Slider.SnapAlways
        from:0
        to: timeline.duration
        stepSize: 1/timeline.fps

        focusPolicy: Qt.NoFocus

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
            Repeater {
                id: keyframe_handles
                model: timeline_data_model
                delegate: Rectangle {
                        x: modelData.ts * parent.width / timeline.duration - width / 2
                        y:24
                        width: 10
                        height: width
                        radius: width/2
                        color: selected ? "orange" : "black"

                        property double ts: modelData.ts

                        property bool selected: false

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {selected=!selected;}
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


    function updateKeyframe(scene) {

        var frame = {scene:{},ts: value};

        for (var i = 0; i < scene.children.length; i++) {
            var agent = scene.children[i];
            frame["scene"][agent.name] = agent.serialize();
        }

        timeline_data[value.toString()] = frame;
        timeline_data_model = Object.values(timeline_data);

        console.log(JSON.stringify(timeline_data));
    }

    function deleteKeyframe() {

        for (var i = 0; i < keyframe_handles.count; i++) {
            var kf = keyframe_handles.itemAt(i);
            if (kf.selected) {
                console.log("Deleting keyframe " + kf.ts);
                delete timeline_data[kf.ts];
            }
        }

        timeline_data_model = Object.values(timeline_data);

    }

}
