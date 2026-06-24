# Jio Invoice Scraper

This repository contains a scraper for Jio invoices packaged as a Lambda container image.

## Shared scraper logic

The `run_scraper()` function in [app/client.py](app/client.py) centralizes the scraper execution:

1. request an OTP via Jio login API
2. read the OTP from S3
3. submit the OTP
4. download the invoice PDF
5. write the invoice to a specified output path

Both entrypoints call this function:

- **CLI**: `python app/client.py` writes invoice to `invoice.pdf`
- **Lambda**: `lambda.lambda_handler.handler` writes invoice to `/tmp/invoice.pdf`

## Docker image

Build the Lambda-compatible container image locally:

```bash
docker build -t jio-scraper-lambda .
```

Push the image to Amazon ECR and create a Lambda function from the container image.

## Lambda handler

The Lambda entrypoint is `lambda/lambda_handler.py`, with the handler:

```python
lambda.lambda_handler.handler
```

## Notes

- Lambda container images must be built and pushed to ECR.
- The function uses the Lambda runtime, so execution is limited by Lambda timeout settings (up to 15 minutes).
- If you want to persist the downloaded invoice, add code to upload the PDF to S3 from within the handler.

