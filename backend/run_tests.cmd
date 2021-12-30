docker build -t "test:githubdata" .
docker run -it --rm --name "testgithubdata" test:githubdata ./test.sh