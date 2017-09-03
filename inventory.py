#!/usr/bin/env python

""" 
    Inventory

    Script que faz a coleta de informacoes dos servidores Red Hat/CentOS

    2017-08-10 - Nereu - 1st version
    2017-08-14 - Nereu - rewritten everything
    2017-08-15 - Nereu - more fixes
    2017-08-21 - Nereu - table processes

"""

import datetime
import json
import os
import paramiko
import pymysql
import re
import sys

dt_begin=datetime.datetime.now()

db=pymysql.connect('localhost','root','','inventory',charset='utf8')

c=db.cursor()

commands={
  'is_vm'       : "/sbin/ip link show | grep -q ' 00:0c:29:' && echo 'YES' || echo 'NO'",
  'version'     : "/bin/cat /etc/system-release || /bin/cat /etc/redhat-release || echo 'Unkown'",
  'uptime'      : '/usr/bin/uptime',
  'cpuinfo'     : '/bin/cat /proc/cpuinfo',
  'cpumodel'    : "/bin/grep 'model name' /proc/cpuinfo",
  'meminfo'     : "/bin/cat /proc/meminfo",
  'hostname'    : '/bin/hostname',
  'arch'        : '/usr/bin/test -e /bin/arch && /bin/arch',
  'ps'          : "/bin/ps -Ao 'pid,uid,ppid,vsize,rss,size,cmd'",
  'sockstat'    : '/bin/cat /proc/net/sockstat',
  'netstat_tcp' : '/bin/netstat -ant',
  'netstat_udp' : '/bin/netstat -anu',
  'lsblk'       : '/usr/bin/test -e /bin/lsblk && /bin/lsblk',
  'users'       : '/bin/cat /etc/passwd',
  'groups'      : '/bin/cat /etc/group',
  'packages'    : '/bin/rpm -qa --queryformat "%{NAME},%{VERSION},%{RELEASE},%{ARCH}\n"',
  'sysctl'      : '/sbin/sysctl -a',
}

hosts=[]

output={}


### Initialize

def Initialize():

  print('\n. Initialize')

  if c.execute('select host_name from host_list order by 1'):
    for h in c.fetchall():
      hosts.append(h[0])
  else:
    print('  Error: table host_list is empty!\n')
    sys.exit(1)

  for h in hosts:
    output[h]=dict()
    for cmd in commands: output[h][cmd]=''

  return

### Extract

def Extract():

  print('\n. Extract')

  ssh = paramiko.SSHClient()

  ssh.set_missing_host_key_policy=paramiko.client.AutoAddPolicy

  ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

  for h in hosts:
    try:
      print('  . %s' % ( h, ) )

      ssh.connect(h, username=os.getlogin(),key_filename=os.path.expanduser('~/.ssh/id_rsa'),timeout=2)

      output[h]['is_up']='YES'
     
      for col,cmd in commands.items():
        try:
          ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
          output[h][col]=''.join(ssh_stdout.readlines()).rstrip()
          #output[h][col]=output[h][col].rstrip()
        except:
          print('    Error: SSH exec(%s) cmd=[%s]' % (h,cmd) )
          output[h][col]=''

      ssh.close()

    except:
      output[h]['is_up']='NO'
      print('    Error: SSH connect(%s)' % ( h ) )
      continue

  return

### Dump_Json

def Dump_Json(fname):
    f=open(fname,'w',encoding='utf-8')
    json.dump(output,f)
    f.close()
    return

### Load_Json

def Load_Json(fname):
    f=open(fname,'r',encoding='utf-8')
    o = json.load(f)
    f.close()
    return o

### Transform

