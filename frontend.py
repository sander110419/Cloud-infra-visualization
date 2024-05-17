from PyQt5.QtWidgets import QApplication, QFileDialog, QScrollArea, QComboBox, QTextEdit, QWidget, QVBoxLayout, QPushButton, QDialog, QLineEdit, QFormLayout, QListWidgetItem, QDialogButtonBox, QListWidget, QCheckBox, QLabel, QRadioButton, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QProcess
from functions import authenticate_to_azure, get_subscriptions
import sys
import keyring

try:
    def get_subscriptions(subscription_client, subscription_id):
        if subscription_id:
            subscriptions = [(subscription_id, subscription.display_name)]
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

            self.advancedLayout.addWidget(self.outputExcelCheckbox)
            self.advancedLayout.addWidget(self.outputDrawIOCheckbox)

            self.resourceGroupNameInput = QLineEdit()
            self.resourceGroupTagKeyInput = QLineEdit()
            self.resourceGroupTagValueInput = QLineEdit()
            self.resourceTagKeyInput = QLineEdit()
            self.resourceTagValueInput = QLineEdit()
            self.outputFolderInput = QLineEdit()
            self.browseButton = QPushButton('Browse')
            self.browseButton.clicked.connect(lambda: self.browse_for_folder(self.outputFolderInput))

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
            self.advancedLayout.addWidget(self.outputFolderInput)
            self.advancedLayout.addWidget(self.browseButton)

            layout.addWidget(self.scrollArea)

            self.runButton = QPushButton('Run main.py', self)
            self.runButton.clicked.connect(self.run_main_py)
            layout.addWidget(self.runButton)

            self.outputTextEdit = QTextEdit()
            layout.addWidget(self.outputTextEdit)

            self.setLayout(layout)

            # Initially hide the advanced options
            self.scrollArea.hide()

        def load_identity(self, identity=None):
            if not identity:
                identities = keyring.get_password("Azure", "identities")
                if identities:
                    identities = identities.split(',')
                    
                    # Create a custom dialog
                    dialog = QDialog()
                    layout = QVBoxLayout()

                    comboBox = QComboBox()
                    comboBox.addItems(identities)
                    layout.addWidget(comboBox)

                    deleteButton = QPushButton('Delete', self)
                    deleteButton.clicked.connect(lambda: self.delete_identity(comboBox.currentText()))
                    layout.addWidget(deleteButton)

                    okButton = QPushButton('OK', self)
                    okButton.clicked.connect(dialog.accept)
                    layout.addWidget(okButton)

                    dialog.setLayout(layout)
                    result = dialog.exec_()

                    if result == QDialog.Accepted:
                        identity = comboBox.currentText()
                        self.current_identity = identity
                else:
                    QMessageBox.information(self, "No Identities Available", "There are no saved identities available.")
                    return

            self.tenant_id = keyring.get_password("Azure", f"{self.current_identity}_tenant_id")
            self.client_id = keyring.get_password("Azure", f"{self.current_identity}_client_id")
            self.client_secret = keyring.get_password("Azure", f"{self.current_identity}_client_secret")

            credential, subscription_client = authenticate_to_azure(self.tenant_id, self.client_id, self.client_secret)
            self.subscriptions = get_subscriptions(subscription_client, None)

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

        def browse_for_folder(self, outputFolderInput):
            folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            outputFolderInput.setText(folder)

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

        def on_item_changed(self, item):
            if item.checkState() == Qt.Checked:
                self.selected_subscription_id = item.text().split(' ')[-1].strip('()')
                print(f"Selected subscription ID: {self.selected_subscription_id}")
                for i in range(self.listWidget.count()):
                    other_item = self.listWidget.item(i)
                    if other_item != item:
                        other_item.setCheckState(Qt.Unchecked)

        def run_main_py(self):
            if self.selected_subscription_id and self.tenant_id and self.client_id and self.client_secret:
                self.process = QProcess()
                self.process.readyReadStandardOutput.connect(self.read_output)
                self.process.errorOccurred.connect(self.handle_error)

                # Prepare the arguments for main.py
                args = ['main.py', 
                        '--subscription_id', self.selected_subscription_id,
                        '--tenant_id', self.tenant_id,
                        '--client_id', self.client_id,
                        '--client_secret', self.client_secret]

                # Add the advanced options to the arguments if they are not empty
                if self.resourceGroupNameInput.text():
                    args.extend(['--resource_group', self.resourceGroupNameInput.text()])
                if self.resourceGroupTagKeyInput.text():
                    args.extend(['--rgtag_key', self.resourceGroupTagKeyInput.text()])
                if self.resourceGroupTagValueInput.text():
                    args.extend(['--rgtag_value', self.resourceGroupTagValueInput.text()])
                if self.resourceTagKeyInput.text():
                    args.extend(['--rtag_key', self.resourceTagKeyInput.text()])
                if self.resourceTagValueInput.text():
                    args.extend(['--rtag_value', self.resourceTagValueInput.text()])
                if self.outputFolderInput.text():
                    args.extend(['--output_folder', self.outputFolderInput.text()])
                if self.outputExcelCheckbox.isChecked():
                    args.append('--output_xlsx')
                if self.outputDrawIOCheckbox.isChecked():
                    args.append('--output_drawio')

                # Start the process with the prepared arguments
                self.process.start(sys.executable, ['-u'] + args)

        def handle_error(self, error):
            self.outputTextEdit.append(f"An error occurred while running main.py: {error}")

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
            client_secret_input = QLineEdit(dialog)
            form.addRow('Enter Identity Name:', identity_name_input)
            form.addRow('Enter Tenant ID:', tenant_id_input)
            form.addRow('Enter Client ID:', client_id_input)
            form.addRow('Enter Client Secret:', client_secret_input)

            saveButton = QPushButton('Save', dialog)
            dontSaveButton = QPushButton("Don't Save", dialog)
            saveButton.clicked.connect(lambda: self.save_credentials(identity_name_input.text(), tenant_id_input.text(), client_id_input.text(), client_secret_input.text(), dialog))
            dontSaveButton.clicked.connect(lambda: self.dont_save_credentials(identity_name_input.text(), tenant_id_input.text(), client_id_input.text(), client_secret_input.text(), dialog))

            form.addRow(saveButton, dontSaveButton)

            dialog.exec_()

        def save_credentials(self, identity_name, tenant_id, client_id, client_secret, dialog):
            self.tenant_id = tenant_id
            self.client_id = client_id
            self.client_secret = client_secret

            keyring.set_password("Azure", f"{identity_name}_tenant_id", self.tenant_id)
            keyring.set_password("Azure", f"{identity_name}_client_id", self.client_id)
            keyring.set_password("Azure", f"{identity_name}_client_secret", self.client_secret)

            identities = keyring.get_password("Azure", "identities")
            if identities:
                identities = identities.split(',')
                identities.append(identity_name)
            else:
                identities = [identity_name]
            keyring.set_password("Azure", "identities", ','.join(identities))

            self.current_identity = identity_name
            self.load_identity(self.current_identity)
            dialog.accept()

        def dont_save_credentials(self, identity_name, tenant_id, client_id, client_secret, dialog):
            self.tenant_id = tenant_id
            self.client_id = client_id
            self.client_secret = client_secret

            # Check if any field is empty
            if not any([not identity_name.strip(), not tenant_id.strip(), not client_id.strip(), not client_secret.strip()]):
                self.current_identity = identity_name
                self.load_identity(self.current_identity)
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
