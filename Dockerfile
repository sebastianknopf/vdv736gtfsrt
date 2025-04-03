# select base image
FROM python:3.10-slim

# workdir inside the container is /app
WORKDIR /app

# install git in order to use setuptools_scm
# required for automatic detection of version
RUN apt-get update && apt-get install -y git

# copy everything into container
COPY . .

# run installation inside the container
RUN pip install --no-cache-dir .
RUN rm -rf .git
RUN rm -rf .github

# expose default port for GTFS-RT server
# however note, that this is a default port only and can be overriden
# also note, that a VDV736 subscriber will also open a port
# in public/subscribe mode to make it's endpoint reachable
# hence, this is DOCUMENTATION ONLY
EXPOSE 8080

# ready - run the converter
ENTRYPOINT ["sh", "-c", "python vdv736gtfsrt"]

# CMD is defined at runtime