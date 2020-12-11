Apache HTTP Server 2.4 Container Image
======================================

This container image includes Apache HTTP Server 2.4 for OpenShift and general usage.
Users can choose between RHEL, CentOS and Fedora based images.
The RHEL images are available in the [Red Hat Container Catalog](https://access.redhat.com/containers/),
the CentOS images are available on [Quay.io](https://quay.io/organization/centos7),
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


Usage in OpenShift
------------------
In this example, we assume that you are using the `rhel8/httpd-24` image, available through the `httpd:24` imagestream tag in Openshift.
To build a simple [httpd-sample-app](https://github.com/sclorg/httpd-ex.git) application in Openshift:

```
oc new-app httpd:24~https://github.com/sclorg/httpd-ex.git
```

To access the application:
```
$ oc get pods
$ oc exec <pod> -- curl 127.0.0.1:8080
```

Source-to-Image framework and scripts
-------------------------------------
This image supports the [Source-to-Image](https://docs.openshift.com/container-platform/3.11/creating_images/s2i.html)
(S2I) strategy in OpenShift. The Source-to-Image is an OpenShift framework
which makes it easy to write images that take application source code as
an input, use a builder image like this httpd container image, and produce
a new image that runs the assembled application as an output.

To support the Source-to-Image framework, important scripts are included in the builder image:

* The `/usr/libexec/s2i/run` script is set as the default command in the resulting container image (the new image with the application artifacts).

* The `/usr/libexec/s2i/assemble` script inside the image is run to produce a new image with the application artifacts. The script takes sources of a given application and places them into appropriate directories inside the image. The structure of httpd-app can look like this:

**`./httpd-cfg`**  
       Can contain additional Apache configuration files (`*.conf`)

**`./httpd-pre-init`**  
       Can contain shell scripts (`*.sh`) that are sourced before `httpd` is started

**`./httpd-ssl`**  
       Can contain user's own SSL certificate (in the `certs/` subdirectory) and a key (in the `private/` subdirectory)

**`./`**  
       Application source code


Build an application using a Dockerfile
---------------------------------------
Compared to the Source-to-Image strategy, using a Dockerfile is a more
flexible way to build an httpd container image with an application.
Use a Dockerfile when Source-to-Image is not sufficiently flexible for you or
when you build the image outside of the OpenShift environment.

To use the httpd image in a Dockerfile, follow these steps:

#### 1. Pull a base builder image to build on

```
podman pull rhel8/httpd-24
```

#### 2. Pull an application code

An example application available at https://github.com/sclorg/httpd-ex.git is used here. To adjust the example application, clone the repository.

```
git clone https://github.com/sclorg/httpd-ex.git app-src
```

#### 3. Prepare an application inside a container

This step usually consists of at least these parts:

* putting the application source into the container
* moving certificates to the correct place (if available in the application source code)
* setting the default command in the resulting image

For all these three parts, you can either set up all manually and use the `httpd` or `run-httpd` commands explicitly in the Dockerfile ([3.1.](#31-to-use-own-setup-create-a-dockerfile-with-this-content)), or you can use the Source-to-Image scripts inside the image ([3.2.](#32-to-use-the-source-to-image-scripts-and-build-an-image-using-a-dockerfile-create-a-dockerfile-with-this-content). For more information about these scripts, which enable you to set-up and run the httpd daemon, see the "Source-to-Image framework and scripts" section above.

##### 3.1. To use your own setup, create a Dockerfile with this content:
```
FROM registry.redhat.io/rhel8/httpd-24

# Add application sources
ADD app-src/index.html /var/www/html/index.html

# The run script uses standard ways to run the application
CMD run-httpd
```

##### 3.2. To use the Source-to-Image scripts and build an image using a Dockerfile, create a Dockerfile with this content:
```
FROM registry.redhat.io/rhel8/httpd-24

# Add application sources to a directory where the assemble script expects them
# and set permissions so that the container runs without the root access
USER 0
ADD app-src/index.html /tmp/src/index.html
RUN chown -R 1001:0 /tmp/src
USER 1001

# Let the assemble script install the dependencies
RUN /usr/libexec/s2i/assemble

# The run script uses standard ways to run the application
CMD /usr/libexec/s2i/run
```

#### 4. Build a new image from a Dockerfile prepared in the previous step

```
podman build -t httpd-app .
```

#### 5. Run the resulting image with the final application

```
podman run -d httpd-app
```


Direct usage with a mounted directory
-------------------------------------

An example of the data on the host for both the examples above, which is served by
The Apache HTTP web server:

```
$ ls -lZ /wwwdata/html
-rw-r--r--. 1 1001 1001 54321 Jan 01 12:34 index.html
-rw-r--r--. 1 1001 1001  5678 Jan 01 12:34 page.html
```

If you want to run the image directly and mount the static pages available in the `/wwwdata/` directory on the host
as a container volume, execute the following command:

```
$ podman run -d --name httpd -p 8080:8080 -v /wwwdata:/var/www:Z rhel8/httpd-24
```

This creates a container named `httpd` running the Apache HTTP Server, serving data from
` the /wwwdata/` directory. Port 8080 is exposed and mapped to the host.



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
$ podman run -d -u 0 -e HTTPD_LOG_TO_VOLUME=1 --name httpd -v /wwwlogs:/var/log/httpd24:Z rhel8/httpd-24
```

To run an image using the `event` MPM (rather than the default `prefork`), execute the following command:

```
$ podman run -d -e HTTPD_MPM=event --name httpd rhel8/httpd-24
```

You can also set the following mount points by passing the `-v /host:/container` flag to podman.

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
podman run -d -u 1234 rhel8/httpd-24
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
In that repository, the Dockerfile for CentOS7 is called Dockerfile, the Dockerfile
for RHEL7 is called Dockerfile.rhel7, the Dockerfile for RHEL8 is called Dockerfile.rhel8,
and the Dockerfile for Fedora is called Dockerfile.fedora.
