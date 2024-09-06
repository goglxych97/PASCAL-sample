# main.py
import sys
from PyQt5.QtWidgets import QApplication
from mainwindow import MainWindow
from uploadscreen import UploadScreen


def main():
    """
    Entry point for the application. Sets up the application, upload screen, 
    and launches the main window after loading a NIfTI file.
    """
    app = QApplication(sys.argv)  # Initialize the QApplication
    upload_screen = UploadScreen()  # Create the upload screen instance
    main_window = None  # Placeholder for the main window

    def launch_main_window(nifti_file_path, shape):
        """
        Launch the main window after a NIfTI file is loaded.
        :param nifti_file_path: Path to the loaded NIfTI file
        :param shape: Shape of the NIfTI image
        """
        global main_window
        upload_screen.close()
        main_window = MainWindow(nifti_file_path, shape)
        main_window.show()

    # Connect the signal from upload screen to the function that launches the main window
    upload_screen.nifti_loaded.connect(launch_main_window)
    upload_screen.show()

    # Start the event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
