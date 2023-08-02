import QtQuick 2.14
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.1
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: simulator
    width: 800
    height: 800
    visible: true
    //Material.theme: Material.Dark
    //Material.accent: Material.Red

    property double m2px: 100 // 100px = 1m


    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            ToolButton {
                text: qsTr("‹")
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
                Material.accent: Material.Green
                onClicked: {
                    agents.addAgent()
                }
            }
            ToolButton {
                text: qsTr("⋮")
                onClicked: menu.open()
            }
        }
    }

    footer: ToolBar{
        RowLayout {
            anchors.fill: parent
            Slider {
                id:timeline
                x: 5
                implicitWidth:parent.width - 10
                width:implicitWidth
                snapMode: Slider.SnapAlways
                property int fps: 2
                property int duration: 10 // sec
                from:0
                to: duration
                stepSize: 1/fps
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


    Item {
        id:agents

        Agent {
            x: 400; y:400;
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

    }
    WheelHandler {
        //property: "rotation"
        onWheel: (event)=> {
            m2px = Math.max(50, Math.min(400, m2px + 15 * event.angleDelta.y/Math.abs(event.angleDelta.y)));
        }
    }
    }
