# Examples of HTTPD container image usage
=========================================
This directory includes several examples of how to use the httpd container to serve static HTML content.

Building and deploying in OpenShift
-------------------
```
oc new-app rhel8/httpd-24~https://github.com/sclorg/httpd-ex.git
```

Building with s2i
-------------------
```
s2i build https://github.com/sclorg/httpd-container.git --context-dir=examples/sample-test-app/ centos/httpd-24-centos7 httpd-sample-app
```
The `s2i` binary can be obtained from https://github.com/openshift/source-to-image.


Dockerfile examples
-------------------

This directory also contains example Dockerfiles that demonstrate how to use the image with a Dockerfile and `docker build`, with an example application code available at https://github.com/sclorg/httpd-ex.git.

1. Pull the source to the local machine first:
```
git clone https://github.com/sclorg/httpd-ex.git app-src
```

2.a. Build a new image from a Dockerfile in this directory:
```
docker build -f Dockerfile -t httpd-app .
```

2.b. Alternatively, build a new image from a Dockerfile.s2i in this directory; this Dockerfile uses the Source-to-Image scripts that are available in the image:
```
docker build -f Dockerfile.s2i -t httpd-app .
```

3. Run the resulting image with the final application:
```
docker run -ti --rm -p 8080:8080 -p 8443:8443 httpd-app
```

4. Get the example static content using curl:
```
curl http://127.0.0.1:8080
curl --insecure https://127.0.0.1:8443
```

Note: The use of the `--insecure` option is caused by using self-signed certificates for HTTPS by default.
