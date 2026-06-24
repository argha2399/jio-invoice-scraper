import logging

from scrape.scraper import InvoiceScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_scraper(output_path: str = "invoice.pdf") -> str:
    logger.info("Starting Jio invoice scraper")

    with InvoiceScraper() as scraper:
        scraper.request_otp()
        scraper.extract_otp()
        scraper.submit_otp()
        pdf = scraper.download_invoice()

    with open(output_path, "wb") as f:
        f.write(pdf.content)

    logger.info("Invoice written to %s", output_path)
    return output_path


if __name__ == "__main__":
    run_scraper("invoice.pdf")
