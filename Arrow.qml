import QtQuick 2.0

Canvas {
    id: vector
    width: 400
    height: 400

    property color color: "#03a"

    opacity: 0.5
    property double m2px: 100
    property double dx: 1
    property double dy: 0
    property double scaling: 0.5

    onDxChanged: requestPaint()
    onDyChanged: requestPaint()

    onPaint: {
        var ctx = getContext("2d");
        ctx.reset();

        var centreX = width / 2;
        var centreY = height / 2;
        var len = Math.sqrt(dx**2 + dy**2) * m2px * scaling;

            
        ctx.translate(centreX,centreY);
        ctx.rotate(Math.atan2(dy, dx));
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.moveTo(0,0);
        ctx.lineTo(len, 0);
        ctx.lineTo(len -5, 5);
        ctx.moveTo(len, 0);
        ctx.lineTo(len -5, -5);
        ctx.stroke()
    }
}
