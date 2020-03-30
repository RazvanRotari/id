
## ID

Generate an unique id ... in python or bash or anything 


Example python:
```
import id

new_unique_id = id.id()
```

Example bash:
```
# mkdir id_fs
# ./id_fs.py id_fs
# cat id_fs/id

```

Run tests:

```
./test_id.py
```

## Dependencies
Optional - to run the id_fs
```
pip install --user fuse-python
```

Check id.py for more the implementation

## Research:
[1] https://devforth.io/blog/why-your-software-should-use-uuids-in-2020s
UUIDv1 - It includes 2 parts: 48-bit Host Mac Address (so already unique for different clients
	who generate it), 60-bit Timestamp (nanoseconds precision, even two subsequent generate
	function calls will never generate same timestamps). It's harder to measure a clash here
	but it is always better to use this version, and later in post, I will explain why.


[2] https://github.com/twitter-archive/snowflake

[3] https://www.callicoder.com/distributed-unique-id-sequence-number-generator/
