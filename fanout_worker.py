import friendDB
import redis
import uuid
import pickle
import pika

######################################################## Handle post
# A dictionary to store the postDB posted by the user
postDB = redis.Redis(host='localhost', port=6379, db=0)

# ########################################## Setting up Message Queue
# Connect to rabbit MQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
# declare queue
channel.queue_declare(queue='FanoutMQ')

feedcache = {}

# ########################################## Setting up Message queue call back
def callback(ch, method, properties, body):
    with open('feedcache', 'wb') as feedcache_file:
        message = pickle.loads(body)
        uuid = message[0]
        friends = message[1]
        feed = pickle.loads(postDB.get(uuid))
        feed_poster = feed[0]
        feed_content = feed[1]
        for friend in friends:
            if friend not in feedcache:
                feedcache[friend] = {}
            feedcache[friend][uuid] = feed_poster
            pickle.dump(feedcache, feedcache_file)
            print(feedcache)
    

# Starting consuming MQ
channel.basic_consume(queue='FanoutMQ',
                      auto_ack=True,
                      on_message_callback=callback)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
