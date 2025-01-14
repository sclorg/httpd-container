Apache HTTP Server Container Images
===================================

[![Build and push images to Quay.io registry](https://github.com/sclorg/httpd-container/actions/workflows/build-and-push.yml/badge.svg)](https://github.com/sclorg/httpd-container/actions/workflows/build-and-push.yml)

Images available on Quay are:
* Fedora [httpd-2.4](https://quay.io/repository/fedora/httpd-24)

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
* [httpd-2.4-micro](2.4-micro)

RHEL versions currently supported are:
* RHEL 8
* RHEL 9
* RHEL 10

CentOS Stream versions currently supported are:
* CentOS Stream 9
* CentOS Stream 10


Installation
------------
Choose either the CentOS Stream 9, CentOS Stream 10, RHEL8 based image, RHEL9 based image, or RHEL10 based image:

*  **RHEL8 based image**

    These images are available in the [Red Hat Container Catalog](https://catalog.redhat.com/software/containers/ubi8/httpd-24/6065b844aee24f523c207943?architecture=amd64&image=6660528072b80acc3c2193f3&container-tabs=overview).
    To download it run:

    ```
    $ podman pull registry.access.redhat.com/rhel8/httpd-24
    ```

    To build a RHEL8 based Apache HTTP Server image, you need to run Docker build on a properly
    subscribed RHEL machine.

    ```
    $ git clone --recursive https://github.com/sclorg/httpd-container.git
    $ cd httpd-container
    $ git submodule update --init
    $ make build TARGET=rhel8 VERSIONS=2.4
    ```

*  **CentOS Stream 9 based image**

    This image is available on DockerHub. To download it run:

    ```
    $ podman pull quay.io/sclorg/httpd-24-c9s
    ```

    To build a CentOS based Apache HTTP Server image from scratch run:

    ```
    $ git clone --recursive https://github.com/sclorg/httpd-container.git
    $ cd httpd-container
    $ git submodule update --init
    $ make build TARGET=c9s VERSIONS=2.4
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

Users can choose between testing Apache HTTP Server based on a RHEL or CentOS Stream image.

*  **RHEL based image**

    To test a RHEL8 based Apache HTTP Server image, you need to run the test on a properly
    subscribed RHEL machine.

    ```
    $ cd httpd-container
    $ git submodule update --init
    $ make test TARGET=rhel8 VERSIONS=2.4
    ```

*  **CentOS Stream based image**

    ```
    $ cd httpd-container
    $ git submodule update --init
    $ make test TARGET=c9s VERSIONS=2.4
    ```

For using other versions of Apache HTTP Server, just replace the `2.4` value by particular version
in the commands above.

**Notice: By omitting the `VERSIONS` parameter, the build/test action will be performed
on all provided versions of Apache HTTP Server, which must be specified in  `VERSIONS` variable.
This variable must be set to a list with possible versions (subdirectories).**

