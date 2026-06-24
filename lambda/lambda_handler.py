from app.client import run_scraper


def handler(event, context):
    output_path = "/tmp/invoice.pdf"
    run_scraper(output_path)

    return {
        "status": "success",
        "invoice_path": output_path,
    }
