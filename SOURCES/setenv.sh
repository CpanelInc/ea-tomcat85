export CATALINA_OPTS="$CATALINA_OPTS -server -Dfile.encoding=UTF-8 -Xms128m -Xmx6248m"
export CATALINA_PID="/var/run/catalina.pid"
if [ -e "/usr/lib/jvm/jre-1.8.0-openjdk.x86_64" ]; then
   export JAVA_HOME="/usr/lib/jvm/jre-1.8.0-openjdk.x86_64"
else
   export JAVA_HOME="/usr/lib/jvm/jre-1.8.0-openjdk"
fi

