#!/usr/bin/env bash
#SBATCH --array=1-890%890
#SBATCH --time=100:00:00          # Run time in hh:mm:ss
#SBATCH --mem-per-cpu=8192       # Minimum memory required per CPU (in megabytes)
#SBATCH --job-name=leohu
#SBATCH --error=/work/pavlov/okochenova/genomes_workdir/leopard_cat/logs/exonerate_cat.%A_%a.err
#SBATCH --output=/work/pavlov/okochenova/genomes_workdir/leopard_cat/logs/exonerate_cat.%A_%a.out

module load exonerate/2.2
source /work/pavlov/okochenova/profile

SPLITED_PEP_DIR="/work/pavlov/okochenova/genomes/human/pep/homo_sapiens_no_selenocytein/"

PEP_FILE="${SPLITED_PEP_DIR}homo_sapiens_no_selenocytein_pep_${SLURM_ARRAY_TASK_ID}.fasta"

LEOPARD_CAT_GENOME="/work/pavlov/okochenova/genomes/leopard_cat/final.assembly.fasta"

EXONERATE_OUTPUT_DIR="/work/pavlov/okochenova/genomes_workdir/leopard_cat/exonerate_human_pep/"
mkdir -p ${EXONERATE_OUTPUT_DIR}
EXONERATE_OUTPUT_FILE="${EXONERATE_OUTPUT_DIR}/exonerate_human_pep_${SLURM_ARRAY_TASK_ID}.out"

exonerate  --model protein2genome --showalignment --showquerygff --showtargetgff \
           -n 10 -q ${PEP_FILE} -t ${LEOPARD_CAT_GENOME} > ${EXONERATE_OUTPUT_FILE}

