#! /bin/bash

export myusername=mdipierro
export port=8000
export web2py_path=/home/mdipierro/web2py
if ! ` netcat -z localhost $port `
then pgrep -flu $myusername web2py | cut -d -f1 | xargs kill > /dev/null  2>&1
     chown $myusername: /var/log/web2py.log
     su $myusername -c 'cd $web2py_path && ./web2py.py -p $port -a password 2>&1 >> /var/log/web2py.log'
     sleep 3
     if ` netcat -z localhost $port `
         then echo "web2py was restarted"
         else echo "web2py could not be started!"
     fi
fi
