Apache HTTP Server 2.4
======================

This container image includes Apache HTTP Server 2.4 for OpenShift and general usage.
Users can choose between RHEL, CentOS, and Fedora based images.
The RHEL image is available in the [Red Hat Registry](https://access.redhat.com/containers)
as registry.access.redhat.com/rhscl/httpd-24-rhel7.
The CentOS image is then available on [Docker Hub](https://hub.docker.com/r/centos/httpd-24-centos7/)
as centos/httpd-24-centos7.


DESCRIPTION
-----------

Apache HTTP Server 2.4 available as docker container, is a powerful, efficient,
and extensible web server. Apache supports a variety of features, many implemented as compiled modules
which extend the core functionality.
These can range from server-side programming language support to authentication schemes.
Virtual hosting allows one Apache installation to serve many different Web sites."


USAGE
-----

For this, we will assume that you are using the `rhscl/httpd-24-rhel7` image.
The image can be used as a base image for other applications based on Apache HTTP web server.

An example of the data on the host for both the examples above, that will be served by
Apache HTTP web server:

```
$ ls -lZ /wwwdata/html
-rw-r--r--. 1 1001 1001 54321 Jan 01 12:34 index.html
-rw-r--r--. 1 1001 1001  5678 Jan 01 12:34 page.html
```

If you want to run the image and mount the static pages available in `/wwwdata` on the host
as a docker volume, execute the following command:

```
$ docker run -d --name httpd -p 8080:8080 -v /wwwdata:/var/www:Z rhscl/httpd-24-rhel7
```

This will create a container named `httpd` running Apache HTTP Server, serving data from
`/wwwdata` directory. Port 8080 will be exposed and mapped to the host.

If you want to create a new Docker layered image, use [Source-to-Image](https://github.com/openshift/source-to-image), a tool for building/building artifacts from source and injecting into docker images. To create a new Docker image named `httpd-app` using Source-to-Image, while using data available `/www/data` on the host, execute the following command:

```
$ s2i build file:///wwwdata/html rhscl/httpd-24-rhel7 httpd-app
```

To run such a new image, execute the following command:

```
$ docker run -d --name httpd -p 8080:8080 httpd-app
```


CONFIGURATION
-------------

The Apache HTTP Server container image supports the following configuration variable, which can be set by using the `-e` option with the docker run command:

|    Variable name        |    Description                            |
| :---------------------- | ----------------------------------------- |
|  `HTTPD_LOG_TO_VOLUME` | By default, httpd logs into standard output, so the logs are accessible by using the docker logs command. When `HTTPD_LOG_TO_VOLUME` is set, httpd logs into `/var/log/httpd24`, which can be mounted to host system using the Docker volumes. This option is only allowed when container is run as UID 0. |


If you want to run the image and mount the log files into `/wwwlogs` on the host
as a docker volume, execute the following command:

```
$ docker run -d -u 0 -e HTTPD_LOG_TO_VOLUME=1 --name httpd -v /wwwlogs:/var/log/httpd24:Z rhscl/httpd-24-rhel7
```


VOLUMES
-------

You can also set the following mount points by passing the `-v /host:/container` flag to Docker.

|  Volume mount point      | Description                                                            |
| :----------------------- | ---------------------------------------------------------------------- |
|  `/var/www`              | Apache HTTP Server data directory                                      |
|  `/var/log/httpd24`      | Apache HTTP Server log directory (available only when running as root, path `/var/log/httpd` is used in case of Fedora based image) |

**Notice: When mouting a directory from the host into the container, ensure that the mounted
directory has the appropriate permissions and that the owner and group of the directory
matches the user UID or name which is running inside the container.**


DEFAULT USER
------------

By default, Apache HTTP Server container runs as UID 1001. That means the volume mounted directories for the files (if mounted using `-v` option) need to be prepared properly, so the UID 1001 can read them.

To run the container as a different UID, use `-u` option. For example if you want to run the container as UID 1234, execute the following command:

```
docker run -d -u 1234 rhscl/httpd-24-rhel7
```

To log into a volume mounted directory, the container needs to be run as UID 0 (see above).



TROUBLESHOOTING
---------------
The httpd deamon in the container logs to the standard output by default, so the log is available in the container log. The log can be examined by running:

    docker logs <container>


SEE ALSO
--------
Dockerfile and other sources for this container image are available on
https://github.com/sclorg/httpd-container.
In that repository, Dockerfile for CentOS is called Dockerfile, Dockerfile
for RHEL is called Dockerfile.rhel7.

