# `sample-test-app`
This is a simple example of static content served using httpd.

## Building with s2i
```
s2i build https://github.com/sclorg/httpd-container.git --context-dir=examples/sample-test-app/ centos/httpd-24-centos7 httpd-sample-app
```

## Building and deploying in OpenShift
```
oc new-app centos/httpd-24-centos7~https://github.com/sclorg/httpd-container.git --context-dir=examples/sample-test-app
```
