FROM --platform=linux/amd64 python:3.10.14-slim-bookworm

WORKDIR /usr/app

RUN pip install langchain_google_genai
RUN pip install flask

COPY ./ ./

EXPOSE 3000

CMD ["python", "server.py"]