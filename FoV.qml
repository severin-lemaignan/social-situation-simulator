import QtQuick 2.0
Canvas {
    id: field_of_view
    width: 200
    height: 200

    property color color: "#44dd4444"

    property int fov: 60 // field of view, in degrees
    property int foa: fov // field of attention, in degrees

    property int radius: width/2

    property bool fovVisible: true
    onFovVisibleChanged: requestPaint()
    property bool outOfFov: false
    onOutOfFovChanged: requestPaint()

    onPaint: {
        var ctx = getContext("2d");
        ctx.reset();

            var centreX = width / 2;
            var centreY = height / 2;

            var halfFov = Math.PI / 180 * fov/ 2;
            var halfFoa = Math.PI / 180 * foa/ 2;

            if (fovVisible) {
                ctx.beginPath();
                ctx.fillStyle = color;
                ctx.moveTo(centreX, centreY);
                ctx.arc(centreX, centreY, radius, -halfFov, halfFov, false);
                ctx.lineTo(centreX, centreY);
                ctx.fill();

                ctx.beginPath();
                ctx.fillStyle = color;
                ctx.moveTo(centreX, centreY);
                ctx.arc(centreX, centreY, radius, -halfFoa, halfFoa, false);
                ctx.lineTo(centreX, centreY);
                ctx.fill();
                
                ctx.beginPath();
                ctx.strokeStyle = "black"
                ctx.lineWidth = 2;
                ctx.moveTo(centreX + radius * Math.cos(halfFov),  centreY + radius * Math.sin(halfFov));
                ctx.lineTo(centreX,centreY);
                ctx.lineTo(centreX + radius * Math.cos(-halfFov),  centreY + radius * Math.sin(-halfFov));
                ctx.stroke()
            }


            if (outOfFov) {

                const gradient = ctx.createConicalGradient(centreX, centreY,0);

                const idx = (fov/2)/360;
                console.log(idx);
                gradient.addColorStop(idx - 0.03, "#00000000");
                gradient.addColorStop(idx, "black");
                gradient.addColorStop(1-idx, "black");
                gradient.addColorStop(1-idx+0.03, "#00000000");

                ctx.fillStyle = gradient;
                ctx.fillRect(centreX-10*radius, centreY-10*radius, 20*radius,  20*radius);
            }
    }
}
