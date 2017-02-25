s/^Listen 80/Listen 0.0.0.0:8080/
s/^User apache/User default/
s/^Group apache/Group root/
151s%AllowOverride None%AllowOverride All%
