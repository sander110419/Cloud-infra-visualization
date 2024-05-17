from PyQt5.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout, QPushButton, QDialog, QLineEdit, QFormLayout, QListWidgetItem, QDialogButtonBox, QListWidget, QCheckBox, QLabel
from PyQt5.QtCore import Qt, QProcess
from functions import authenticate_to_azure, get_subscriptions
import sys

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

            self.initUI()

        def handle_error(self, error):
            self.outputTextEdit.append(f"An error occurred while running main.py: {error}")

        def initUI(self):
            layout = QVBoxLayout()

            self.label = QLabel("Please enter Tenant ID, Client ID and Secret")
            layout.addWidget(self.label)

            btn = QPushButton('Enter Details', self)
            btn.clicked.connect(self.showDialog)
            layout.addWidget(btn)

            self.listWidget = QListWidget()
            layout.addWidget(self.listWidget)
            self.listWidget.itemChanged.connect(self.on_item_changed)

            # Add a button to start main.py
            self.runButton = QPushButton('Run main.py', self)
            self.runButton.clicked.connect(self.run_main_py)
            layout.addWidget(self.runButton)

            # Add a QTextEdit widget to display the output of main.py
            self.outputTextEdit = QTextEdit()
            #self.outputTextEdit.setReadOnly(True)
            layout.addWidget(self.outputTextEdit)

            self.setLayout(layout)

        def on_item_changed(self, item):
            if item.checkState() == Qt.Checked:
                # Extract the subscription ID from the item text
                self.selected_subscription_id = item.text().split(' ')[-1].strip('()')
                print(f"Selected subscription ID: {self.selected_subscription_id}")

                # Uncheck all other items
                for i in range(self.listWidget.count()):
                    other_item = self.listWidget.item(i)
                    if other_item != item:
                        other_item.setCheckState(Qt.Unchecked)

        def run_main_py(self):
            if self.selected_subscription_id and self.tenant_id and self.client_id and self.client_secret:
                # Create a QProcess object
                self.process = QProcess()

                # Connect the readyReadStandardOutput signal to a slot function that reads the output
                self.process.readyReadStandardOutput.connect(self.read_output)
                self.process.errorOccurred.connect(self.handle_error)
                # Start main.py with the selected subscription, tenant ID, client ID, and client secret as parameters
                self.process.start(sys.executable, ['-u','main.py', 
                                                    '--subscription_id', self.selected_subscription_id,
                                                    '--tenant_id', self.tenant_id,
                                                    '--client_id', self.client_id,
                                                    '--client_secret', self.client_secret,
                                                    '--resource_group', 'rg-p-app-10007729',
                                                    '--output_xlsx'])
                self.process.errorOccurred.connect(self.handle_error)
        
        def handle_error(self, error):
            self.outputTextEdit.append(f"An error occurred while running main.py: {error}")


        def read_output(self):
            # Read the standard output of the process
            output = bytes(self.process.readAllStandardOutput()).decode()
            error = bytes(self.process.readAllStandardError()).decode()

            # Append the output to the QTextEdit widget
            if output:
                self.outputTextEdit.append(output)
            if error:
                self.outputTextEdit.append(error)

        def showDialog(self):
            dialog = QDialog()
            dialog.setWindowTitle('Input Dialog')
            form = QFormLayout(dialog)
            tenant_id_input = QLineEdit(dialog)
            client_id_input = QLineEdit(dialog)
            client_secret_input = QLineEdit(dialog)
            form.addRow('Enter Tenant ID:', tenant_id_input)
            form.addRow('Enter Client ID:', client_id_input)
            form.addRow('Enter Client Secret:', client_secret_input)

            # Add OK and Cancel buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            form.addRow(buttons)

            ok = dialog.exec_()
            if ok:
                self.tenant_id = tenant_id_input.text()
                self.client_id = client_id_input.text()
                self.client_secret = client_secret_input.text()

            # Authenticate to Azure and get subscriptions
            credential, subscription_client = authenticate_to_azure(self.tenant_id, self.client_id, self.client_secret)
            self.subscriptions = get_subscriptions(subscription_client, None)

            # Update the list widget with the subscriptions
            self.listWidget.clear()
            for id, name in self.subscriptions:
                item = QListWidgetItem(f"{name} ({id})")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.listWidget.addItem(item)


    if __name__ == '__main__':
        app = QApplication([])
        ex = AzureAuthApp()
        ex.show()
        app.exec_()

except Exception as e:
    with open('error_log.txt', 'w') as f:
        f.write(str(e))