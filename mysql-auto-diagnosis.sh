#!/bin/sh

##################
#
# SETTINGS
# PLEASE SET VARIABLES BELOW
#
# RDSUSER requires at least a PROCESS PRIVILEGE
#
# It's advised to call this script as unpriviled user from cron. Please set proper permissions for STAT_DIR to allow that user to write files in that directory


#################
STAT_DIR="/tmp/reports-mysql/"
host=$1
echo ${WORKSPACE}

##################
# SCRIPT
#################
DATE=`date '+%Y-%m-%d-%H%M%S'`
if [ $? -eq 0 ]; then

	echo "================FULL PROCESS LIST================" > ${STAT_DIR}/${host}.diagnosis.txt
  echo "${host}.${DATE}" \ >> ${STAT_DIR}/${host}.diagnosis.txt
	mysql --login-path=${host} -e 'SHOW FULL PROCESSLIST;' >> ${STAT_DIR}/${host}.diagnosis.txt
	echo '================INNODB STATUS================'  >> ${STAT_DIR}/${host}.diagnosis.txt
	mysql --login-path=${host} -e 'SHOW ENGINE INNODB STATUS\G' >> ${STAT_DIR}/${host}.diagnosis.txt
	echo "================INNODB MUTEX================" >> ${STAT_DIR}/${host}.diagnosis.txt
	mysql --login-path=${host} -e 'SHOW ENGINE INNODB MUTEX;' >> ${STAT_DIR}/${host}.diagnosis.txt
	echo "================GLOBAL STATUS================" >> ${STAT_DIR}/${host}.diagnosis.txt
	mysql --login-path=${host} -e 'SHOW GLOBAL STATUS;' >> ${STAT_DIR}/${host}.diagnosis.txt
	echo "================VARIABLES================" >> ${STAT_DIR}/${host}.diagnosis.txt
	mysql --login-path=${host} -e 'SHOW VARIABLES;' >> ${STAT_DIR}/${host}.diagnosis.txt
	echo "================GLOBAL VARIABLES================" >> ${STAT_DIR}/${host}.diagnosis.txt
	mysql --login-path=${host} -e 'SHOW GLOBAL VARIABLES;' >> ${STAT_DIR}/${host}.diagnosis.txt
	echo "================LOCKS================" >> ${STAT_DIR}/${host}.diagnosis.txt
	mysql --login-path=${host} -e 'SELECT trx_id, trx_state, trx_wait_started, trx_requested_lock_id, time_to_sec(timediff(now(),trx_started)) AS cq, lock_type, lock_table, lock_index, lock_data FROM information_schema.innodb_trx LEFT JOIN information_schema.innodb_locks ON trx_requested_lock_id=lock_id; ' >> ${STAT_DIR}/${host}.diagnosis.txt

else
	echo "DIRECTORY CREATING ERROR"
fi
