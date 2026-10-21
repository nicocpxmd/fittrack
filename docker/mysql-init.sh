#!/bin/bash
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE goals; CREATE DATABASE workouts;"
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" goals < /schemas/goals.sql
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" workouts < /schemas/workouts.sql
