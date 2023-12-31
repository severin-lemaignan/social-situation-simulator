import QtQuick 2.14
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.1
import QtQuick.Layouts 1.15

Item {
    id:timeline

    property int fps: 2
    property int duration: 10 // sec

    property alias implicitWidth: timeline_slider.implicitWidth
    property alias value: timeline_slider.value

    property var timeline_data: new Object();
    property var timeline_data_model: [];

    property var scene;

    property bool playing: false

    anchors.fill: parent
    RowLayout {
        anchors.fill: parent
        ToolButton {
            icon.name: playing ? "media-playback-pause" : "media-playback-start"
            focusPolicy: Qt.NoFocus
            onClicked: {
                if (playing) {
                    stop();
                } else {
                    play();
                }
            }
        }
        Slider {
            id:timeline_slider
            Layout.fillWidth:true
            x: timeline.x
            snapMode: Slider.SnapAlways
            from:0
            to: timeline.duration
            stepSize: 1/timeline.fps

            focusPolicy: Qt.NoFocus

            onMoved: {
                playing = false;
            }

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
                        y:-20
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


            onValueChanged: refreshScene()


        }
    }


    function refreshScene() {

        var new_scene = {}

        var timestamps = Object.keys(timeline_data).map(x => parseFloat(x)).sort(function(a,b) { return a - b;});

        //console.log("Current time: " + value);
        //console.log("Timestamps: " + timestamps);

        // outside of the timestamp range? return
        if (value < Math.min(...timestamps) || value > Math.max(...timestamps)) {
            return
        }

        if (value.toString() in timeline_data) {
            new_scene = timeline_data[value.toString()].scene;
        }
        else {
            // find prev and next timestamps
            var prev_t = timestamps[0];
            var next_t = 0;

            for (var i = 1; i < timestamps.length; i++) {
                if (value < timestamps[i]) {
                    next_t = timestamps[i];
                    break;
                }
                else {
                    prev_t = timestamps[i];
                }
            }

            // interpolate
            for (const name in timeline_data[prev_t.toString()].scene) {
                new_scene[name] = interpolate(
                    timeline_data[prev_t.toString()].scene[name],
                    prev_t,
                    timeline_data[next_t.toString()].scene[name],
                    next_t,
                    value);
             }
        }

        for (var i = 0; i < scene.children.length; i++) {
            var agent = scene.children[i];

            if (agent.name in new_scene) {
                agent.deserialize(new_scene[agent.name]);
            }
        }
    }

    function setScene(new_scene) {
        for (var i = 0; i < scene.children.length; i++) {
            var agent = scene.children[i];

            if (agent.name in new_scene) {
                agent.deserialize(new_scene[agent.name]);
            }
        }
    }

    function wrap_angle(a) {
        const r = a % 360;
        if(r>180) {return r-360}
        return r;
    } 

    // interpolate between two objects whose values are numbers, at time t between t_a and t_b
    function interpolate(a,t_a,b,t_b,t) {
        const zip = (a,b) => a.map((k, i) => [k, b[i]]);

        const ab = zip(Object.values(a), Object.values(b));

        //console.log("at " + t_a + ": " + Object.values(a));
        //console.log("at " + t_b + ": " + Object.values(b));
        const vals = ab.map(v => {
            if (typeof(v[0]) === "number") {
                return v[0] + (v[1]-v[0])/(t_b-t_a)*(t-t_a);
            } else {
                return v[0];
            }
        });
        //console.log("  => at " + t + ": " + vals);

        var result = Object.assign({}, a);
        var idx = 0
        for (const k in result) {
            result[k] = vals[idx];
            idx++
        }

        // fixes for 'special' values:

        // wrap angles
        result.theta = a.theta + (wrap_angle(b.theta-a.theta))/(t_b-t_a)*(t-t_a);

        // speed remain constant between frames
        result.vx = a.vx;
        result.vy = a.vy;

        return result;
    }

    function updateKeyframe() {

        var frame = {scene:{},ts: value};

        for (var i = 0; i < scene.children.length; i++) {
            var agent = scene.children[i];
            frame["scene"][agent.name] = agent.serialize();
        }

        timeline_data[value.toString()] = frame;

        recomputeVelocities();

        timeline_data_model = Object.values(timeline_data);

        console.log(JSON.stringify(timeline_data));
    }


    function deleteKeyframe() {

        for (var i = 0; i < keyframe_handles.count; i++) {
            var kf = keyframe_handles.itemAt(i);
            if (kf.selected) {
                delete timeline_data[kf.ts];
            }
        }

        timeline_data_model = Object.values(timeline_data);

    }

    function toJson() {
        return JSON.stringify(timeline_data);
    }

    function save(fileUrl) {
        var json = toJson();
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.HEADERS_RECEIVED) {
                //print('HEADERS_RECEIVED')
            } else if(xhr.readyState === XMLHttpRequest.DONE) {
                console.log("Saved to " + fileUrl);
                //print('DONE')
            }
        }
        xhr.open("PUT", fileUrl);
        xhr.send(json);

    }

    function load(fileUrl, agents) {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.HEADERS_RECEIVED) {
                //print('HEADERS_RECEIVED')
            } else if(xhr.readyState === XMLHttpRequest.DONE) {
                //print('DONE')
                timeline_data = JSON.parse(xhr.responseText.toString());

                // wtf javascript??? by default sort() converts everything to strings first...!
                var timestamps = Object.keys(timeline_data).map(x => parseFloat(x)).sort(function(a,b) { return a - b;});

                duration = timestamps[timestamps.length-1] - timestamps[0]


                recomputeVelocities();
                timeline_data_model = Object.values(timeline_data);

                agents.deleteAll();
                for (var name in timeline_data[timeline_data_model[0].ts].scene) {
                    agents.addAgent(name);
                }

                value = timestamps[0];
                refreshScene();
            }
        }
        xhr.open("GET", fileUrl);
        xhr.send();

    }

    PropertyAnimation {
        id: play_animation
        property: "value"
        target: timeline
        from: value
        to: timeline.duration
        duration: (timeline.duration - timeline.value) * 1000
        running: timeline.playing

        onFinished: {
            timeline.playing = false
        }
    }

    function play() {
        if (playing) {return;}

        // if we are at the end, jump at the beginning
        if (value == duration) {
            value = 0;
        }

        playing = true;
    }

    function stop() {
        if (!playing) {return;}
        playing = false;
    }

    function togglePlay() {
        playing ? stop() : play()
    }

    /** at each keyframe, compute the velocity of each the agent that
        * would take it to the next keyframe, and store it in the 
        * timeline_data structure.
        *
        * At the last keyframe, the velocity is set to 0.
        */
    function recomputeVelocities() {

        var timestamps = Object.keys(timeline_data).map(x => parseFloat(x)).sort(function(a,b) { return a - b;});

        if (timestamps.length == 0) {
            return;
        }
        if (timestamps.length == 1) {
            var scene = timeline_data[timestamps[0].toString()].scene;

            for (var name in scene) {
                scene[name]["vx"] = 0;
                scene[name]["vy"] = 0;
            }
        }


        var prev_ts = timestamps[0];

        for (var ts of timestamps.slice(1)) {

            var dt = ts - prev_ts;

            var scene = timeline_data[ts.toString()].scene;
            var prev_scene = timeline_data[prev_ts.toString()].scene;

            for (var name in scene) {

                var x = scene[name].x;
                var y = scene[name].y;

                // name might not exist in previous scene if the agent
                // has just been added
                if (name in prev_scene) {
                    var prev_x = prev_scene[name].x;
                    var prev_y = prev_scene[name].y;

                    prev_scene[name]["vx"] = (x-prev_x)/dt;
                    prev_scene[name]["vy"] = (y-prev_y)/dt;
                }

                scene[name]["vx"] = 0;
                scene[name]["vy"] = 0;
            }

            prev_ts = ts;

        }
    }

}
