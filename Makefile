all: test protocol

test: protocol
	@./run_test.sh

protocol: proto/session.proto
	@mkdir -p py_gen
	@protoc -I=proto --python_out=py_gen proto/session.proto

clean:
	@rm -rf py_gen
	@find . -type f -regex ".*pyc" | xargs rm
