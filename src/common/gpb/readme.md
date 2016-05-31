# Generating GPB Files {#GPBBufferReadme}

How to use protoc to compile .proto files into Python using Protocol Compiler 2.6.1:

1. Download and unzip Protocol Compiler 2.6.1 binary for Windows: 
   https://github.com/google/protobuf/releases/download/v2.6.1/protoc-2.6.1-win32.zip
2. Navigate to the unzipped folder and copy protoc.exe
3. Paste protoc.exe into the folder that contains the .proto files you wish to compile
4. Open Command Prompt
5. Change directory to where protoc.exe and your .proto files are
6. Enter the command 'protoc --python_out=C:\put\output\path\here filename.proto'
7. If there are any errors, open the .proto file, fix them, save, and re-run the command
8. Enjoy some coffee