import QtQuick 2.14
import QtQuick.Controls 2.12


ApplicationWindow {
    id: simulator
    width: 800
    height: 800
    visible: true

    property double m2px: 100 // 100px = 1m

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


    Agent {
        x: 400; y:400;
        color: "orange"
        name: "robot"
        m2px: simulator.m2px
        origin_x: parent.width/2
        origin_y: parent.height/2
    }

    Agent {
        x: 100; y:100;
        color: "red"
        name: "A"
        m2px: simulator.m2px
        origin_x: parent.width/2
        origin_y: parent.height/2
    }
    Agent {
        x: 100; y:200;
        color: "blue"
        name: "B"
        m2px: simulator.m2px
        origin_x: parent.width/2
        origin_y: parent.height/2
    }
    Agent {
        x: 100; y:300;
        color: "green"
        name: "C"
        m2px: simulator.m2px
        origin_x: parent.width/2
        origin_y: parent.height/2
    }
    Agent {
        x: 100; y:400;
        color: "purple"
        name: "D"
        m2px: simulator.m2px
        origin_x: parent.width/2
        origin_y: parent.height/2
    }
     WheelHandler {
        //property: "rotation"
        onWheel: (event)=> {
            m2px = Math.max(50, Math.min(400, m2px + 15 * event.angleDelta.y/Math.abs(event.angleDelta.y)));
                }
    }
}
