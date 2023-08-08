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

import os
import boto3
import time

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='appd-test-queue')

if __name__ == "__main__":
    while True:
        for message in queue.receive_messages(MessageAttributeNames=['Author','AppDynamicsCorrelationHeader']):
            # Get the custom author message attribute if it was set
            author_text = ''
            correlation_header = None
            if message.message_attributes is not None:
                author_name = message.message_attributes.get('Author').get('StringValue')
                correlation_header = message.message_attributes.get('AppDynamicsCorrelationHeader').get('StringValue')
                if author_name:
                    author_text = ' ({0})'.format(author_name)


            # Print out the body and author (if set)
            # APPDYNAMICS: Create BT handle manually
            print('process message...')
            with appd.bt('process message', correlation_header) as bt_handle:
                time.sleep( 0.5 )
                print(correlation_header)
                print('Hello, {0}!{1}'.format(message.body, author_text))
                appd.add_snapshot_data(bt_handle,'body',message.body)
                exit_call_handle = appd.start_exit_call(bt_handle, appd.EXIT_QUEUE, 'sqs-queue-next', {'VENDOR': 'AWS', 'SERVERPOOL': 'appd-test-queue-next'})
                print(appd.make_correlation_header(bt_handle, exit_call_handle))
                time.sleep( 0.5 )
                appd.end_exit_call(exit_call_handle)


            # Let the queue know that the message is processed
            message.delete()
