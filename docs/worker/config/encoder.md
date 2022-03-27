# encoder

`encoder` specifies how tasks will be serialized and compressed.


## Definition

```python
@dataclasses.dataclass(
    frozen=True,
)
class Encoder:
    compressor: typing.Optional[str] = None
    serializer: str = 'pickle'
```


The `compressor` parameter specifies the type of compressor. Each task is compressed before being pushed to the queue. Brokers can reduce storage/memory usage by using `compressor`. Tasks with a lot of parameters or data can quickly take up a lot of memory. Due to the compression algorithm being a CPU intensive operation, using a compressor would negatively impact task pushing/pulling.

You can choose from the following compressors:

- `None` [default] - No compression is applied
- `bzip2`
- `gzip`
- `lzma`
- `zlib`


The `serializer` type is defined by the `serializer` parameter. Whenever a task is pushed to the queue, it should be serialized so the broker can save it as a byte array. Because each serialization algorithm has some limitations, it is critical to choose the right serialization algorithm.

These serializers are available:

- `pickle` [default]:
    - Pros: fast, native, supports many data types.
    - Cons: insecure (allows arbitrary code to run), non-portable, might deceive into thinking parameters are serialized correctly but finding a broken object upon deserialization.
- `msgpack`
    - Pros: fast, portable, and secure.
    - Cons: fewer data types are supported.

Any combination of compressor and serializer can be made to suit your needs.

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
