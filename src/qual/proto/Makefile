PROTOC=protoc

all:
	$(PROTOC) --python_out=../pb2 AnalogAudio.proto
	$(PROTOC) --python_out=../pb2 ARINC429.proto
	$(PROTOC) --python_out=../pb2 ARINC485.proto
	$(PROTOC) --python_out=../pb2 ARINC717Frame.proto
	$(PROTOC) --python_out=../pb2 CarrierCardData.proto
	$(PROTOC) --python_out=../pb2 CPULoading.proto
	$(PROTOC) --python_out=../pb2 Encoder.proto
	$(PROTOC) --python_out=../pb2 Ethernet.proto
	$(PROTOC) --python_out=../pb2 GPIO.proto
	$(PROTOC) --python_out=../pb2 HDAudio.proto
	$(PROTOC) --python_out=../pb2 HDDS.proto
	$(PROTOC) --python_out=../pb2 MemoryBandwidth.proto
	$(PROTOC) --python_out=../pb2 RS232.proto
	$(PROTOC) --python_out=../pb2 RS485.proto
	$(PROTOC) --python_out=../pb2 SSD.proto

clean:
	rm ../pb2/*_pb2.py 2>/dev/null || true
	rm ../pb2/*_pb2.pyc 2>/dev/null || true
