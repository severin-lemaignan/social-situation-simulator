import QtQuick 2.12
import QtQuick.Controls 2.12

Item {

    id: agent

    property double gaze_direction: 0.0 // gaze direction, in degrees.
    property string name
    objectName: "agent_" + name

    property double m2px: 100

    // coordinates, in meters
    property double x_m: 0
    property double y_m: 0

    // velocity -- computed and set by the timeline
    property double vx_m: 0
    property double vy_m: 0

    x: (x_m + origin_x) * m2px; y: (y_m + origin_y) * m2px

    property string color: "green"

    property double origin_x: 0
    property double origin_y: 0

    property bool selected: false

    property bool talking: false
    property var engaged_with: []

    // handle to the timeline, used to enable/disable 'talking'
    property var timeline;

    FoV {
        width: 200
        height: 200
        rotation: agent.gaze_direction
        opacity: parent.selected ? 1 : 0.5
        fov: 100
        foa: 30
        x: parent.width/2-width/2
        y: parent.height/2-height/2


        Image {
            id: gaze_handle
            source: "res/rotate.svg"

            width:30
            height:30

            x: parent.width/2 -width/2 + 0.3 * m2px
            y: parent.height/2 - height/2

            Drag.active: gazeDragArea.drag.active


            MouseArea {
                id: gazeDragArea
                anchors.fill: parent

                drag.target: rotation_target
            }
        }


    }

    Item {
        id: rotation_target

        property int position: x+y
        onPositionChanged: {

            agent.gaze_direction = Math.atan2(y+agent.height/2,x+agent.width/2) * 180/Math.PI;
        }
    }

    Image {
        id: selection_shadow
        width: 0.5 * m2px + 5
        height: width * 0.8
        rotation: parent.gaze_direction + 90
        transformOrigin: Item.Center
        x: - width/2
        y: - height/2
        source: parent.name === "robot" ? "res/robot_selected.svg" : "res/people_selected.svg" 

        visible: parent.selected
    }

    Image {
        id: body
        width: 0.5 * m2px
        height: width * 0.8
        //radius: width/4
        rotation: parent.gaze_direction + 90
        transformOrigin: Item.Center
        x: - width/2
        y: - height/2
        property string color: parent.color
        source: parent.name === "robot" ? "res/robot.svg" : "res/people_" + color + ".svg" 

        Drag.active: dragArea.drag.active
        Drag.hotSpot.x: 10
        Drag.hotSpot.y: 10
        Drag.onActiveChanged: {
            if (!Drag.active) {
                parent.x_m = parent.x/m2px - origin_x;
                parent.y_m = parent.y/m2px - origin_y;
                //console.log(parent.name + " is now at " + parent.x_m + ", " + parent.y_m);
            }
        }

        MouseArea {
            id: dragArea
            anchors.fill: parent

            drag.target: parent.parent

            onClicked: agent.selected = !agent.selected

        }



    }

    Arrow {
        id: velocity
        width: 400
        height: 400
        dx: vx_m
        dy: vy_m
        m2px: agent.m2px
        x: parent.width/2-width/2
        y: parent.height/2-height/2
        opacity: 0.5
    }

    Button {
        id: speech_bubble
        icon.name: "user-idle-symbolic"
        visible: talking
        x: -20
        y: -50
        background:Item{} 
        focusPolicy: Qt.NoFocus

        onClicked: {
            talking=false;
            timeline.updateKeyframe();
        }
    }

    Button {
        id: engaged
        icon.name: "send-to-symbolic"
        visible: engaged_with.length !== 0
        background: Item{} 
        focusPolicy: Qt.NoFocus
        anchors.left: speech_bubble.right
        anchors.leftMargin: 4
        y: -50

        onClicked: {
            engaged_with=[];
            timeline.updateKeyframe();
        }



    }


    Text {
        y: body.height/2 + 5
        x: -body.width/2 + 2
        text: "<i>"+name+"</i>"
        color: "#333"
    }

    function serialize() {
        return {x: x_m, 
            y: y_m, 
            theta: gaze_direction, 
            vx: vx_m, 
            vy: vy_m, 
            talking: talking, 
            engaged_with: engaged_with
        };
    }

    function deserialize(state) {
        x_m = state.x;
        y_m = state.y;
        gaze_direction = state.theta;

        vx_m = state.vx;
        vy_m = state.vy;

        if ("talking" in state) {
            talking = state.talking;
        }

        if ("engaged_with" in state) {
            engaged_with = state.engaged_with;
        }
    }
}
