FROM jasonrivers/nagios:latest

ARG PG_HOST
ARG PG_PORT
ARG PG_NAGIOS_USER

# Install check_pgactivity plugin
RUN apt-get update && apt-get install -y check-pgactivity postgresql-client

# Render commands.cfg
COPY etc/objects/commands.cfg.template ${NAGIOS_HOME}/etc/objects/commands.cfg.template
RUN envsubst '$PG_HOST,$PG_PORT,$PG_NAGIOS_USER' < ${NAGIOS_HOME}/etc/objects/commands.cfg.template >> ${NAGIOS_HOME}/etc/objects/commands.cfg
