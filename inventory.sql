
drop database if exists inventory;

create database inventory charset=utf8;

use inventory;

drop table if exists host_list;

create table host_list (
  host_name varchar(64)  not null,
  primary key(host_name)
) engine MyISAM charset=utf8;

drop table if exists hosts;

create table hosts (
  host_name     varchar(64)  not null,
  is_up         varchar(3)   null,
  is_vm         varchar(3)   null,
  distro        varchar(16)  null,
  version       varchar(255) null,
  version_major varchar(16)  null,
  version_minor varchar(16)  null,
  cpumodel      varchar(255) null,
  procs         int          null,
  uptime        varchar(255) null,
  ps_output     text null,
  sockstat      text null,
  lsblk_output  text null,
  primary key(host_name)
) engine MyISAM charset=utf8;

drop table if exists meminfo;

create table meminfo ( 
  host_name       varchar(64) not null,
  parameter_name  varchar(32) not null,
  parameter_value bigint not null,
  parameter_unit  varchar(8) null,
  primary key(host_name,parameter_name)
) engine MyISAM charset=utf8;

drop table if exists users;

create table users (
  host_name varchar(64) not null,
  user_name varchar(32) not null,
  password  varchar(255) null,
  user_id   bigint not null,
  group_id  bigint not null,
  gecos     varchar(255) null,
  home_dir  varchar(255) null,
  shell     varchar(255) null,
  primary key(host_name,user_name)
) engine MyISAM charset=utf8;

drop table if exists groups;

create table groups (
   host_name  varchar(64) not null,
   group_name varchar(32) not null,
   password   varchar(255) null,
   group_id   bigint not null,
   user_list  text null,
   primary key(host_name,group_name)
 ) engine MyISAM charset=utf8;

drop table if exists processes;

create table processes (
   host_name   varchar(64) not null,
   pid         int             null, -- process ID 
   uid         bigint          null, -- user ID number
   ppid        int             null, -- parent process ID
   vsize       bigint          null, -- total VM size in kB
   rss         bigint          null, -- resident set size
   size        bigint          null, -- memory size in kilobytes
   cmd         text            null, -- simple name of executable
   primary key(host_name,pid)
) engine MyISAM charset=utf8;

drop table if exists netstat;

create table netstat (
   host_name  varchar(64) not null,
   protocol   varchar(8)  not null,
   bind       varchar(32) not null,
   port       int         not null,
   index host_proto_port(host_name,protocol,port)
) engine MyISAM charset=utf8;

drop table if exists ports;

create table ports (
  protocol varchar(8) not null,
  port     int not null,
  program  varchar(255),
  primary key(protocol,port)
) engine MyISAM charset=utf8;

insert into ports values 
('tcp',   22, 'sshd'),
('tcp',   80, 'httpd'),
('tcp',  443, 'https'),
('tcp', 3306, 'MySQL'),
('udp',   68, 'dhcpd'),
('udp',  514, 'syslogd')
;

drop table if exists packages;

create table packages (
  host_name       varchar(64) not null,
  package_name    varchar(64) not null,
  package_version varchar(32) null,
  package_release varchar(32) null,
  package_arch    varchar(8)  null,
  index host_package(host_name,package_name)
) engine MyISAM charset=utf8;

drop table if exists inventory;

create table inventory ( 
   begin datetime null, 
   end datetime null 
) engine MyISAM charset=utf8;

