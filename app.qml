import QtQuick 2.14
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.1
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

import io.qt.textproperties 1.0

ApplicationWindow {
    id: simulator
    width: 800
    height: 800
    visible: true
    //Material.theme: Material.Dark
    //Material.accent: Material.Red

    property double m2px: 100 // 100px = 1m

    Bridge {
        id: bridge

    }

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            ToolButton {
                text: qsTr("‹")
                focusPolicy: Qt.NoFocus
                onClicked: stack.pop()
            }
            Label {
                text: "Social Situation Simulator"
                elide: Label.ElideRight
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                Layout.fillWidth: true
            }
            Button {
                id: btn_add_agent
                text: "+"
                highlighted: true
                focusPolicy: Qt.NoFocus
                Material.accent: Material.Green
                onClicked: {
                    agents.addAgent();
                }
            }
            ToolButton {
                text: qsTr("Save")
                focusPolicy: Qt.NoFocus
                onClicked: saveFileDialog.open()
            }
            ToolButton {
                text: qsTr("Load")
                focusPolicy: Qt.NoFocus
                onClicked: loadFileDialog.open()
            }
            ToolButton {
                text: qsTr("⋮")
                focusPolicy: Qt.NoFocus
                onClicked: menu.open()
            }
        }
    }

    FileDialog {
        id: saveFileDialog
        fileMode: FileDialog.SaveFile
        nameFilters: ["JSON files (*.json)", "All files (*)"]
        onAccepted: timeline.save(saveFileDialog.selectedFile)
    }

    FileDialog {
        id: loadFileDialog
        fileMode: FileDialog.OpenFile
        nameFilters: ["JSON files (*.json)", "All files (*)"]
        onAccepted: timeline.load(loadFileDialog.selectedFile)
    }

    footer: ToolBar{
        RowLayout {
            anchors.fill: parent
            Timeline {
                id: timeline
                x: 5
                scene: agents
            }
        }
    }



    // draw the background grid
    Repeater {
        model:10
        Rectangle {

            x: simulator.width/2 - width/2
            y: simulator.height/2 - height/2

            width: m2px * 2 * (index + 1);
            height:width;
            radius:width/2

            color:"transparent"
            border.width:2
            border.color: "#ddd"
        }
    }
    MouseArea {
        id: winArea
        anchors.fill: parent
        onClicked: {
            agents.focus=true
        }

    }


    Item {
        focus:true
        id:agents

        Agent {
            x_m: 0; y_m: 0;
            name: "robot"
            m2px: simulator.m2px
            origin_x: (simulator.width/2) / m2px
            origin_y: (simulator.height/2) / m2px
        }


        Component.onCompleted: {
            addAgent()
        }


        property int idx: 0;
        function addAgent() {

            const agents_list = [{name:"John", color: "orange"},
            {name:"Emily", color: "blue"},
            {name:"Will", color: "green"},
            {name:"Violet", color: "purple"},
            {name:"Jane", color: "red"},
            {name:"Bob", color: "orange"},
            {name:"Mary", color: "blue"},
            {name:"Matthew", color: "green"},
            {name:"Edith", color: "purple"},
            {name:"Thomas", color: "red"},
        ]

        const component = Qt.createComponent("Agent.qml");
        var new_agent = component.createObject(agents,
        {
            x_m: -2 + 1.0 * Math.floor(idx / 5), 
            y_m: -2 + 1.0 * (idx % 5 ), 
            color: agents_list[idx].color, 
            name: agents_list[idx].name, 
            m2px:Qt.binding(function() {return m2px}),
            origin_x: Qt.binding(function(){return (simulator.width/2) / m2px}),
            origin_y: Qt.binding(function(){return (simulator.height/2) / m2px}),
        });

        idx = (idx + 1) % agents_list.length;

        if (new_agent == null) {
            // Error Handling
            console.log("Error creating object");
        }
    }

    Keys.onPressed: (event) => {
        if (event.key === Qt.Key_Space) {
            timeline.updateKeyframe(agents);
        }
        if (event.key === Qt.Key_Delete) {
            timeline.deleteKeyframe();
        }
        if (event.key === Qt.Key_Return) {
            bridge.describe(timeline.toJson());
        }
    }

}


WheelHandler {
    //property: "rotation"
    onWheel: (event)=> {
        m2px = Math.max(50, Math.min(400, m2px + 15 * event.angleDelta.y/Math.abs(event.angleDelta.y)));
    }
}
}