def Transform():

  print('\n. Transform')
  for h in output.keys():
    print('  . %s' % ( h, ) )

    # Meminfo
    if len(output[h]['meminfo']):
      meminfo=[ m.replace(':','').split() for m in output[h]['meminfo'].split('\n') ]
      for i in range(0,len(meminfo)):
        if len(meminfo[i]) == 2:
          meminfo[i].append('')
      output[h]['meminfo']=meminfo

    # Users
    if len(output[h]['users']):
      output[h]['users']=[ u.split(':') for u in output[h]['users'].split('\n') ]

    # Groups
    if len(output[h]['groups']):
      output[h]['groups']=[ g.split(':') for g in output[h]['groups'].split('\n') ] 

    # Packges
    if len(output[h]['packages']):
      output[h]['packages']=[ p.split(',') for p in output[h]['packages'].split('\n') ]

    # Processes
    output[h]['processes']=list()
    for l in output[h]['ps'].split('\n')[1:]:
     ll=re.split('\s+',l.strip())
     cmd=' '.join(ll[6:])
     ll=ll[0:6]
     ll.append(cmd)
     output[h]['processes'].append(ll)

    # Sysctl
    output[h]['kernel_params']=[ re.split('\s*=\s*',l) for l in output[h]['sysctl'].strip().split('\n') if '=' in l ]

    # Tcp
    tcp=[]
    if len(output[h]['netstat_tcp']):
      for l in output[h]['netstat_tcp'].split('\n'):
        f=[ x for x in l.split() ]
        if f[-1]=='LISTEN':
          tcp.append( [ f[3], f[3].split(':')[-1] ] )
    output[h]['tcp']=tcp

    # Udp
    udp=[]
    if len(output[h]['netstat_udp']):
      for l in output[h]['netstat_udp'].split('\n'):
        f=[ x for x in l.split() ]
        if f[0]=='udp':
          udp.append( [ f[3], f[3].split(':')[-1] ] )
    output[h]['udp']=udp

    # Hosts
    distro=output[h]['version'].split(' ')[0]
    v=re.search(r'([0-9\.]+)',output[h]['version'])
    if v:
      if '.' in v.group(0):
        (major,*minor)=v.group(0).split('.')
      else:
        major=v.group(0)
        minor=''
    else:
      ( major, minor ) = ('','')
  
    if len(output[h]['cpumodel']):
      cpumodel=output[h]['cpumodel'].split('\n')
      procs=len(cpumodel)
      cpumodel=cpumodel[0].split(': ')[1]
    else:
      cpumodel=''
      procs=0

    output[h]['hosts']=[ 
      h,
      output[h]['is_up'],
      output[h]['is_vm'],
      distro, 
      output[h]['version'],
      major, 
      minor,
      cpumodel,
      procs,
      output[h]['hostname'],
      output[h]['arch'],
      output[h]['uptime'],
      output[h]['ps'],
      output[h]['sockstat'],
      output[h]['lsblk']
    ]

  return

### Load

def Load():

  print('\n. Load')

  for h in output.keys():
    print('  . %s' % ( h, ) )
    c.execute('insert into hosts values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', output[h]['hosts'] )
    c.executemany('insert into meminfo   values (%s,%s,%s,%s)',            [ [ h ] + m for m in output[h]['meminfo'] ] )
    c.executemany('insert into users     values (%s,%s,%s,%s,%s,%s,%s,%s)',[ [ h ] + u for u in output[h]['users'] ] )
    c.executemany('insert into groups    values (%s,%s,%s,%s,%s)',         [ [ h ] + g for g in output[h]['groups'] ] )
    c.executemany('insert into packages  values (%s,%s,%s,%s,%s)',         [ [ h ] + p for p in output[h]['packages'] ] )
    c.executemany('insert into netstat   values (%s,%s,%s,%s)',            [ [ h, 'tcp' ] + t for t in output[h]['tcp'] ] )
    c.executemany('insert into netstat   values (%s,%s,%s,%s)',            [ [ h, 'udp' ] + u for u in output[h]['udp'] ] )
    c.executemany('insert into processes values (%s,%s,%s,%s,%s,%s,%s,%s)',[ [ h ] + p for p in output[h]['processes'] ] )
    c.executemany('insert into kernel_params values (%s,%s,%s)'           ,[ [ h ] + s for s in output[h]['kernel_params'] ] )

  c.execute('insert into inventory values ( %s, %s )', ( dt_begin, datetime.datetime.now() ) )

  return

###

print('\nInventory %s' % ( '-' * 60 ) )

Initialize()

Extract()

#Dump_Json('inventory_extracted.json')

#Debug
#output=Load_Json('inventory_extracted.json')

Transform()

#Dump_Json('inventory_transformed.json')

Load()

print('\n%s\n' % ( '-' * 70 ) )
