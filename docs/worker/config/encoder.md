# Worker Config - encoder

The `encoder` parameter controls the encoder which is responsible for the tasks compression and serialization.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Encoder:
    compressor: typing.Optional[str] = None
    serializer: str = 'pickle'
```


The `compressor` parameter defines the type of the compressor. Each task prior to being pushed to the queue is going through a compressor. The usage of `compressor` can help reducing the storage/memory of the broker. Tasks with a lot of parameters/data can take a lot of memory and might fill the memory/storage quickly. Using a compressor would impact the performance of task pushing/pulling due to the compression algorithm being a CPU intensive operation.

The following compressors are available:

- `None` [default] - No compression is applied
- `bzip2`
- `gzip`
- `lzma`
- `zlib`


The `serializer` parameter defines the type of the serializer. Each task prior to being pushed to the queue should be serialized so the broker could save it as a byte array. Choosing the right serialization algorithm is important due to some limitations of each serialization algorithm.

The following serializers are available:

- `pickle` [default]:
    - pros: fast, native, many supported data types.
    - cons: insecure (allows to run arbitrary code), non-portable, might mislead to think that the parameters were serialized correctly but deserializing them would end with a broken object.
- `msgpack`
    - pros: fast, portable, secured.
    - cons: fewer supported data types.

One can make any combination of compressor and serializer that suit your needs.

## Examples

=== "default"
    ```python
    sergeant.config.Encoder(
        compressor=None,
        serializer='pickle',
    )
    ```

=== "zlib-pickle"
    ```python
    sergeant.config.Encoder(
        compressor='zlib',
        serializer='pickle',
    )
    ```

=== "lzma-msgpack"
    ```python
    sergeant.config.Encoder(
        compressor='lzma',
        serializer='msgpack',
    )
    ```
