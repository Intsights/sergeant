from . import mongo
from . import redis
from . import redis_cluster

from . import _connector


__connectors__ = {
    mongo.Connector.name: mongo.Connector,
    redis_cluster.Connector.name: redis_cluster.Connector,
    redis.Connector.name: redis.Connector,
}
