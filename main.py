# main.py
from mainwindow import MainWindow
from uploadscreen import UploadScreen
from PyQt5.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)  # Initialize QApplication
    upload_screen = UploadScreen()  # Create upload screen instance
    main_window = None

    def launch_main_window(nifti_file_path):
        """
        Launch the main window.
        :param nifti_file_path: Path to the loaded NIfTI file
        """
        global main_window
        upload_screen.close()
        main_window = MainWindow(nifti_file_path)
        main_window.show()

    upload_screen.nifti_loaded.connect(launch_main_window) # Connect the signal from upload screen
    upload_screen.show()

    sys.exit(app.exec_()) # Start the event loop


if __name__ == "__main__":
    main()
