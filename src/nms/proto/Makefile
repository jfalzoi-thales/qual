PROTOC=protoc

all:
	$(PROTOC) --python_out=../host/pb2 common_nm.proto
	$(PROTOC) --python_out=../host/pb2 nms_host_api.proto
	$(PROTOC) --python_out=../guest/pb2 nms_guest_api.proto
	$(PROTOC) --python_out=../guest/pb2 common_nm.proto

clean:
	rm ../host/pb2/*_pb2.py 2>/dev/null || true
	rm ../host/pb2/*_pb2.pyc 2>/dev/null || true
	rm ../guest/pb2/*_pb2.py 2>/dev/null || true
	rm ../guest/pb2/*_pb2.pyc 2>/dev/null || true
