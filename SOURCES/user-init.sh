. /etc/rc.d/init.d/functions
. $HOME/ea-tomcat85/bin/setenv.sh
 
tomcat_pid() {
  if [ -n "$CATALINA_PID" ] && [ -e $CATALINA_PID ]; then
      cat $CATALINA_PID
  fi
}

ERROR=0
case $1 in
    start)
        pid=$(tomcat_pid)
        if [ -n "$pid" ] && [ ps --pid $pid 2>&1 1>/dev/null ]; then
            echo -e "\e[00;33mTomcat is already running (pid: $pid)\e[00m"
            ERROR=1
        else
            /opt/cpanel/ea-tomcat85/bin/user-startup.sh
        fi
        ;;
    stop)
        pid=$(tomcat_pid)
        if [ ! -n "$pid" ] || [ ! ps --pid $pid 2>&1 1>/dev/null ]; then
            echo -e "\e[00;31mTomcat is already shutdown\e[00m"
            ERROR=1
        else
            /opt/cpanel/ea-tomcat85/bin/user-shutdown.sh
        fi
        ;;
    restart|force-reload)
        pid=$(tomcat_pid)
        if [ -n "$pid" && ps --pid $pid 2>&1 1>/dev/null ]; then
            /opt/cpanel/ea-tomcat85/bin/user-shutdown.sh
        fi

        /opt/cpanel/ea-tomcat85/bin/user-startup.sh
        ;;
    status|fullstatus)
        pid=$(tomcat_pid)
        if [ -f "$CATALINA_PID" ]; then
            if ps --pid $pid 2>&1 1>/dev/null; then
                echo -e "\e[00;32mTomcat is running!\e[00m"
                ERROR=0
            else
                echo "$CATALINA_PID found, but $pid is not running"
                ERROR=4
            fi
        else
            echo -e "\e[00;31mTomcat is currently not running.\e[00m"
            ERROR=3
        fi
        ;; 
    *)
        echo $"Usage: $0 {start|stop|restart|status|fullstatus}"
        ERROR=2
esac
 
exit $ERROR
