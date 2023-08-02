import QtQuick 2.12
import QtQuick.Controls 2.12

import io.qt.textproperties 1.0

Item {

    id: agent

    property double gaze_direction: 0.0 // gaze direction, in degrees.
    property string name

    property double m2px: 100

    // coordinates, in meters
    property double x_m: 0
    property double y_m: 0

    x: (x_m + origin_x) * m2px; y: (y_m + origin_y) * m2px

    property double position: x_m+y_m // property that will change if either X or Y change, so that we can have a onPositionChanged callback

    property string color: "green"

    property double origin_x: 0
    property double origin_y: 0

    property bool selected: false

    FoV {
        width: 200
        height: 200
        rotation: agent.gaze_direction
        opacity: parent.selected ? 1 : 0.5
        fov: 100
        foa: 30
        x: parent.width/2-width/2
        y: parent.height/2-height/2
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
            bridge.updatePosition(name, x_m, y_m, gaze_direction);
        }
        }

        MouseArea {
            id: dragArea
            anchors.fill: parent

            drag.target: parent.parent

            onClicked: agent.selected = !agent.selected

        }



    }

    Bridge {
        id: bridge
    }


    onGaze_directionChanged: {
        bridge.updatePosition(name, x_m, y_m, gaze_direction);
    }

    Component.onCompleted: {
        bridge.updatePosition(name, x_m, y_m, gaze_direction);
    }


    Rectangle {
        id: gaze
        width:5; height:width
        radius:width/2

        color: "black"

        x: parent.width/2-width/2 + 30 * Math.cos(parent.gaze_direction * Math.PI/180)
        y: parent.height/2-height/2 + 30 * Math.sin(parent.gaze_direction * Math.PI/180)
    }

    Rectangle {
        id: gaze_handle
        //anchors.fill: gaze
        color: "transparent"

        width:20
        height:20

        x:0
        y:0

        Binding on x {
            when: !gazeDragArea.drag.active
            value: gaze.x
        }

        Binding on y {
            when: !gazeDragArea.drag.active
            value: gaze.y
        }

        property int position: x+y

        Drag.active: gazeDragArea.drag.active

        MouseArea {
            id: gazeDragArea
            anchors.fill: parent

            drag.target: parent
        }

        onPositionChanged: {

            if (gazeDragArea.drag.active) {
                parent.gaze_direction = Math.atan2(y-height/2+parent.height/2,x-width/2+parent.width/2) * 180/Math.PI;
            }
        }
    }

    Text {
        y: body.height/2 + 5
        x: -body.width/2 + 2
        text: "<i>"+name+"</i>"
        color: "#333"
    }
}
