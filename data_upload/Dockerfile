FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
COPY geovigil_logo.png .
RUN pip3 install -r requirements.txt

COPY extract.py .

CMD ["extract.lambda_handler"]