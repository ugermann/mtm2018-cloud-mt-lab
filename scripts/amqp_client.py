#!/usr/bin/env python3
import pika, sys, threading, time

global printed, i
pending = threading.Semaphore(1)

def on_message(ch, method, properties, body):
    id = int(properties.correlation_id)
    print(" [%s] Received: '%s'"%(id,body.decode('utf8').strip()))
    pending.release()
    print(pending," translations pending")
    ch.basic_ack(delivery_tag = method.delivery_tag)
    pass

def print_translations(channel,queue_name):
    channel.basic_consume(on_message, queue=queue_name)
    channel.start_consuming()
    
params = pika.ConnectionParameters(host='localhost')
connection = pika.BlockingConnection(params)
channel = connection.channel()

q = channel.queue_declare(queue='task_queue',durable=True)
r = channel.queue_declare('',exclusive=True,auto_delete=True)

result_printer = threading.Thread(target=print_translations,
                                  args = (channel, r.method.queue,))
result_printer.start()

i = 0
for line in sys.stdin:
    channel.basic_publish(exchange='', routing_key='task_queue',
                          body=line, properties = pika.BasicProperties(
                              reply_to=r.method.queue,
                              correlation_id="%d"%i,))
    pending.acquire()
    print(" [%d] Sent '%s'"%(i,line.strip()))
    i += 1
    pass

# wait till all translations have been printed
while printed < i:
    print(printed,i)
    time.sleep(1)
connection.close()



