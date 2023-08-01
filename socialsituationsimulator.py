import sys

from pathlib import Path
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QStringListModel, QUrl, Slot, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class Bridge(QObject):
    def __init__(self):
        super().__init__()
        self.persons = {}

    @Slot(str, float, float, float)
    def updatePosition(self, name, x, y, theta):
        self.persons[name] = (x, y)
        print(
            "Person <%s> is at %.2f, %.2f (m); orientation: %.1fdeg"
            % (name, x, y, theta)
        )


if __name__ == "__main__":

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    qml_file = Path(__file__).parent / "app.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
