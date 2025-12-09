from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parent / ".." / "data" / "context_template.jsonld"

def create_custom_vc_context_from_template(endpoint_base_url: str):
    context_template = TEMPLATE_PATH.read_text()
    context = context_template.replace("ENDPOINT_BASE_URL", endpoint_base_url)

    return context