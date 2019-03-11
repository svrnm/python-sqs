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
            with appd.bt('process message', correlation_header) as bt_handle:
                print(correlation_header)
                print('Hello, {0}!{1}'.format(message.body, author_text))
                exit_call_handle = appd.start_exit_call(bt_handle, appd.EXIT_CACHE, 'sqs-2', {'VENDOR': 'AWS', 'SERVERPOOL': 'appd-test-queue-2'})
                print(appd.make_correlation_header(bt_handle, exit_call_handle))
                time.sleep( 1 )
                appd.end_exit_call(exit_call_handle)


            # Let the queue know that the message is processed
            message.delete()
