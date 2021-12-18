#!/bin/bash

# cleaning up coverage info
rm -rf coverage_info
# cleaning up a testing container that might've not been removed before
docker rm -f test-desk2-api > /dev/null 2>&1

# building an image
docker build --file deploy/api.dockerfile -t desk2-api .

# unit, integration testing, code coverage
echo "Running unit tests in a container..."
docker run -d -e "EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'" -e "EMAIL_HOST_USER='123'" -e "EMAIL_HOST_PASSWORD='123'" --name test-desk2-api -i --entrypoint /usr/bin/dash desk2-api

# executing migrations
echo -e "echo \"1\n''\n1\n''\n2\n\" | python manage.py makemigrations\n" | docker exec -i test-desk2-api /usr/bin/dash
echo -e "python manage.py migrate\n" | docker exec -i test-desk2-api /usr/bin/dash

UNIT_TEST_RES=$(echo -e "coverage run manage.py test\n" | docker exec -i test-desk2-api /usr/bin/dash 2>&1 | tee /dev/tty)
echo -e "coverage html" | docker exec -i test-desk2-api /usr/bin/dash
docker cp test-desk2-api:/app/htmlcov coverage_info
echo "Coverage info was expored to ./coverage_info"

echo "Removing a testing container..."
docker rm -f test-desk2-api > /dev/null 2>&1
if [ $(echo $UNIT_TEST_RES | grep "FAIL") ]
then
    echo "Errors when executing unit tests, exiting"
    exit 3
fi

# smoke testing
cd tests
echo "Running smoke tests..."
# cleaning up a testing deployment that might've not been removed before
docker-container down > /dev/null 2>&1

SMOKE_TEST_RES=$(python run-smoke-tests.py 2>&1 | tee /dev/tty)
if [ $(echo $SMOKE_TEST_RES | grep "Failed") ]
then
    echo "Errors when executing smoke tests, exiting"
    exit 3
fi
cd ..