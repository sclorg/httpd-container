Apache HTTP Server Container Images
===================================
[![Docker Repository on Quay](https://quay.io/repository/centos7/httpd-24-centos7/status "Docker Repository on Quay")](https://quay.io/repository/centos7/httpd-24-centos7)

This repository contains Dockerfiles for Apache HTTP Server images for OpenShift and general usage.
Users can choose between RHEL and CentOS based images.

For more information about contributing, see
[the Contribution Guidelines](https://github.com/sclorg/welcome/blob/master/contribution.md).
For more information about concepts used in these container images, see the
[Landing page](https://github.com/sclorg/welcome).


Versions
--------
Apache HTTPD versions currently provided are:
* [httpd-2.4](2.4)

RHEL versions currently supported are:
* RHEL 7

CentOS versions currently supported are:
* CentOS 7


Installation
------------
Choose either the CentOS7 or RHEL7 based image:

*  **RHEL7 based image**

    These images are available in the [Red Hat Container Catalog](https://access.redhat.com/containers/#/registry.access.redhat.com/rhscl/httpd-24-rhel7).
    To download it run:

    ```
    $ podman pull registry.access.redhat.com/rhscl/httpd-24-rhel7
    ```

    To build a RHEL7 based Apache HTTP Server image, you need to run Docker build on a properly
    subscribed RHEL machine.

    ```
    $ git clone --recursive https://github.com/sclorg/httpd-container.git
    $ cd httpd-container
    $ git submodule update --init
    $ make build TARGET=rhel7 VERSIONS=2.4
    ```

*  **CentOS7 based image**

    This image is available on DockerHub. To download it run:

    ```
    $ podman pull quay.io/centos7/httpd-24-centos7
    ```

    To build a CentOS based Apache HTTP Server image from scratch run:

    ```
    $ git clone --recursive https://github.com/sclorg/httpd-container.git
    $ cd httpd-container
    $ git submodule update --init
    $ make build TARGET=centos7 VERSIONS=2.4
    ```

For using other versions of Apache HTTP Server, just replace the `2.4` value by particular version
in the commands above.

Note: while the installation steps are calling `podman`, you can replace any such calls by `docker` with the same arguments.

**Notice: By omitting the `VERSIONS` parameter, the build/test action will be performed
on all provided versions of Apache HTTP Server, which must be specified in  `VERSIONS` variable.
This variable must be set to a list with possible versions (subdirectories).**


Usage
-----

For information about usage of Dockerfile for Apache HTTP Server 2.4,
see [usage documentation](2.4).


Test
----

This repository also provides a test framework, which checks basic functionality
of the Apache HTTP Server image.

Users can choose between testing Apache HTTP Server based on a RHEL or CentOS image.

*  **RHEL based image**

    To test a RHEL7 based Apache HTTP Server image, you need to run the test on a properly
    subscribed RHEL machine.

    ```
    $ cd httpd-container
    $ git submodule update --init
    $ make test TARGET=rhel7 VERSIONS=2.4
    ```

*  **CentOS based image**

    ```
    $ cd httpd-container
    $ git submodule update --init
    $ make test TARGET=centos7 VERSIONS=2.4
    ```

For using other versions of Apache HTTP Server, just replace the `2.4` value by particular version
in the commands above.

**Notice: By omitting the `VERSIONS` parameter, the build/test action will be performed
on all provided versions of Apache HTTP Server, which must be specified in  `VERSIONS` variable.
This variable must be set to a list with possible versions (subdirectories).**

