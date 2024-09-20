# main.py
from windows.main_window import MainWindow
from windows.init_window import InitWindow
from PyQt5.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)  # Init QApplication
    init_window = InitWindow()  # InitWindow instance
    main_window = None

    def launch_main_window(nifti_file_path):
        """
        Launch the main window.
        """
        global main_window
        init_window.close()
        main_window = MainWindow(nifti_file_path)
        main_window.show()

    init_window.nifti_loaded.connect(launch_main_window)
    init_window.show()

    sys.exit(app.exec_())  # Start the event loop

if __name__ == "__main__":
    main()
