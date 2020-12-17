#!/bin/bash -x
mv /home/bitnami/htdocs/index.html /home/bitnami/htdocs/index.html.bak
wget https://raw.githubusercontent.com/osirislab/Giraffe/master/htdocs/ssrf.php -O /home/bitnami/htdocs/index.php