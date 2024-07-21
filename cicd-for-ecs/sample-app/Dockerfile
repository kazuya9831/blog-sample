FROM python:3.12-slim-bookworm
COPY src/ .

RUN pip install streamlit

CMD [ "streamlit", "run", "--client.showSidebarNavigation=False", "--server.port", "80", "./main.py"]
