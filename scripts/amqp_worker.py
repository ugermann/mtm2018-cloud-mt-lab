#!/usr/bin/env python3
import sys, argparse, logging, time, pika
from websocket import create_connection

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-J", "--job-queue", default = "localhost:5672")
    parser.add_argument("-T", "--mt-server", default = "localhost:8080")
    parser.add_argument("-v", "--verbose", nargs='?',
                        const='INFO', default='WARN') 
    return parser.parse_args()

class TranslationClient:
    def __init__(self,host):
        self.host = host
        self.url = "ws://%s/translate"%(host)
        self.conn = self.reconnect()
        return

    def reconnect(self):
        tries_left = 60
        while tries_left:
            try:
                logger.info("Connecting to server %s"%self.url)
                conn = create_connection(self.url)
                return conn
            except:
                tries_left -= 1
                if tries_left:
                    logger.info("Could not connect to server. "
                                "%d tries left."%tries_left)
                else:
                    logger.error("Fatal error. "
                                 "Could not connect for 60 seconds.")
                    pass
                time.sleep(1)
                pass
            pass
        return
    
    def translate(self,line):
        retries = 3
        while retries:
            try:
                self.conn.send(line)
                translation = self.conn.recv()
                break
            except:
                retries -= 1
                if retries:
                    conn = self.reconnect()
                else:
                    logger.error("Cannot communicate with server. Giving up.")
                    raise
                time.sleep(1)
                pass
            pass
        return translation
    pass # end of class definition

opts = parse_args()
logging.basicConfig(level=opts.verbose,format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# set up translation client connection
C = TranslationClient(opts.mt_server)
logger.info("Ready for translation")

# listen on job_queue
params = pika.ConnectionParameters(host='localhost')
connection = pika.BlockingConnection()
logger.info("Have connection")
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
logger.info(' [*] Waiting for messages. To exit press CTRL+C')

# callback function to execute for each new message
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    print(" [x] Properties ", properties)
    translation = C.translate(body)
    ch.basic_publish\
        (exchange = '', body = translation,
         routing_key = properties.reply_to,
         properties = pika.BasicProperties(
             correlation_id = properties.correlation_id,
         ))

    print(translation)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    return
    
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='task_queue')
channel.start_consuming()

# #!/usr/bin/env python3
# import sys, argparse, logging, time, asyncio
# from websocket import create_connection

# from aio_pika import IncomingMessage, Message, connect as connect_to_job_queue

# logger = logging.getLogger(__name__)

# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-J", "--job-queue-host",
#                         default="localhost:5672")
#     parser.add_argument("-T", "--translation-server-host",
#                         default = "localhost:8080")
#     parser.add_argument("-v", "--verbose", nargs='?',
#                         const='INFO', default='WARN') 
#     return parser.parse_args()

# class TranslationClient:
#     def __init__(self,host):
#         self.host = host
#         self.url = "ws://%s/translate"%host
#         self.conn = None
#         return

#     async def reconnect(self):
#         tries_left = 60
#         while tries_left:
#             try:
#                 logger.info("Connecting to server %s"%self.url)
#                 conn = create_connection(self.url)
#                 return conn
#             except:
#                 tries_left -= 1
#                 if tries_left:
#                     logger.info("Could not connect to server. "
#                                 "%d tries left."%tries_left)
#                 else:
#                     logger.error("Fatal error. "
#                                  "Could not connect for 60 seconds.")
#                     pass
#                 await asyncio.sleep(1)
#                 pass
#             pass
#         return
    
#     async def translate(self,line):
#         retries = 3
#         while retries:
#             try:
#                 self.conn.send(line)
#                 translation = self.conn.recv()
#                 break
#             except:
#                 retries -= 1
#                 if retries:
#                     conn = self.reconnect()
#                 else:
#                     logger.error("Cannot communicate with server. Giving up.")
#                     raise
#                 await async.sleep(1)
#                 pass
#             pass
#         return translation
#     pass # end of class definition


# async def main(loop):
#     opts = parse_args()
#     logging.basicConfig(level=opts.verbose,format="%(levelname)s %(message)s")
#     C = TranslationClient(opts.host, opts.port)
#     await C.reconnect()

#     connection = await connect(
#         "amqp://guest:guest@%s/"%opts.job_queue_host, loop=loop
#     )

#     # Creating a channel
#     channel = await connection.channel()

#     # Declaring queue
#     queue = await channel.declare_queue('mt-jobs')

#     async def on_message(msg: IncomingMessage):
#         print(" [x] Received message %r" % msg)
#         print("Message body is: %r" % msg.body)
#         translation = await C.translate(msg.body)
#         response = Message(translation,
#                            correlation_id=msg.correlation_id)
#         await channel.default_exchange.\
#             publish(msg, routing_key=msg.reply_to)
#         print("Sent translation to %s"%msg.reply_to)
#         return

    

# if __name__ == "__main__":
#     logger.info("Ready for translation")
#     for line in sys.stdin:
#         print(C.translate(line),end='')
#         pass

        
