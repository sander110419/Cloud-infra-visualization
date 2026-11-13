"""Smoke tests for the Qt front-end. Skipped when PyQt5 is not installed
(``pip install -r requirements-gui.txt``)."""
import json
import os
import time

import pytest

pytest.importorskip("PyQt5")
pytest.importorskip("keyring")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QProcess, Qt  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

import frontend  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def qt_app():
    yield QApplication.instance() or QApplication([])


@pytest.fixture
def window(qt_app, monkeypatch):
    monkeypatch.setattr(frontend, "authenticate_to_azure", lambda *args, **kwargs: (None, object()))
    monkeypatch.setattr(frontend, "get_subscriptions", lambda *args: [("sub-1", "One"), ("sub-2", "Two (test)")])
    window = frontend.AzureAuthApp()
    window.tenant_id, window.client_id, window.client_secret = "tenant", "client", "s3cret"
    window.load_subscriptions()
    return window


def test_several_subscriptions_can_be_selected(window):
    assert window.listWidget.count() == 2 and window.selected_subscription_ids == []
    window.listWidget.item(0).setCheckState(Qt.Checked)
    window.listWidget.item(1).setCheckState(Qt.Checked)
    assert window.selected_subscription_ids == ["sub-1", "sub-2"]
    window.listWidget.item(0).setCheckState(Qt.Unchecked)
    assert window.selected_subscription_ids == ["sub-2"]


def test_arguments_passed_to_main(window):
    window.listWidget.item(0).setCheckState(Qt.Checked)
    window.listWidget.item(1).setCheckState(Qt.Checked)
    window.outputHtmlCheckbox.setChecked(True)
    window.outputDrawIOCheckbox.setChecked(True)
    window.resourceGroupNameInput.setText("rg-app")
    args = window.prepare_args()
    assert args[:2] == ["-u", os.path.join(ROOT, "main.py")]
    assert args[args.index("--subscription_id") + 1] == "sub-1,sub-2"
    assert args[args.index("--resource_group") + 1] == "rg-app"
    assert "--output_html" in args and "--output_drawio" in args and "--output_xlsx" not in args
    # main.py must accept exactly what the front-end sends
    from functions import parse_arguments
    parsed = parse_arguments(args[2:])
    assert parsed.subscription_ids == ["sub-1", "sub-2"] and parsed.output_html

    # the secret is handed over through the environment, never on the command line
    assert "s3cret" not in args and "--client_secret" not in args
    window.setup_process()
    assert window.process.processEnvironment().value("AZURE_CLIENT_SECRET") == "s3cret"


def test_generation_runs_in_the_background(window, qt_app, sample, tmp_path, monkeypatch):
    source = tmp_path / "inventory.json"
    source.write_text(json.dumps(sample), encoding="utf-8")
    out = tmp_path / "out"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(window, "prepare_args", lambda: [
        "-u", os.path.join(ROOT, "main.py"), "--input_json", str(source), "--output_folder", str(out),
        "--output_drawio"])
    asked = []
    monkeypatch.setattr(window, "ask_to_open_output_folder", lambda: asked.append(True))
    window.listWidget.item(0).setCheckState(Qt.Checked)

    window.run_main_py()
    assert not window.runButton.isEnabled(), "no second run while one is in progress"
    deadline = time.time() + 120
    while window.process.state() != QProcess.NotRunning and time.time() < deadline:
        qt_app.processEvents()
        time.sleep(0.05)
    qt_app.processEvents()

    assert (out / "output.drawio").exists()
    assert asked == [True], "asks to open the folder once the run has really finished"
    assert window.runButton.isEnabled()
    assert "output.drawio" in window.outputTextEdit.toPlainText()
