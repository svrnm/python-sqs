# Copyright 2019 Severin Neumann
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

# APPDYNAMICS: Import and init
from appdynamics.agent import api as appd
appd.init()
import tornado.ioloop
import tornado.web
import os
import boto3
import requests
import json

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='appd-test-queue')

class SendHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.uri)
        # APPDYNAMICS: Get BT handle
        self.sendMessage()

    def sendMessage(self):
        bt_handle = appd.get_active_bt_handle(self.request)
        exit_call_handle = appd.start_exit_call(bt_handle, appd.EXIT_QUEUE, 'sqs-queue', {'VENDOR': 'AWS', 'SERVERPOOL': 'appd-test-queue'})
        correlation_header = appd.make_correlation_header(bt_handle, exit_call_handle)
        print(correlation_header)
        appd.add_snapshot_data(bt_handle,'Author','AppDynamics')
        queue.send_message(MessageBody='boto3', MessageAttributes={
            'Author': {
                'StringValue': 'AppDynamics',
                'DataType': 'String'
                },
            'AppDynamicsCorrelationHeader': {
                'StringValue': correlation_header[1],
                'DataType': 'String'
            }
        })
        # requestGUID = correlation_header[1].split('*guid=')[1].split('*')[0]
        # data = json.dumps([{'name':'start','requestGUID':requestGUID}])
        # response = requests.post('https://analytics.api.appdynamics.com/events/publish/dummy', headers={'X-Events-API-AccountName':'<<>>', 'X-Events-API-Key':'<<>>', 'content-type':'application/vnd.appd.events+json;v=2'}, data=data)
        appd.end_exit_call(exit_call_handle)

class ProcessHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(self.request.uri)
        for message in queue.receive_messages(MessageAttributeNames=['Author']):
            # Get the custom author message attribute if it was set
            author_text = ''
            if message.message_attributes is not None:
                author_name = message.message_attributes.get('Author').get('StringValue')
                if author_name:
                    author_text = ' ({0})'.format(author_name)

            # Print out the body and author (if set)
            self.write('Hello, {0}!{1}'.format(message.body, author_text))

            # Let the queue know that the message is processed
            message.delete()



def make_app():
    return tornado.web.Application([
        (r"/send", SendHandler),
        (r"/process", ProcessHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    port = os.environ.get('TORNADO_PORT') if os.environ.get('TORNADO_PORT') else '8666'
    app.listen(port)
    print('Running python node on port ' + port)
    tornado.ioloop.IOLoop.current().start()
