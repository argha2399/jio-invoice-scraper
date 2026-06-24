from urllib.parse import urljoin
import requests
import re
import json
from tenacity import retry, stop_after_delay, wait_fixed
from utils.aws import S3Client
import logging

logger = logging.getLogger(__name__)


class InvoiceScraper:
    def __enter__(self):
        logger.info("Starting InvoiceScraper")
        return self

    def __init__(self, *args, **kwargs):
        self.session = requests.Session()
        self.mobile_number = "9667136661"
        self.otp = None
        self.s3_client = S3Client(bucket="zoho-android-automation", region="ap-south-1")

    def request_otp(self):
        payload = json.dumps(
            {
                "alternateNumber": "",
                "loginFlowType": "JIOFIBER",
                "mobileNumber": self.mobile_number,
            }
        )
        resp = self.session.post(
            "https://www.jio.com/api/jio-login-service/login/sendOtp",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        logger.info(f"OTP request response: {resp.status_code} - {resp.text}")

    @retry(stop=stop_after_delay(120), wait=wait_fixed(10))
    def extract_otp(self) -> str:
        files = self.s3_client.list_files(prefix="sms/drop")
        logger.info(f"Files: {files}")
        assert files, "Empty file"
        data: dict = json.loads(
            self.s3_client.read_from_s3(path=f"sms/drop/{files[0]}")
        )
        self.otp = re.search(r"\d{6}", data["body"]).group()
        logger.info(f"OTP: {self.otp}")

    def submit_otp(self) -> None:
        assert self.otp, "OTP not set"
        url = "https://www.jio.com/api/jio-login-service/login/validateOtp"
        payload = json.dumps({"otp": self.otp})
        headers = {"Content-Type": "application/json"}
        resp = self.session.post(url, headers=headers, data=payload)
        logger.info(f"OTP submission response: {resp.status_code} - {resp.text}")

    def download_invoice(self) -> bytes:
        url = "https://www.jio.com/api/jio-dashboard-history-service/dashboard-hist/invoice/history?pageNo=0"
        response = self.session.get(url)
        txn_num = response.json()["rechargeHistoryNew"][0]["recharges"][0]["txnNumber"]
        logger.info(f"Transaction Number: {txn_num}")

        pre_req = self.session.get(
            f"https://www.jio.com/api/jio-dashboard-history-service/dashboard-hist/invoice/download/{txn_num}"
        )
        invoice_url = urljoin("https://www.jio.com", pre_req.json()["url"])
        pdf = self.session.get(invoice_url)
        logger.info(f"Invoice downloaded: {pdf.status_code} - {pdf.text}")
        return pdf

    def __exit__(self, exc_type, exc_value, traceback):
        self.s3_client.delete_recursively(prefix="sms/drop")
        self.session.close()
        logger.info("Exiting InvoiceScraper")
