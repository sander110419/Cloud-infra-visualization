def get_resource_name(details):
    if isinstance(details, dict):
        return str(details.get('name', 'Unknown'))
    elif isinstance(details, list) and details:
        # If Details is a list, try to get name from first item
        if isinstance(details[0], dict):
            return str(details[0].get('name', 'Unknown'))
    return 'Unknown'

def generate_mermaid_flowchart(data):
    mermaid_code = ["graph LR;"]
    
    for subscription_id, subscription_data in data['Objects'].items():
        sub_id = f"sub_{subscription_id.replace('-', '_').replace(' ', '_')}"
        mermaid_code.append(f"{sub_id}[Subscription: {subscription_id}]")
        
        for rg_name, resources in subscription_data.items():
            rg_id = f"rg_{rg_name.replace('-', '_').replace(' ', '_')}"
            mermaid_code.append(f"{rg_id}[RG: {rg_name}]")
            mermaid_code.append(f"{sub_id} --> {rg_id}")
            
            for resource in resources:
                # Get resource name using the new helper function
                resource_name = get_resource_name(resource['Details'])
                resource_id = f"res_{resource_name.replace('-', '_').replace(' ', '_')}"
                resource_type = resource['ResourceType'].split('/')[-1]
                mermaid_code.append(f"{resource_id}[{resource_type}: {resource_name}]")
                mermaid_code.append(f"{rg_id} --> {resource_id}")
    
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
                const zoomSensitivity = 0.001;

                function updateTransform() {{
                    mermaidDiv.style.transform = `translate(-50%, -50%) translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
                }}

                container.addEventListener('wheel', function(e) {{
                    e.preventDefault();
                    const delta = e.deltaY * zoomSensitivity;
                    const newScale = scale - delta;

                    // Keep the scale within reasonable bounds
                    if (newScale > 0.001 && newScale < 10) {{
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
