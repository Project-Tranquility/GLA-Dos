FROM alpine
WORKDIR /app
RUN apk add --no-cache python3 py3-pip sqlite sqlite-libs
COPY requirement.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirement.txt
COPY . .
CMD ["python3", "main.py"]