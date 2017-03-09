#!/bin/bash
source /home/hadoop/.bash_profile
createRunId(){
    local date=$(date +%Y%m%d%H%M%S)
    local rand=$(cat /dev/urandom | tr -cd [:alnum:] | head -c 4)
    echo $date"_"$rand
}

lock(){
    local lockFile=${LOG_DIR}/${1}.lock
    [ -f ${lockFile} ] && echo "Lock already exists, exiting" && exit 6
    touch ${lockFile}
    if [ "$?" != "0" ];then
        echo "Failed to acquire lock: ${lockFile}" && exit 7
    fi
}

unlock(){
    local lockFile=${LOG_DIR}/${1}.lock
    [ ! -f ${lockFile} ] && return 1
    rm -f ${lockFile}
    if [ "$?" != "0" ];then
        echo "Failed to release lock: ${lockFile}"
        exit 8
    fi
}

readIterationNumber(){
    local scriptPath=${1}
    local checkpointPath=${LOG_DIR}/${1}.ckp
    if [ -f ${checkpointPath} ];then
        cat ${checkpointPath}
    else
        echo "0"
    fi
}

writeIterationNumber(){
    local scriptPath=${1}
    local iterationNumber=${2}
    local checkpointPath=${LOG_DIR}/${1}.ckp
    echo ${iterationNumber}>${checkpointPath}
}

runPigScripts(){
    local files=$@
    local runId=`createRunId`
    if [ "x${PIG_HOME}" == "x" ]; then
        echo "PIG_HOME not defined in configuration file"
        exit 5
    fi
    for file in ${files}
    do
        local logFilePrefix=${LOG_DIR}/${runId}.$(basename ${file})
        local iterationNumber=$(readIterationNumber $(basename ${file}))
        if [ -f ${file} ];then
	    echo "Logs are written into ${logFilePrefix}.out and ${logFilePrefix}.err"
            ${PIG_HOME}/bin/pig -param iterationNumber=${iterationNumber} ${file} 1>>${logFilePrefix}.out 2>>${logFilePrefix}.err
            if [ "$?" == "0" ];then
                writeIterationNumber $(basename ${file}) $((${iterationNumber}+1))
                echo "Executed ${file} successfully!";
	    else
                echo "Executed ${file} with errors, exit code: $?";
            fi
        else
            echo "${file} doesn't exist >>${logFilePrefix}.err"
        fi
    done
}

runHiveScripts(){
    local files=$@
    local runId=`createRunId`
    if [ "x${HIVE_HOME}" == "x" ]; then
        echo "HIVE_HOME not defined in configuration file"
        exit 5
    fi
    for file in ${files}
    do
        local logFilePrefix=${LOG_DIR}/${runId}.$(basename ${file})
        local iterationNumber=$(readIterationNumber $(basename ${file}))
        if [ -f ${file} ];then
	    echo "Logs are written into ${logFilePrefix}.out and ${logFilePrefix}.err"
            ${HIVE_HOME}/bin/hive -hiveconf kinesis.checkpoint.iteration.no=${iterationNumber} -f ${file} 1>>${logFilePrefix}.out 2>>${logFilePrefix}.err
            if [ "$?" == "0" ];then
                writeIterationNumber $(basename ${file}) $((${iterationNumber}+1))
                echo "Executed ${file} successfully!";
	    else
                echo "Executed ${file} with errors, exit code: $?";
            fi
        else
            echo "${file} doesn't exist >>${logFilePrefix}.err"
        fi
    done
}

showConfig(){
    echo ""
    echo "SCRIPT_TYPE=${SCRIPT_TYPE}"
    echo "SCRIPTS=${SCRIPTS}"
    echo "LOG_DIR=${LOG_DIR}"
    echo "JAVA_HOME=${JAVA_HOME}"
    echo "HADOOP_HOME=${HADOOP_HOME}"
    [ "x${HIVE_HOME}" != "x" ] && echo "HIVE_HOME=${HIVE_HOME}"
    [ "x${PIG_HOME}" != "x" ] && echo "PIG_HOME=${PIG_HOME}"
    echo ""
}

echo "$(basename $0) ran at: $(date +%Y-%m-%dT%H:%M:%S)"
[ "x${1}" != "x" ] && [ -f "${1}" ] && CONFIG=${1}

if [ "x${CONFIG}" == "x" ];then
    echo "Invalid configuration file: ${1}"
    exit 1
fi

source ${CONFIG}
if [ "x${SCRIPT_TYPE}" == "x" ] || [ "x${SCRIPTS}" == "x" ] || 
    [ "x${LOG_DIR}" == "x" ] || [ "x${JAVA_HOME}" == "x" ]  ||
    [ "x${HADOOP_HOME}" == "x" ];then
    echo "Invalid configuration in configuration file: ${CONFIG}"
    showConfig
    exit 2
fi

if [ ! -d ${LOG_DIR} ];then
    showConfig
    echo "${LOG_DIR} doesn't exist"
    exit 9
fi

lock `basename ${CONFIG}`
case ${SCRIPT_TYPE} in
    "pig"|"PIG")
        runPigScripts ${SCRIPTS}
        ;;
    "hive"|"HIVE")
        runHiveScripts ${SCRIPTS}
        ;;
    *) 
        echo "Invalid script type: ${SCRIPT_TYPE}"
        exit 3
        ;;
esac
unlock `basename ${CONFIG}`

