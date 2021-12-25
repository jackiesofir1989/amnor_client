# first stage
FROM python:3.9.5  AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# second unnamed stage
FROM python:3.9.5-slim
WORKDIR /code

# copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local /root/.local
COPY ./src .

ENV PATH=/root/.local:$PATH
ENV UDEV=1
CMD [ "python", "./main.py" ]

