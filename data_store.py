import os
import logging

import redis

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

def get_redis_client():
  host = os.getenv("REDIS_HOST") or "localhost"
  port = int(os.getenv("REDIS_PORT") or 6379)
  LOG.info(f"Connecting to redis on {host}:{port}")

  return redis.Redis(host=host, port=port, db=0)

class DataStore():
  def __init__(self):
    self.redis_client = get_redis_client()

  def set_sheet_for_channel(self, guild_id, channel_id, sheet_key):
    key = self._channel_key(guild_id, channel_id)
    self.redis_client.set(key, sheet_key)

  def get_sheet_for_channel(self, guild_id, channel_id):
    key = self._channel_key(guild_id, channel_id)
    return self.redis_client.get(key).decode('utf-8')

  def _channel_key(self, guild_id, channel_id):
    return f"g{guild_id}:c{channel_id}"

if __name__ == "__main__":
  from dotenv import load_dotenv
  load_dotenv()

  r = get_redis_client()
  print(r.keys('*'))
  r.set('foo', 'bar')
  print(r.get('foo'))
  r.set('foo', 'baz')
  print(r.get('foo'))
