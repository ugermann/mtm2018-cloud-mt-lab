#!/usr/bin/env python3
import sys, argparse, logging, time
from websocket import create_connection

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default = "localhost")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-v", "--verbose", nargs='?',
                        const='INFO', default='WARN') 
    return parser.parse_args()

class TranslationClient:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.url = "ws://%s:%d/translate"%(host,port)
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

if __name__ == "__main__":
    opts = parse_args()
    logging.basicConfig(level=opts.verbose,format="%(levelname)s %(message)s")
    C = TranslationClient(opts.host, opts.port)
    logger.info("Ready for translation")
    for line in sys.stdin:
        print(C.translate(line),end='')
        pass

        
