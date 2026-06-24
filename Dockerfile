
FROM public.ecr.aws/lambda/python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /var/task

# Install build tools and pipenv
RUN python -m pip install --upgrade pip setuptools wheel pipenv

# Copy dependency declarations and install in the Lambda image
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system --ignore-pipfile

# Copy application code
COPY . .

# Use the Lambda handler entry point
CMD ["lambda.lambda_handler.handler"]
