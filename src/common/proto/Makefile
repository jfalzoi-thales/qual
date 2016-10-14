PROTOC=protoc

all:
	$(PROTOC) --python_out=../pb2 ARINC429Driver.proto
	$(PROTOC) --python_out=../pb2 ARINC717Driver.proto
	$(PROTOC) --python_out=../pb2 ErrorMessage.proto
	$(PROTOC) --python_out=../pb2 GPIOManager.proto
	$(PROTOC) --python_out=../pb2 HDDS_API.proto
	$(PROTOC) --python_out=../pb2 MessageHeader.proto
	$(PROTOC) --python_out=../pb2 PowerInfo.proto
	$(PROTOC) --python_out=../pb2 SEMA.proto
	$(PROTOC) --python_out=../pb2 rtc_driver.proto

clean:
	rm ../pb2/*_pb2.py 2>/dev/null || true
	rm ../pb2/*_pb2.pyc 2>/dev/null || true
