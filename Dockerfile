FROM python:2.7
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV TORNADO_PORT=80
EXPOSE 80
CMD [ "pyagent", "run", "-c", "agent.cfg", "--", "python", "index.py" ]
