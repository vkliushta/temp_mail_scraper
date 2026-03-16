FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		ca-certificates wget gnupg \
		libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
		libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libasound2 \
		libpangocairo-1.0-0 libgtk-3-0 libgbm1 libdrm2 libxss1 \
		fonts-liberation libxrender1 \
	&& rm -rf /var/lib/apt/lists/*

RUN playwright install chromium

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "src.app:create_app()"]
