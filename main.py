import json
import logging
import os
import shutil
import sys

from azure_func.arm import ArmClient, ArmError
from azure_func.collector import Collector, CollectorOptions
from azure_func.icons import icon_dir
from functions import build_credential, parse_arguments, set_up_logging
from json2docx import generate_word_document
from json2drawio import generate_drawio
from json2mermaid import generate_html, generate_mermaid_flowchart
from output_xlsx import output_to_excel

OUTPUT_JSON = 'output.json'


def collect(args):
    """Query Azure and return the inventory document."""
    credential = build_credential(args.tenant_id, args.client_id, args.client_secret, args.certificate_path,
                                  args.use_device_code, args.interactive_login, args.user_login, args.use_cli)
    arm = ArmClient(credential, args.arm_endpoint)
    options = CollectorOptions(
        engine=args.engine,
        resource_group=args.resource_group,
        rgtag_key=args.rgtag_key, rgtag_value=args.rgtag_value,
        rtag_key=args.rtag_key, rtag_value=args.rtag_value,
        include_children=not args.skip_children,
        include_advisor=not args.skip_advisor,
        workers=args.workers,
    )
    try:
        return Collector(arm, options, progress=_progress).collect(args.subscription_ids)
    finally:
        arm.close()


def _progress(message):
    print(message, flush=True)


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, default=str)


def write_html(data, output_folder):
    html_content = generate_html(generate_mermaid_flowchart(data))
    with open(os.path.join(output_folder, 'output.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    # The HTML refers to ./icons/<name>.svg
    icons_destination = os.path.join(output_folder, 'icons')
    if os.path.exists(icon_dir()):
        if os.path.exists(icons_destination):
            shutil.rmtree(icons_destination)
        shutil.copytree(icon_dir(), icons_destination)


def write_drawio(data, args, output_folder):
    path = generate_drawio(data, os.path.join(output_folder, 'output.drawio'), icons=args.drawio_icons)
    size_mb = os.path.getsize(path) / 1_000_000
    if size_mb > 10 and args.drawio_icons == 'embedded':
        print(f"Tip: output.drawio is {size_mb:.0f} MB. --drawio_icons library makes it less than half that size.",
              flush=True)


def write_outputs(data, args, output_folder):
    """Write every requested output. Returns the names of the outputs that failed."""
    writers = []
    if args.output_xlsx:
        writers.append(('Excel', 'output.xlsx', lambda: output_to_excel(data, output_folder)))
    if args.output_drawio:
        writers.append(('draw.io', 'output.drawio', lambda: write_drawio(data, args, output_folder)))
    if args.output_docx:
        writers.append(('Word', 'output.docx', lambda: generate_word_document(data, output_folder)))
    if args.output_html:
        writers.append(('HTML', 'output.html', lambda: write_html(data, output_folder)))

    failed = []
    for name, filename, writer in writers:
        try:
            writer()
            print(f"Wrote {os.path.join(output_folder, filename)}", flush=True)
        except Exception as e:  # one broken output should not cost you the others
            logging.exception("Error writing %s output", name)
            print(f"ERROR: could not write the {name} output: {e}", flush=True)
            failed.append(name)
    return failed


def generate_output(argv=None):
    args = parse_arguments(argv)
    set_up_logging(args.log_level)

    output_folder = args.output_folder if args.output_folder else os.path.join('.', 'output')
    os.makedirs(output_folder, exist_ok=True)

    if args.input_json:
        try:
            data = read_json(args.input_json)
        except (OSError, ValueError) as e:
            print(f"ERROR: could not read {args.input_json}: {e}")
            return 1
    else:
        try:
            data = collect(args)
        except (ValueError, ArmError) as e:
            logging.error("Collection failed: %s", e)
            print(f"ERROR: {e}")
            return 1
        except Exception as e:  # e.g. azure.identity authentication errors
            logging.exception("Collection failed")
            print(f"ERROR: {e}")
            return 1
        json_path = os.path.join(output_folder, OUTPUT_JSON)
        write_json(data, json_path)
        print(f"Wrote {json_path}", flush=True)

    failed = write_outputs(data, args, output_folder)
    subscription_errors = [info for info in (data.get('Subscriptions') or {}).values() if info.get('Error')]
    return 1 if failed or subscription_errors else 0


if __name__ == "__main__":
    sys.exit(generate_output())
