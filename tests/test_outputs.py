"""Excel, Word, HTML outputs and the command line."""
import json
import os

import pytest
from docx import Document
from openpyxl import load_workbook

import main
from json2docx import generate_word_document
from json2mermaid import generate_html, generate_mermaid_flowchart
from output_xlsx import output_to_excel, sheet_title
from tests.fake_azure import SUB_DEV, FakeCredential


@pytest.fixture
def no_azure_environment(monkeypatch):
    for name in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_CLIENT_CERTIFICATE_PATH",
                 "AZURE_ARM_ENDPOINT"):
        monkeypatch.delenv(name, raising=False)


# ---- Excel ------------------------------------------------------------------
def test_excel(sample, tmp_path):
    output_to_excel(sample, str(tmp_path))
    workbook = load_workbook(tmp_path / "output.xlsx")
    names = workbook.sheetnames
    assert names[0] == "Index" and names[-2:] == ["Recommendations", "All Resources"]
    assert "Compute - Virtualmachines" in names and "Quantum - Workspaces" in names
    assert all(len(name) <= 31 for name in names) and len(set(map(str.lower, names))) == len(names)

    machines = workbook["Compute - Virtualmachines"]
    assert machines["A1"].value == "Index"
    header = [cell.value for cell in machines[2]]
    assert header[:5] == ["subscription_id", "resource_group", "type", "id", "name"]
    assert "properties.hardwareProfile.vmSize" in header and "tags.role" in header
    assert header.index("tags.role") > header.index("properties.hardwareProfile.vmSize")
    assert machines.max_row == 2 + 4, "four virtual machines"

    # The union of all columns is used, not just those of the first resource of a type
    disks = workbook["Compute - Disks"]
    disk_header = [cell.value for cell in disks[2]]
    assert "properties.osType" in disk_header

    # Visio expects a plain table with the header in the first row
    everything = workbook["All Resources"]
    assert [cell.value for cell in everything[1]] == ["subscription_id", "resource_group", "type", "id", "name",
                                                       "VisioShape"]
    total = sum(len(group) for groups in sample["Objects"].values() for group in groups.values())
    assert everything.max_row == 1 + total
    shapes = {row[5].value for row in everything.iter_rows(min_row=2)}
    assert "compute_virtualmachines" in shapes

    recommendations = workbook["Recommendations"]
    assert recommendations.max_row == 2 + 5
    index = {row[0].value: row[2].value for row in workbook["Index"].iter_rows(min_row=2)}
    assert index["Compute - Virtualmachines"] == 4 and index["All Resources"] == total


def test_sheet_titles_are_valid_and_unique():
    used = set()
    first = sheet_title("Microsoft.Storage/storageAccounts/blobServices/containers", used)
    second = sheet_title("Microsoft.Storage/storageAccounts/blobServicesOther/x", used)
    assert len(first) <= 31 and len(second) <= 31 and first.lower() != second.lower()
    assert sheet_title("Odd/[type]:*?", used).count("[") == 0


# ---- Word -------------------------------------------------------------------
def test_word(sample, tmp_path):
    small = {**sample, "Objects": {SUB_DEV: sample["Objects"][SUB_DEV]}}
    generate_word_document(small, str(tmp_path))
    document = Document(str(tmp_path / "output.docx"))
    subscriptions = document.tables[0]
    assert subscriptions.rows[1].cells[1].text == "Contoso Dev/Test"
    groups = {row.cells[1].text for row in document.tables[1].rows[1:]}
    assert groups == {"rg-dev", "NetworkWatcherRG"}
    headings = [p.text for p in document.paragraphs if p.style.name.startswith("Heading")]
    assert "Resource Group: rg-dev" in headings
    assert any(heading.endswith("- vm-dev-01") for heading in headings)


# ---- HTML / mermaid ---------------------------------------------------------
def test_mermaid(sample):
    code = generate_mermaid_flowchart(sample)
    lines = code.splitlines()
    assert lines[0] == "graph LR;"
    definitions = [line.split("[", 1)[0] for line in lines if '["' in line]
    assert len(definitions) == len(set(definitions)), "node ids are unique"
    total = sum(len(group) for groups in sample["Objects"].values() for group in groups.values())
    groups = sum(len(groups) for groups in sample["Objects"].values())
    assert len(definitions) == total + groups + len(sample["Objects"])
    for line in lines[1:]:
        if '["' in line:
            label = line.split('["', 1)[1].rsplit('"]', 1)[0]
            assert '"' not in label, line
    assert "./icons/Virtual-Machine.svg" in code and "Contoso Dev/Test" in code
    html = generate_html(code)
    assert "mermaid" in html and "graph LR;" in html


# ---- command line -----------------------------------------------------------
def test_outputs_from_existing_json(sample, tmp_path, no_azure_environment):
    source = tmp_path / "inventory.json"
    source.write_text(json.dumps(sample), encoding="utf-8")
    out = tmp_path / "out"
    code = main.generate_output(["--input_json", str(source), "--output_folder", str(out), "--output_xlsx",
                                 "--output_drawio", "--output_docx", "--output_mermaid",
                                 "--drawio_icons", "library"])
    assert code == 0
    for name in ("output.xlsx", "output.drawio", "output.docx", "output.html"):
        assert (out / name).stat().st_size > 1000, name
    assert (out / "icons" / "Virtual-Machine.svg").exists()
    assert "img/lib/azure2/" in (out / "output.drawio").read_text(encoding="utf-8")


def test_full_run_against_fake_azure(fake_azure, tmp_path, monkeypatch, capsys, no_azure_environment):
    monkeypatch.setattr(main, "build_credential", lambda *args, **kwargs: FakeCredential())
    out = tmp_path / "out"
    code = main.generate_output(["--arm_endpoint", fake_azure.endpoint, "--subscription_id", SUB_DEV,
                                 "--output_folder", str(out), "--output_drawio", "--output_xlsx"])
    assert code == 0
    data = json.loads((out / "output.json").read_text(encoding="utf-8"))
    assert list(data["Objects"]) == [SUB_DEV]
    assert (out / "output.drawio").exists() and (out / "output.xlsx").exists()
    printed = capsys.readouterr().out
    assert "Contoso Dev/Test" in printed and "output.drawio" in printed


def test_missing_credentials_is_a_clean_error(tmp_path, capsys, no_azure_environment):
    code = main.generate_output(["--output_folder", str(tmp_path)])
    assert code == 1
    assert "No way to log in" in capsys.readouterr().out
    assert not os.path.exists(tmp_path / "output.json")


def test_arguments(no_azure_environment, monkeypatch):
    from functions import parse_arguments
    args = parse_arguments(["--subscription_id", "a, b", "--subscription_id", "c", "--output_mermaid"])
    assert args.subscription_ids == ["a", "b", "c"] and args.output_html is True
    assert args.engine == "auto" and args.drawio_icons == "embedded"
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "from-env")
    assert parse_arguments([]).client_secret == "from-env"
