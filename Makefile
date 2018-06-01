all: test protocol

test: protocol
	@./bin/with-env.sh ./bin/run-test.sh

protocol: proto/session.proto
	@mkdir -p py_gen
	@protoc -I=proto --python_out=py_gen proto/session.proto

clean:
	@rm -rf py_gen
	@find . -type f -regex ".*pyc" | xargs rm

cli: protocol
	./bin/with-env.sh ./src/cli.py --play

replay: protocol
	./bin/with-env.sh ./src/cli.py --replay

web: protocol
	./bin/with-env.sh python2 ./src/web.py 8080
