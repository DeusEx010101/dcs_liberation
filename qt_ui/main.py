from userdata import logging_config

# Logging setup
VERSION_STRING = "2.0RC7"
logging_config.init_logging(VERSION_STRING)

import logging
import os
import sys

import dcs
from PySide2 import QtWidgets
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QSplashScreen

from qt_ui import uiconstants
from qt_ui.windows.GameUpdateSignal import GameUpdateSignal
from qt_ui.windows.QLiberationWindow import QLiberationWindow
from qt_ui.windows.preferences.QLiberationFirstStartWindow import QLiberationFirstStartWindow
from userdata import liberation_install, persistency

if __name__ == "__main__":

    app = QApplication(sys.argv)

    css = ""
    with open("./resources/stylesheets/style.css") as stylesheet:
        app.setStyleSheet(stylesheet.read())




    # Inject custom payload in pydcs framework
    custom_payloads = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..\\resources\\customized_payloads")
    if os.path.exists(custom_payloads):
        dcs.planes.FlyingType.payload_dirs.append(custom_payloads)
    else:
        # For release version the path is different.
        custom_payloads = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       "resources\\customized_payloads")
        if os.path.exists(custom_payloads):
            dcs.planes.FlyingType.payload_dirs.append(custom_payloads)


    first_start = liberation_install.init()
    if first_start:
        window = QLiberationFirstStartWindow()
        window.exec_()

    logging.info("Using {} as 'Saved Game Folder'".format(persistency.base_path()))
    logging.info("Using {} as 'DCS installation folder'".format(liberation_install.get_dcs_install_directory()))

    # Splash screen setup
    pixmap = QPixmap("./resources/ui/splash_screen.png")
    splash = QSplashScreen(pixmap)
    splash.show()

    # Once splash screen is up : load resources & setup stuff
    uiconstants.load_icons()
    uiconstants.load_event_icons()
    uiconstants.load_aircraft_icons()
    uiconstants.load_vehicle_icons()

    # Replace DCS Mission scripting file to allow DCS Liberation to work
    try:
        liberation_install.replace_mission_scripting_file()
    except:
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.setWindowTitle("Wrong DCS installation directory.")
        error_dialog.showMessage("Unable to modify Mission Scripting file. Possible issues with rights. Try running as admin, or please perform the modification of the MissionScripting file manually.")
        error_dialog.exec_()

    # Apply CSS (need works)
    GameUpdateSignal()

    # Start window
    window = QLiberationWindow()
    window.showMaximized()
    splash.finish(window)
    qt_execution_code = app.exec_()

    # Restore Mission Scripting file
    logging.info("QT App terminated with status code : " + str(qt_execution_code))
    logging.info("Attempt to restore original mission scripting file")
    liberation_install.restore_original_mission_scripting()
    logging.info("QT process exited with code : " + str(qt_execution_code))
    sys.exit(0)


