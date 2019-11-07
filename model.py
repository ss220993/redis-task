import redis

db = redis.Redis(host='redis', port='6379')
recent_key = 'event:Recent:'
brands_count_key = 'event:Brand:'
color_key = 'event:Color:'


def get_recent_item(timeGiven):
    return db.get(recent_key + timeGiven)

def get_brands_count(timeGiven):
    return db.get(brands_count_key + timeGiven)

def get_recent_ten_colors(color):
    print("here")
    return db.zrevrangebyscore(color_key + color, '+inf', '-inf', start=0, num=10)