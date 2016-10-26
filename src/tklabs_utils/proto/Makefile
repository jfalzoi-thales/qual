PROTOC=protoc

all:
	$(PROTOC) --python_out=../pb2 common_nm.proto

clean:
	rm ../pb2/*_pb2.py 2>/dev/null || true
	rm ../pb2/*_pb2.pyc 2>/dev/null || true
