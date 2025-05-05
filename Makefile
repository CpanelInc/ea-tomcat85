OBS_PROJECT := EA4
OBS_PACKAGE := ea-tomcat85
DISABLE_BUILD += repository=CentOS_8 repository=CentOS_9 repository=Almalinux_10
include $(EATOOLS_BUILD_DIR)obs.mk
