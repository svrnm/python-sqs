# Python with correlation for SQS

To run the project rename the [agent.stub.cfg](agent.stub.cfg) to `agent.cfg` and the [loop.stub.cfg](loop.stub.cfg) to `loop.cfg` and
set your controller properties.

Also, configure [boto3](https://github.com/boto/boto3) following the [quickstart](https://github.com/boto/boto3#quick-start), i.e. setup the credentials and config file.

Next, install the files in [requirements.txt](requirements.txt)

```shell
pip install -r requirements.txt
```

Afterwards you can run the application with the following three commands:

- Tornado Webserver:
```shell
env TORNADO_PORT=8888 pyagent run -c agent.cfg -- python index.py
```

- Receiver Loop:
```shell
pyagent run -c loop.cfg -- python loop.py
```

- curl to call the webserver
```shell
while [ true ] ; do curl -o - "http://localhost:8888/send" ; sleep 1; done;
```
