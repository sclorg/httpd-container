Apache HTTP Server 2.4 Container Image
======================

This container image includes Apache HTTP Server 2.4 for OpenShift and general usage.
Users can choose between RHEL, CentOS and Fedora based images.
The RHEL images are available in the [Red Hat Container Catalog](https://access.redhat.com/containers/),
the CentOS images are available on [Docker Hub](https://hub.docker.com/r/centos/),
and the Fedora images are available in [Fedora Registry](https://registry.fedoraproject.org/).
The resulting image can be run using [podman](https://github.com/containers/libpod).

Note: while the examples in this README are calling `podman`, you can replace any such calls by `docker` with the same arguments

Description
-----------

Apache HTTP Server 2.4 available as container, is a powerful, efficient,
and extensible web server. Apache supports a variety of features, many implemented as compiled modules
which extend the core functionality.
These can range from server-side programming language support to authentication schemes.
Virtual hosting allows one Apache installation to serve many different Web sites."


Usage
-----

For this, we will assume that you are using the Apache HTTP Server 2.4 container image from the
Red Hat Container Catalog called `rhscl/httpd-24-rhel7` available via `httpd:2.4` imagestream tag in Openshift.
The image can be used as a base image for other applications based on Apache HTTP web server.

An example of the data on the host for both the examples above, that will be served by
Apache HTTP web server:

```
$ ls -lZ /wwwdata/html
-rw-r--r--. 1 1001 1001 54321 Jan 01 12:34 index.html
-rw-r--r--. 1 1001 1001  5678 Jan 01 12:34 page.html
```

If you want to run the image and mount the static pages available in `/wwwdata` on the host
as a container volume, execute the following command:

```
$ podman run -d --name httpd -p 8080:8080 -v /wwwdata:/var/www:Z rhscl/httpd-24-rhel7
```

This will create a container named `httpd` running Apache HTTP Server, serving data from
`/wwwdata` directory. Port 8080 will be exposed and mapped to the host.

If you want to create a new container layered image, you can use the Source build feature of Openshift. To create a new httpd application in Openshift, while using data available in `/wwwdata/html` on the host, execute the following command:

```
oc new-app httpd:2.4~/wwwdata/html --name httpd-app
```

The same application can also be built using the standalone [S2I](https://github.com/openshift/source-to-image) application on systems that have it available

```
$ s2i build file:///wwwdata/html rhscl/httpd-24-rhel7 httpd-app
```

The structure of httpd-app can look like this:

**`./httpd-cfg`**  
       Can contain additional Apache configuration files (`*.conf`)

**`./httpd-pre-init`**  
       Can contain shell scripts (`*.sh`) that are sourced before `httpd` is started

**`./httpd-ssl`**  
       Can contain own SSL certificate (in `certs/` subdirectory) and key (in `private/` subdirectory)

**`./`**  
       Application source code


Environment variables and volumes
---------------------------------

The Apache HTTP Server container image supports the following configuration variable, which can be set by using the `-e` option with the podman run command:

**`HTTPD_LOG_TO_VOLUME`**  
       By default, httpd logs into standard output, so the logs are accessible by using the podman logs command. When `HTTPD_LOG_TO_VOLUME` is set, httpd logs into `/var/log/httpd24`, which can be mounted to host system using the container volumes. This option is only allowed when container is run as UID 0.

**`HTTPD_MPM`**
       The variable `HTTPD_MPM` can be set to change the default Multi-Processing Module (MPM) from the package default MPM.


If you want to run the image and mount the log files into `/wwwlogs` on the host
as a container volume, execute the following command:

```
$ podman run -d -u 0 -e HTTPD_LOG_TO_VOLUME=1 --name httpd -v /wwwlogs:/var/log/httpd24:Z rhscl/httpd-24-rhel7
```

To run an image using the `event` MPM (rather than the default `prefork`), execute the following command:

```
$ podman run -d -e HTTPD_MPM=event --name httpd rhscl/httpd-24-rhel7
```

You can also set the following mount points by passing the `-v /host:/container` flag to Docker.

**`/var/www`**  
       Apache HTTP Server data directory

**`/var/log/httpd24`**  
       Apache HTTP Server log directory (available only when running as root, path `/var/log/httpd` is used in case of Fedora based image)


**Notice: When mouting a directory from the host into the container, ensure that the mounted
directory has the appropriate permissions and that the owner and group of the directory
matches the user UID or name which is running inside the container.**

Default SSL certificates
------------------------

Default SSL certificates are generated when Apache HTTP server container is started for the first time or own SSL certificates were not provided (see bolow how to provide them). SSL certificates are not stored in the base image but generated, so each container will have unique default SSL key pair. SSL certificate/key are stored in /etc/httpd/tls directory:

    /etc/httpd/tls/localhost.key
    /etc/httpd/tls/localhost.crt


Using own SSL certificates
--------------------------
In order to provide own SSL certificates for securing the connection with SSL, use the extending feature described above. In particular, put the SSL certificates into a separate directory inside your application:

    ./httpd-ssl/certs/server-cert-selfsigned.pem
    ./httpd-ssl/private/server-key.pem

The default behaviour is to look for the certificate and the private key in subdirectories certs/ and private/; those files will be used for the ssl settings in the httpd.


Default user
------------

By default, Apache HTTP Server container runs as UID 1001. That means the volume mounted directories for the files (if mounted using `-v` option) need to be prepared properly, so the UID 1001 can read them.

To run the container as a different UID, use `-u` option. For example if you want to run the container as UID 1234, execute the following command:

```
podman run -d -u 1234 rhscl/httpd-24-rhel7
```

To log into a volume mounted directory, the container needs to be run as UID 0 (see above).


Troubleshooting
---------------
The httpd deamon in the container logs to the standard output by default, so the log is available in the container log. The log can be examined by running:

    podman logs <container>


See also
--------
Dockerfile and other sources for this container image are available on
https://github.com/sclorg/httpd-container.
In that repository, the Dockerfile for CentOS is called Dockerfile, the Dockerfile
for RHEL7 is called Dockerfile.rhel7, the Dockerfile for RHEL8 is called Dockerfile.rhel8,
and the Dockerfile for Fedora is called Dockerfile.fedora.
