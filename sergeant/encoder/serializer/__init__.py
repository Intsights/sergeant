from . import msgpack
from . import pickle


__serializers__ = {
    msgpack.Serializer.name: msgpack.Serializer,
    pickle.Serializer.name: pickle.Serializer,
}
