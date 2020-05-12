from . import _connector

from . import mongo
from . import redis


__connectors__ = {
    mongo.Connector.name: mongo.Connector,
    redis.Connector.name: redis.Connector,
}
