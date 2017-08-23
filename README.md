# Inventory

Script in Python to create an inventory of Red Hat/CentOS servers.

## Getting Started

This script is part of my Python's programming study.

This version is a POC and should not be used in a production environment.

### Prerequisites

The script depends on:

 * Python
 * module pymysql
 * module paramiko
 * MySQL database

### Usage

See "run.sh".

Example:
``` shell
$ ./run.sh
... many DDLs output...

--------------
insert into host_list values ('test')
--------------

Query OK, 1 row affected (0.00 sec)

Bye

Inventory ------------------------------------------------------------

. Initialize

. Extract
  . 192.168.10.138...
  . py...
  . test...
    Error: SSH connect(test)

. Transform
  . 192.168.10.138...
  . py...
  . test...

. Load
  . 192.168.10.138...
  . py...
  . test...

----------------------------------------------------------------------

``` 

## Author

* Nereu Matos - [nereum](https://github.com/nereum/)


## License

This project is licensed under the Creative Commons CC0
