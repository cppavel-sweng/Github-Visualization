# set base image (host OS)
FROM python:3.6

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY tests/requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY tests/test.sh .
COPY tests/github_mock.py .
COPY tests/github_data_test.py .
COPY github_data.py .
COPY programming_languages.py .

# command to run on container start
CMD [ "/bin/bash"]