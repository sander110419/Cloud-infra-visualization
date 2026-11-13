from urllib.parse import quote

from azure_func.icons import describe
from azure_func.inventory import Inventory


def _escape(text):
    """Escape text for a quoted mermaid label (mermaid uses #name; entity codes)."""
    text = str(text).replace('#', '#35;').replace('&', '#amp;')
    return text.replace('<', '#lt;').replace('>', '#gt;').replace('"', '#quot;')


def _icon_html(icon_stem, width):
    return f"<img src='./icons/{quote(icon_stem)}.svg' width='{width}'/><br>"


def generate_mermaid_flowchart(data):
    """Subscription -> resource group -> resource -> child resource flowchart."""
    inventory = Inventory(data)
    mermaid_code = ["graph LR;"]  # Using Left to Right layout
    node_ids = {}

    by_group = {}
    for node in inventory.nodes.values():
        by_group.setdefault((node.subscription_id, node.resource_group), []).append(node)

    for sub_index, (subscription_id, subscription_data) in enumerate((data.get('Objects') or {}).items(), start=1):
        sub_id = f"sub{sub_index}"
        sub_name = _escape(inventory.subscription_name(subscription_id))
        sub_label = f"{_icon_html('Subscriptions', 24)}<b>Subscription:</b><br>{sub_name}"
        if sub_name != _escape(subscription_id):
            sub_label += f"<br>{_escape(subscription_id)}"
        mermaid_code.append(f'{sub_id}["{sub_label}"]')

        for rg_index, rg_name in enumerate(subscription_data, start=1):
            rg_id = f"{sub_id}_rg{rg_index}"
            mermaid_code.append(f'{rg_id}["{_icon_html("Resource-Groups", 32)}<b>Resource Group:</b><br>{_escape(rg_name)}"]')
            mermaid_code.append(f"{sub_id} --> {rg_id}")

            nodes = sorted(by_group.get((subscription_id, rg_name), []), key=lambda n: (n.type_lower, n.name.lower()))
            for node in nodes:
                node_ids[node.key] = f"{rg_id}_n{len(node_ids) + 1}"
            for node in nodes:
                sku = node.detail.get('sku')
                icon_stem, type_name = describe(node.type, node.kind, sku.get('name', '') if isinstance(sku, dict) else '')
                name = node.name.rsplit('/', 1)[-1]
                label = f"{_icon_html(icon_stem, 48)}<b>{_escape(type_name)}:</b><br>{_escape(name)}"
                mermaid_code.append(f'{node_ids[node.key]}["{label}"]')
                # Child resources hang off their parent, everything else off the resource group
                parent_id = node_ids.get(node.parent.key) if node.parent is not None else None
                mermaid_code.append(f"{parent_id or rg_id} --> {node_ids[node.key]}")

    return "\n".join(mermaid_code)


def generate_html(mermaid_code):
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud Infrastructure Visualization</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            #container {{
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                position: relative;
            }}
            #mermaid {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform-origin: center center;
            }}
        </style>
    </head>
    <body>
        <div id="container">
            <div id="mermaid">
                <pre class="mermaid">
{mermaid_code}
                </pre>
            </div>
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                maxTextSize : 99999999,
                securityLevel: 'loose',
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }}
            }});

            // Zooming and Panning Functionality
            (function() {{
                const container = document.getElementById('container');
                const mermaidDiv = document.getElementById('mermaid');
                let scale = 1;
                let translateX = 0;
                let translateY = 0;
                const zoomSensitivity = 0.01;

                function updateTransform() {{
                    mermaidDiv.style.transform = `translate(-50%, -50%) translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
                }}

                container.addEventListener('wheel', function(e) {{
                    e.preventDefault();
                    const delta = e.deltaY * zoomSensitivity;
                    const newScale = scale - delta;

                    // Keep the scale within reasonable bounds
                    if (newScale > 0.001 && newScale < 100) {{
                        scale = newScale;
                        updateTransform();
                    }}
                }});

                let isDragging = false;
                let startX = 0;
                let startY = 0;

                container.addEventListener('mousedown', function(e) {{
                    isDragging = true;
                    startX = e.clientX - translateX;
                    startY = e.clientY - translateY;
                    container.style.cursor = 'grabbing';
                }});

                container.addEventListener('mousemove', function(e) {{
                    if (!isDragging) return;
                    translateX = e.clientX - startX;
                    translateY = e.clientY - startY;
                    updateTransform();
                }});

                container.addEventListener('mouseup', function(e) {{
                    isDragging = false;
                    container.style.cursor = 'default';
                }});

                container.addEventListener('mouseleave', function(e) {{
                    isDragging = false;
                    container.style.cursor = 'default';
                }});
            }})();
        </script>
    </body>
    </html>
    '''
    return html_template.format(mermaid_code=mermaid_code)
