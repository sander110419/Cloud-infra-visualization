from PyQt5.QtWidgets import QApplication, QFileDialog, QScrollArea, QComboBox, QTextEdit, QWidget, QVBoxLayout, QPushButton, QDialog, QLineEdit, QFormLayout, QListWidgetItem, QListWidget, QCheckBox, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QProcess
from functions import authenticate_to_azure, get_subscriptions
import sys
import os
import subprocess
import platform
import keyring

try:
    def get_subscriptions(subscription_client, subscription_id):
        if subscription_id:
            subscriptions = [(subscription_id)]
        else:
            subscriptions = [(sub.subscription_id, sub.display_name) for sub in subscription_client.subscriptions.list()]

        return subscriptions

    class AzureAuthApp(QWidget):
        def __init__(self):
            super().__init__()

            self.tenant_id = None
            self.client_id = None
            self.client_secret = None
            self.subscriptions = []
            self.selected_subscription_id = None
            self.current_identity = None

            self.initUI()
            screen = QApplication.desktop().screenGeometry()
            self.resize(800, screen.height())  # Set the default width to 800 and height to the maximum size of the screen

        def handle_error(self, error):
            self.outputTextEdit.append(f"An error occurred while running main.py: {error}")

        def initUI(self):
            layout = QVBoxLayout()

            self.label = QLabel("Please choose an identity or create a new one")
            layout.addWidget(self.label)

            self.loadIdentityButton = QPushButton('Load Identity', self)
            self.loadIdentityButton.clicked.connect(self.load_identity)
            layout.addWidget(self.loadIdentityButton)

            self.newIdentityButton = QPushButton('New Identity', self)
            self.newIdentityButton.clicked.connect(self.showDialog)
            self.useCertificateCheckbox = QCheckBox("Use Certificate")
            self.useCertificateCheckbox.stateChanged.connect(self.toggle_certificate_input)

            self.clientSecretInput = QLineEdit()
            self.certificatePathInput = QLineEdit()
            self.browseCertificateButton = QPushButton('Browse')
            self.browseCertificateButton.clicked.connect(lambda: self.browse_for_certificate(self.certificatePathInput))

            # Initially hide the certificate path input and browse button
            self.certificatePathInput.hide()
            self.browseCertificateButton.hide()
            layout.addWidget(self.newIdentityButton)

            self.listWidget = QListWidget()
            layout.addWidget(self.listWidget)
            self.listWidget.itemChanged.connect(self.on_item_changed)

            self.advancedButton = QPushButton('Advanced', self)
            self.advancedButton.clicked.connect(self.toggle_advanced_options)
            layout.addWidget(self.advancedButton)

            self.scrollArea = QScrollArea()
            self.scrollArea.setWidgetResizable(True)
            self.scrollAreaWidgetContents = QWidget()
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)

            self.advancedLayout = QVBoxLayout(self.scrollAreaWidgetContents)

            self.outputExcelCheckbox = QCheckBox("Output to Excel")
            self.outputDrawIOCheckbox = QCheckBox("Output to DrawIO")
            self.outputDocxCheckbox = QCheckBox("Output to Docx")
            self.outputHtmlCheckbox = QCheckBox("Output to HTML")

            self.advancedLayout.addWidget(self.outputExcelCheckbox)
            self.advancedLayout.addWidget(self.outputDrawIOCheckbox)
            self.advancedLayout.addWidget(self.outputDocxCheckbox)
            self.advancedLayout.addWidget(self.outputHtmlCheckbox)

            self.resourceGroupNameInput = QLineEdit()
            self.resourceGroupTagKeyInput = QLineEdit()
            self.resourceGroupTagValueInput = QLineEdit()
            self.resourceTagKeyInput = QLineEdit()
            self.resourceTagValueInput = QLineEdit()
            self.output_folder_input = QLineEdit()
            self.browseButton = QPushButton('Browse')
            self.browseButton.clicked.connect(lambda: self.browse_for_folder(self.output_folder_input))

            self.advancedLayout.addWidget(QLabel('Resource group name:'))
            self.advancedLayout.addWidget(self.resourceGroupNameInput)
            self.advancedLayout.addWidget(QLabel('Resource group tag key:'))
            self.advancedLayout.addWidget(self.resourceGroupTagKeyInput)
            self.advancedLayout.addWidget(QLabel('Resource group tag value:'))
            self.advancedLayout.addWidget(self.resourceGroupTagValueInput)
            self.advancedLayout.addWidget(QLabel('Resource tag key:'))
            self.advancedLayout.addWidget(self.resourceTagKeyInput)
            self.advancedLayout.addWidget(QLabel('Resource tag value:'))
            self.advancedLayout.addWidget(self.resourceTagValueInput)
            self.advancedLayout.addWidget(QLabel('Output folder:'))
            self.advancedLayout.addWidget(self.output_folder_input)
            #default output folder is /output in current directory
            self.output_folder_input.setText(os.path.join(os.getcwd(), 'output'))
            self.advancedLayout.addWidget(self.browseButton)

            layout.addWidget(self.scrollArea)

            self.runButton = QPushButton('Start document generation', self)
            self.runButton.clicked.connect(self.run_main_py)
            layout.addWidget(self.runButton)

            self.outputTextEdit = QTextEdit()
            layout.addWidget(self.outputTextEdit)

            self.setLayout(layout)

            # Initially hide the advanced options
            self.scrollArea.hide()

            # Apply a stylesheet
            self.setStyleSheet("""
                QWidget {
                    font: 12pt "Segoe UI";
                    color: #FFFFFF;
                    background-color: #2D2D30;
                }
                QPushButton {
                    background-color: #3C3C3F;
                    border: 1px solid #5E5E62;
                    padding: 5px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #5E5E62;
                }
                QPushButton:pressed {
                    background-color: #707070;
                }
                QLabel {
                    font: bold 14pt "Segoe UI";
                }
                QTextEdit {
                    background-color: #1E1E1E;
                    border: none;
                    color: #DCDCDC;
                }
                QCheckBox {
                    background-color: light gray,
                    padding: 5px;
                    spacing: 5px;
                }
                QCheckBox::indicator:checked {
                    background-color: blue;
                    border: 2px solid black;
                }
                QCheckBox::indicator:unchecked {
                    background-color: white;
                    border: 2px solid black;
                }
                QCheckBox::indicator {
                    width: 13px;
                    height: 13px;
                }
                QLineEdit {
                    border: 1px solid #DCDCDC;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #2D2D30;
                    width: 10px;
                    margin: 15px 0 15px 0;
                    border-radius: 0px;
                }
                QScrollBar::handle:vertical {   
                    background-color: #888;
                    min-height: 30px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover{ 
                    background-color: #555;
                }
                QScrollBar::add-line:vertical {
                    height: 15px;
                    subcontrol-position: bottom;
                    subcontrol-origin: margin;
                }
                QScrollBar::sub-line:vertical {
                    height: 15px;
                    subcontrol-position: top;
                    subcontrol-origin: margin;
                }
                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                    border: none;
                    width: 3px;
                    height: 3px;
                    background: transparent;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
            """)
        def toggle_certificate_input(self, state):
            if state == Qt.Checked:
                self.clientSecretInput.hide()
                self.certificatePathInput.show()
                self.browseCertificateButton.show()
            else:
                self.clientSecretInput.show()
                self.certificatePathInput.hide()
                self.browseCertificateButton.hide()

        def load_identity(self, identity=None, tenant_id=None, client_id=None, client_secret=None, certificate_path=None):
            if tenant_id and client_id and (client_secret or certificate_path):
                self.set_credentials(tenant_id, client_id, client_secret, certificate_path)
            else:
                self.load_from_keyring(identity)

        def set_credentials(self, tenant_id, client_id, client_secret, certificate_path):
            self.tenant_id = tenant_id
            self.client_id = client_id
            self.client_secret = client_secret
            self.certificate_path = certificate_path
            self.load_subscriptions()

        def load_from_keyring(self, identity):
            identities = keyring.get_password("Azure", "identities")
            if not identities:
                QMessageBox.information(self, "No Identities Available", "There are no saved identities available.")
                return

            if not identity:
                identity = self.select_identity(identities)
                if not identity:
                    return

            self.current_identity = identity
            self.tenant_id = keyring.get_password("Azure", f"{self.current_identity}_tenant_id")
            self.client_id = keyring.get_password("Azure", f"{self.current_identity}_client_id")
            self.client_secret = keyring.get_password("Azure", f"{self.current_identity}_client_secret")
            self.certificate_path = keyring.get_password("Azure", f"{self.current_identity}_certificate_path")

            if self.tenant_id and self.client_id and (self.client_secret or self.certificate_path):
                self.authenticate_and_load_subscriptions()
            else:
                QMessageBox.information(self, "No Identities Available", "There are no saved identities available.")

        def select_identity(self, identities):
            identities = identities.split(',')
            dialog = self.create_dialog(identities)
            result = dialog.exec_()

            if result == QDialog.Accepted:
                return self.comboBox.currentText()

        def create_dialog(self, identities):
            dialog = QDialog()
            layout = QVBoxLayout()

            self.comboBox = QComboBox()
            self.comboBox.addItems(identities)
            layout.addWidget(self.comboBox)

            delete_button = QPushButton('Delete', self)
            delete_button.clicked.connect(lambda: self.delete_identity(self.comboBox.currentText()))
            layout.addWidget(delete_button)

            ok_button = QPushButton('OK', self)
            ok_button.clicked.connect(dialog.accept)
            layout.addWidget(ok_button)

            dialog.setLayout(layout)
            return dialog

        def authenticate_and_load_subscriptions(self):
            try:
                _, subscription_client = authenticate_to_azure(self.tenant_id, self.client_id, self.client_secret, self.certificate_path)
                self.subscriptions = get_subscriptions(subscription_client, None)
            except Exception as _:
                QMessageBox.critical(self, "Invalid Credential selection", "The provided credentials are not valid.")
                return

            self.listWidget.clear()
            for id, name in self.subscriptions:
                item = QListWidgetItem(f"{name} ({id})")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.listWidget.addItem(item)

            self.label.setText(f"Selected Profile: {self.current_identity}")

        def toggle_advanced_options(self):
            if self.scrollArea.isHidden():
                self.scrollArea.show()
            else:
                self.scrollArea.hide()

        def browse_for_certificate(self, certificate_path_input):
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                    "All Files (*);;Python Files (*.py)", options=options)
            if file_name:
                certificate_path_input.setText(file_name)

        def browse_for_folder(self, output_folder_input):
            folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            if folder:  # If a folder is selected
                if os.path.exists(folder):  # Check if the directory exists
                    output_folder_input.setText(folder)
                else:
                    QMessageBox.critical(self, "Invalid Directory", "The selected directory does not exist.")
            else:
                print("No folder selected.")

        def delete_identity(self, identity):
            if identity:
                reply = QMessageBox.question(self, 'Delete Identity',
                                            f"Are you sure you want to delete the identity '{identity}'?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    # Check if passwords exist before deleting
                    if keyring.get_password("Azure", f"{identity}_tenant_id"):
                        keyring.delete_password("Azure", f"{identity}_tenant_id")
                    if keyring.get_password("Azure", f"{identity}_client_id"):
                        keyring.delete_password("Azure", f"{identity}_client_id")
                    if keyring.get_password("Azure", f"{identity}_client_secret"):
                        keyring.delete_password("Azure", f"{identity}_client_secret")

                    identities = keyring.get_password("Azure", "identities").split(',')
                    identities.remove(identity)
                    keyring.set_password("Azure", "identities", ','.join(identities))

                    self.current_identity = None
                    self.tenant_id = None
                    self.client_id = None
                    self.client_secret = None

                    self.label.setText("Please choose an identity or create a new one")
                    self.listWidget.clear()

                    # Refresh the list of identities in the combo box
                    self.comboBox.clear()  # Change here
                    self.comboBox.addItems(identities)  # And here
                
        def on_item_changed(self, item):
            if item.checkState() == Qt.Checked:
                self.selected_subscription_id = item.text().split(' ')[-1].strip('()')
                print(f"Selected subscription ID: {self.selected_subscription_id}")
                for i in range(self.listWidget.count()):
                    other_item = self.listWidget.item(i)
                    if other_item != item:
                        other_item.setCheckState(Qt.Unchecked)

        def run_main_py(self):
            if self.selected_subscription_id and self.tenant_id and self.client_id and (self.client_secret or self.certificate_path):
                self.setup_process()
                args = self.prepare_args()
                self.start_and_wait_for_process(args)
                self.ask_to_open_output_folder()

        def setup_process(self):
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.read_output)
            self.process.errorOccurred.connect(self.handle_error)

        def prepare_args(self):
            # Get the directory of the current script (or executable)
            dir_path = os.path.dirname(os.path.abspath(__file__))
            # Prepare the arguments for main.py
            args = [os.path.join(dir_path, 'main.py'), 
                    '--subscription_id', self.selected_subscription_id,
                    '--tenant_id', self.tenant_id,
                    '--client_id', self.client_id]
            self.add_advanced_options(args)
            return args

        def add_advanced_options(self, args):
            # Add the advanced options to the arguments if they are not empty
            if self.certificate_path:  # Check if a certificate path is available
                print(self.certificate_path)
                args.extend(['--certificate_path', self.certificate_path])
            elif self.client_secret:  # Otherwise, check if a client secret is available
                args.extend(['--client_secret', self.client_secret])
            self.extend_args_if_text(args, '--resource_group', self.resourceGroupNameInput)
            self.extend_args_if_text(args, '--rgtag_key', self.resourceGroupTagKeyInput)
            self.extend_args_if_text(args, '--rgtag_value', self.resourceGroupTagValueInput)
            self.extend_args_if_text(args, '--rtag_key', self.resourceTagKeyInput)
            self.extend_args_if_text(args, '--rtag_value', self.resourceTagValueInput)
            self.extend_args_if_text(args, '--output_folder', self.output_folder_input)
            if self.outputExcelCheckbox.isChecked():
                args.append('--output_xlsx')
            if self.outputDrawIOCheckbox.isChecked():
                args.append('--output_drawio')
            if self.outputDocxCheckbox.isChecked():
                args.append('--output_docx')
            if self.outputHtmlCheckbox.isChecked():
                args.append('--output_mermaid')

        def start_and_wait_for_process(self, args):
            # Start the process with the prepared arguments
            self.process.start(sys.executable, ['-u'] + args)
            # Wait for the process to finish
            self.process.waitForFinished()

        def ask_to_open_output_folder(self):
            # Ask the user if they want to open the output folder
            reply = QMessageBox.question(self, 'Open Output Folder',
                                        'Do you want to open the output folder?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Open the output folder
                if platform.system() == "Windows":
                    os.startfile(self.output_folder_input.text())
                elif platform.system() == "Darwin":
                    subprocess.call(('open', self.output_folder_input.text()))
                else:
                    subprocess.call(('xdg-open', self.output_folder_input.text()))

        def extend_args_if_text(self, args, arg_name, input_field):
            if input_field.text():
                args.extend([arg_name, input_field.text()])

        def read_output(self):
            output = bytes(self.process.readAllStandardOutput()).decode()
            error = bytes(self.process.readAllStandardError()).decode()

            if output:
                self.outputTextEdit.append(output)
            if error:
                self.outputTextEdit.append(error)

        def showDialog(self):
            dialog = QDialog()
            dialog.setWindowTitle('Input Dialog')
            form = QFormLayout(dialog)
            identity_name_input = QLineEdit(dialog)
            tenant_id_input = QLineEdit(dialog)
            client_id_input = QLineEdit(dialog)
            form.addRow('Enter Identity Name:', identity_name_input)
            form.addRow('Enter Tenant ID:', tenant_id_input)
            form.addRow('Enter Client ID:', client_id_input)
            form.addRow('Enter Client Secret:', self.clientSecretInput)
            form.addRow(self.useCertificateCheckbox)
            form.addRow('Certificate Path:', self.certificatePathInput)
            form.addRow(self.browseCertificateButton)

            save_button = QPushButton('Save', dialog)
            dontsave_button = QPushButton("Don't Save", dialog)
            save_button.clicked.connect(lambda: self.save_credentials(identity_name_input.text(), tenant_id_input.text(), client_id_input.text(), dialog))
            dontsave_button.clicked.connect(lambda: self.dont_save_credentials(identity_name_input.text(), tenant_id_input.text(), client_id_input.text(), dialog))

            form.addRow(save_button, dontsave_button)

            dialog.exec_()

        def load_subscriptions(self):
            try:
                _, subscription_client = authenticate_to_azure(self.tenant_id, self.client_id, self.client_secret, self.certificate_path)
                self.subscriptions = get_subscriptions(subscription_client, None)
            except Exception as _:
                QMessageBox.critical(self, "Invalid Credentials", "The provided credentials are invalid.")
                return

            self.listWidget.clear()
            for id, name in self.subscriptions:
                item = QListWidgetItem(f"{name} ({id})")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.listWidget.addItem(item)

            self.label.setText(f"Selected Profile: {self.current_identity}")

        def save_credentials(self, identity_name, tenant_id, client_id, dialog):
            if self.useCertificateCheckbox.isChecked():
                self.certificate_path = self.certificatePathInput.text()
                self.client_secret = None
            else:
                self.certificate_path = None
                self.client_secret = self.clientSecretInput.text()

            self.tenant_id = tenant_id
            self.client_id = client_id

            try:
                _, subscription_client = authenticate_to_azure(tenant_id, client_id, self.client_secret, self.certificate_path)
                self.subscriptions = get_subscriptions(subscription_client, None)

                # Check if the identity name is already in use
                identities = keyring.get_password("Azure", "identities")
                if identities and identity_name in identities.split(','):
                    QMessageBox.critical(self, "Identity Name In Use", "Please choose a different identity name.")
                    return

                keyring.set_password("Azure", f"{identity_name}_tenant_id", self.tenant_id)
                keyring.set_password("Azure", f"{identity_name}_client_id", self.client_id)
                if self.certificate_path:
                    keyring.set_password("Azure", f"{identity_name}_certificate_path", self.certificate_path)
                else:
                    keyring.set_password("Azure", f"{identity_name}_client_secret", self.client_secret)

                if identities:
                    identities = identities.split(',')
                    identities.append(identity_name)
                else:
                    identities = [identity_name]
                keyring.set_password("Azure", "identities", ','.join(identities))

                # Verify that the credentials were saved correctly
                if all([keyring.get_password("Azure", f"{identity_name}_tenant_id"),
                        keyring.get_password("Azure", f"{identity_name}_client_id"),
                        keyring.get_password("Azure", f"{identity_name}_certificate_path" if self.certificate_path else f"{identity_name}_client_secret")]):
                    self.current_identity = identity_name
                    self.load_identity(self.current_identity)
                    dialog.accept()
                else:
                    QMessageBox.critical(self, "Save Failed", "Failed to save the credentials.")
                    return

            except Exception as _:
                QMessageBox.critical(self, "Invalid Credentials", "The provided credentials are invalid.")

        def dont_save_credentials(self, identity_name, tenant_id, client_id, dialog):
            if self.useCertificateCheckbox.isChecked():
                self.certificate_path = self.certificatePathInput.text()
                self.client_secret = None
            else:
                self.certificate_path = None
                self.client_secret = self.clientSecretInput.text()

            self.tenant_id = tenant_id
            self.client_id = client_id

            # Check if any field is empty
            if not any([not identity_name.strip(), not tenant_id.strip(), not client_id.strip()]):
                if self.certificate_path and not self.certificate_path.strip():
                    QMessageBox.critical(self, "Invalid Certificate Path", "The provided certificate path is invalid.")
                    return
                elif self.client_secret and not self.client_secret.strip():
                    QMessageBox.critical(self, "Invalid Client Secret", "The provided client secret is invalid.")
                    return
                else:
                    self.current_identity = identity_name
                    self.load_subscriptions()  # Call load_subscriptions here
            else:
                self.current_identity = "Unsaved Identity"
                            
            dialog.accept()

    if __name__ == '__main__':
        app = QApplication([])
        ex = AzureAuthApp()
        ex.show()
        app.exec_()

except Exception as e:
    with open('error_log.txt', 'w') as f:
        f.write(str(e))
