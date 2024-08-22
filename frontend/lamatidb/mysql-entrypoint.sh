#!/bin/bash

# Remove the old MySQL data directory
rm -rf /var/lib/mysql/*

# Re-initialize the MySQL data directory
mysqld --initialize-insecure --user=mysql

# Start the MySQL server
exec mysqld
