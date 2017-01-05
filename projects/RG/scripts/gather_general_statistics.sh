#!/usr/bin/env bash
#-----------------Environment variables-----------------
WORKDIR=/home/genomerussia/main/
FASTQ_DIR=${WORKDIR}/fastq/
ANALYSIS_DIR=${WORKDIR}/analysis/
ALIGNMENT_DIR=${WORKDIR}/analysis/alignment/

RAW_READS_DIR=${FASTQ_DIR}/raw/
UNPACKED_READS_DIR=${FASTQ_DIR}/unpacked/
FILTERED_READS_DIR=${FASTQ_DIR}/filtered/

ALIGNMENT_BAM_DIR=${ALIGNMENT_DIR}/bam/
ALIGNMENT_LOG_DIR=${ALIGNMENT_DIR}/log/
ALIGNMENT_TMP_DIR=${ALIGNMENT_DIR}/tmp/

JF_DB_DIR=${ANALYSIS_DIR}/jf/

STAT_DIR=${ANALYSIS_DIR}/stat/
ADAPTERS_STAT_DIR=${STAT_DIR}/adapters/
FASTQC_STAT_DIR=${STAT_DIR}/fastqc/
FILTERING_STAT_DIR=${STAT_DIR}/filtering/
KMER_STAT_DIR=${STAT_DIR}/kmer/
GENERAL_STAT_DIR=${STAT_DIR}/general/

TOOLS_DIR=/home/genomerussia/tools/
MAVR_SCRIPTS_DIR=${TOOLS_DIR}/MAVR/scripts/
FACUT_BIN_DIR=${TOOLS_DIR}/Facut/bin/
FASTQC_DIR=${TOOLS_DIR}/FastQC/
COOCKIECUTTER_SRC_DIR=${TOOLS_DIR}/Cookiecutter/src/

ADAPTER_KMER_FILE=${TOOLS_DIR}/service_sequences/trueseq_adapters_with_rev_com_23_mer.kmer
#PYTHONPATH=${PYTHONPATH}:/home/genomerussia/tools/MAVR
#export PYTONPATH
#-------------------------------------------------------

#----------------------Settings-------------------------
THREAD_NUMBER=60
KMER_SIZE=23
MEMORY=30G
PHRED_SCORE_TYPE=phred33
READ_NAME_TYPE=illumina
QUALITY_THRESHOLD=20
#-------------------------------------------------------

#--------------------------Files------------------------
FILTERING_GENERAL_STAT_FILE="${GENERAL_STAT_DIR}filtering.stat"
ADAPTERS_GENERAL_STAT_FILE="${GENERAL_STAT_DIR}adapters.stat"
KMER_GENERAL_STAT_FILE="${GENERAL_STAT_DIR}kmer.stat"
#-------------------------------------------------------

#--------------------File suffixes----------------------
FILTERING_STAT_FILE_SUFFIX=".filtering.stat"
ADAPTERS_STAT_FILE_SUFFIX=".adapters.stat"
KMER_STAT_FILE_SUFFIX="_${KMER_SIZE}_mer_histogram.histo.stats"
#-------------------------------------------------------
SAMPLE_LIST=($@)
FILTERING_STAT_FILE_LIST=()
ADAPTERS_STAT_FILE_LIST=()
KMER_STAT_FILE_LIST=()
SAMPLE_STRING=`echo $@ | tr " " ,`  # replace space by comma

#echo ${SAMPLE_LIST[@]}

for SAMPLE in ${SAMPLE_LIST[@]};
    do
    SAMPLE_GROUP=`echo ${SAMPLE} | cut -c1-4`

    FILTERING_SAMPLE_DIR="${FILTERING_STAT_DIR}/${SAMPLE_GROUP}/${SAMPLE}/"
    ADAPTERS_SAMPLE_DIR="${ADAPTERS_STAT_DIR}/${SAMPLE_GROUP}/${SAMPLE}/"
    KMER_SAMPLE_DIR="${KMER_STAT_DIR}/${SAMPLE_GROUP}/${SAMPLE}/"

    FILTERING_FILENAME="${FILTERING_SAMPLE_DIR}${SAMPLE}${FILTERING_STAT_FILE_SUFFIX}"
    ADAPTERS_FILENAME="${ADAPTERS_SAMPLE_DIR}${SAMPLE}${ADAPTERS_STAT_FILE_SUFFIX}"
    KMER_FILENAME="${KMER_SAMPLE_DIR}${SAMPLE}${KMER_STAT_FILE_SUFFIX}"

    FILTERING_STAT_FILE_LIST+=(${FILTERING_FILENAME})
    ADAPTERS_STAT_FILE_LIST+=(${ADAPTERS_FILENAME})
    KMER_STAT_FILE_LIST+=(${KMER_FILENAME})
    #echo ${FILTERING_STAT_FILE_LIST[@]}
    done
#echo ${FILTERING_STAT_FILE_LIST[@]}
FILTERING_STAT_FILE_STRING=`echo ${FILTERING_STAT_FILE_LIST[@]} | tr " " ,`
ADAPTERS_STAT_FILE_STRING=`echo ${ADAPTERS_STAT_FILE_LIST[@]} | tr " " ,`
KMER_STAT_FILE_STRING=`echo ${KMER_STAT_FILE_LIST[@]} | tr " " ,`

FILTERING_GENERAL_STAT_STRING="${MAVR_SCRIPTS_DIR}/filter/get_general_stats_from_facut_reports.py -i ${FILTERING_STAT_FILE_STRING} -s ${SAMPLE_STRING} -o ${FILTERING_GENERAL_STAT_FILE}"
echo "${FILTERING_GENERAL_STAT_STRING}"
${FILTERING_GENERAL_STAT_STRING}

ADAPTERS_GENERAL_STAT_STRING="${MAVR_SCRIPTS_DIR}/filter/get_general_stats_from_coockiecutter_reports.py -i ${ADAPTERS_STAT_FILE_STRING} -s ${SAMPLE_STRING} -o ${ADAPTERS_GENERAL_STAT_FILE}"
echo "${ADAPTERS_GENERAL_STAT_STRING}"
${ADAPTERS_GENERAL_STAT_STRING}

KMER_GENERAL_STAT_STRING="${MAVR_SCRIPTS_DIR}/kmer/get_general_stats_from_krater_reports.py -i ${KMER_STAT_FILE_STRING} -s ${SAMPLE_STRING} -o ${KMER_GENERAL_STAT_FILE}"
echo "${KMER_GENERAL_STAT_STRING}"
${KMER_GENERAL_STAT_STRING}
