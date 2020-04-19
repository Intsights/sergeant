from . import msgpack
from . import json
from . import pickle


__serializers__ = {
    msgpack.Serializer.name: msgpack.Serializer,
    json.Serializer.name: json.Serializer,
    pickle.Serializer.name: pickle.Serializer,
}
