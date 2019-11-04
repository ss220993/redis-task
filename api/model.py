import redis

db = redis.Redis('localhost')
recent_key = 'event:Recent:'
brands_count_key = 'event:Brand:'


def get_recent_item(timeGiven):
    return db.get(recent_key + timeGiven)


def get_brands_count(timeGiven):
    return db.get(brands_count_key + timeGiven)
