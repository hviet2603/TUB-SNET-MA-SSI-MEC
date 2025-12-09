# Modify from "https://github.com/decentralized-identity/uni-resolver-driver-did-indy/blob/main/docker/Dockerfile"

# Dockerfile for universalresolver/driver-did-indy

FROM maven:3-eclipse-temurin-17-focal AS build
MAINTAINER Markus Sabadello <markus@danubetech.com>

# build driver-did-indy

WORKDIR /opt/driver-did-indy
ADD pom.xml /opt/driver-did-indy
RUN mvn org.apache.maven.plugins:maven-dependency-plugin:3.3.0:go-offline
ADD src/main/webapp/WEB-INF /opt/driver-did-indy/src/main/webapp/WEB-INF
RUN mvn clean package -P war
ADD . /opt/driver-did-indy
RUN mvn clean package -P war

# build image

FROM jetty:11.0.17-jre17-eclipse-temurin
MAINTAINER Markus Sabadello <markus@danubetech.com>

# install dependencies

USER root

ADD ./lib/ /opt/lib
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y update && \
    apt-get install -y --no-install-recommends software-properties-common gnupg libsodium23 libzmq5 && \
    apt-get -y update && \
    dpkg -i /opt/lib/libssl1.1_1.1.1f-1ubuntu2_amd64.deb && \
    dpkg -i /opt/lib/libindy_1.16.0-bionic_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER jetty

# variables

ENV uniresolver_driver_did_indy_libIndyPath=
ENV uniresolver_driver_did_indy_openParallel=false
ENV uniresolver_driver_did_indy_poolConfigs=debug;./sovrin/snet-hv.txn
ENV uniresolver_driver_did_indy_poolVersions=debug;2
ENV uniresolver_driver_did_indy_walletNames=debug;w1
ENV uniresolver_driver_did_indy_submitterDidSeeds=debug;_
# copy from build stage

COPY --from=build --chown=jetty /opt/driver-did-indy/target/*.war /var/lib/jetty/webapps/ROOT.war
COPY --from=build --chown=jetty /opt/driver-did-indy/sovrin/ /var/lib/jetty/sovrin/

# done

EXPOSE 8080
CMD java -Djetty.http.port=8080 -jar /usr/local/jetty/start.jar