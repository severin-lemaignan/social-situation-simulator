import QtQuick 2.12
import QtQuick.Controls 2.12

import io.qt.textproperties 1.0

Item {

    id: agent

    property double gaze_direction: 0.0 // gaze direction, in degrees.
    property string name

    x: 10; y: 10
    property int position: x+y // property that will change if either X or Y change, so that we can have a onPositionChanged callback
    property string color: "green"

    property double m2px: 100
    property int origin_x: 0
    property int origin_y: 0


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

        MouseArea {
            id: dragArea
            anchors.fill: parent

            drag.target: parent.parent
        }
    }

    Bridge {
        id: bridge
    }

    onPositionChanged: {
        bridge.updatePosition(name, (x-origin_x)/m2px, (y-origin_y)/m2px, gaze_direction);
    }

    onGaze_directionChanged: {
        bridge.updatePosition(name, (x-origin_x)/m2px, (y-origin_y)/m2px, gaze_direction);
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
