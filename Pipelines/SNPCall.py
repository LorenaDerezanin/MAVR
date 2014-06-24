#/usr/bin/env python
import os
import collections
from Bio import SeqIO


def get_chromosomes_bed(reference, reference_index, mitochondrial_region_name="mt",
                        chrom_out_file="chromosomes.bed", mito_out_file="mt.bed", reference_filetype="fasta"):
    if isinstance(reference, collections.MutableSequence):
        ref = reference
    else:
        ref = [reference]
    record_dict = SeqIO.index_db(reference_index, ref, reference_filetype)
    lengthes_dict = {}

    for record_id in record_dict:
        if record_id == mitochondrial_region_name:
            with open(mito_out_file, "w") as mt_fd:
                mt_fd.write(record_id + "\t1\t" + str(len(record_dict[record_id])) + "\n")
            continue
        lengthes_dict[record_id] = len(record_dict[record_id])

    with open(chrom_out_file, "w") as in_fd:
        for record_id in sorted(list(lengthes_dict.keys())):
            in_fd.write(record_id + "\t1\t" + str(lengthes_dict[record_id]) + "\n")


def alignment_sorting_and_filtering(sample_name, chromosomes_bed_file, mitochondrial_bed_file):
    #-F 4 - skip UNaligned reads
    os.system("samtools view -Sb %s_trimmed.sam | samtools sort - %s_trimmed_sorted" % (sample_name, sample_name))
    os.system("samtools rmdup %s_trimmed_sorted.bam %s_trimmed_sorted_rm_pcr.bam" % (sample_name, sample_name))
    os.system("samtools view -b -F 4 -L %s %s_trimmed_sorted_rm_pcr.bam  > %s_trimmed_sorted_rm_pcr_chrom.bam"
              % (chromosomes_bed_file, sample_name, sample_name))
    os.system("samtools index %s_trimmed_sorted_rm_pcr_chrom.bam" % sample_name)
    os.system("samtools view -b -F 4 -L %s %s_trimmed_sorted_rm_pcr.bam  > %s_trimmed_sorted_rm_pcr_mt.bam"
              % (mitochondrial_bed_file, sample_name, sample_name))
    os.system("samtools index %s_trimmed_sorted_rm_pcr_mt.bam" % sample_name)
    os.system("samtools view -b -f 4  %s_trimmed_sorted_rm_pcr.bam  > %s_trimmed_sorted_rm_pcr_unaligned.bam"
              % (sample_name, sample_name))
    os.system("rm -rf %s_trimmed.sam %s_trimmed_sorted.bam %s_trimmed_sorted_rm_pcr.bam"
              % (sample_name, sample_name, sample_name))
    os.system("qualimap bamqc -bam %s_trimmed_sorted_rm_pcr_mt.bam " % sample_name)
    os.system("qualimap bamqc -bam %s_trimmed_sorted_rm_pcr_chrom.bam " % sample_name)


def get_alignment_without_trim(bowtie2_index,
                              sample_name,
                              forward_reads,
                              chromosomes_bed_file,
                              mitochondrial_bed_file,
                              reverse_reads=None,
                              max_threads=5):

    print("Handling %s sample..." % sample_name)

    if reverse_reads:
        os.system("bowtie2 --very-sensitive --phred33 -p %i -x %s -1 %s -2 %s > %s_trimmed.sam"
                  % (max_threads, bowtie2_index, forward_reads, reverse_reads, sample_name))
    else:
        os.system("bowtie2 --very-sensitive --phred33 -p %i -x %s -U %s > %s_trimmed.sam"
                  % (max_threads, bowtie2_index, forward_reads, sample_name))

    alignment_sorting_and_filtering(sample_name, chromosomes_bed_file, mitochondrial_bed_file)


def get_alignment(bowtie2_index,
                  sample_name,
                  min_length,
                  forward_reads,
                  forward_trim,
                  chromosomes_bed_file,
                  mitochondrial_bed_file,
                  reverse_reads=None,
                  reverse_trim=None,
                  skip_correction=False,
                  max_threads=5,
                  adapter="AGATCGGAAGAGC"):
    #Illumina standard adapter AGATCGGAAGAGC
    #Nextera adapter CTGTCTCTTATACACATCT
    print("Handling %s sample..." % sample_name)
    os.system("mkdir -p trimmed")

    if reverse_reads:
        os.system("trim_galore -a %s  --length %i --phred33 --dont_gzip --clip_R1 %i --clip_R2 %i --paired -q 20 -t -o trimmed %s %s"
                  % (adapter, min_length, forward_trim, reverse_trim, forward_reads, reverse_reads))
        os.chdir("trimmed")
        os.system("fastqc -t 2 --nogroup %s_1_val_1.fq %s_2_val_2.fq" % (sample_name, sample_name))

        left_r = "spades/corrected/%s_1_val_1.00.0_0.cor.fastq" % sample_name
        right_r = "spades/corrected/%s_2_val_2.00.0_0.cor.fastq" % sample_name

        if skip_correction:
            left_r = "%s_1_val_1.fq" % sample_name
            right_r = "%s_2_val_2.fq" % sample_name
        else:
            os.system("spades.py -t %i --only-error-correction --disable-gzip-output -1 %s_1_val_1.fq -2 %s_2_val_2.fq -o spades"
                      % (max_threads,sample_name, sample_name))

        os.system("bowtie2 --phred33 -p %i -x %s -1 %s -2 %s > %s_trimmed.sam"
                  % (max_threads, bowtie2_index, left_r, right_r, sample_name))
    else:
        os.system("trim_galore  --length %i --phred33 --dont_gzip --clip_R1 %i -q 20 -t -o trimmed %s"
                  % (min_length, forward_trim, forward_reads))
        os.chdir("trimmed")
        os.system("fastqc -t 2 --nogroup %s_trimmed.fq" % (sample_name))

        unpaired_r = "spades/corrected/%s_trimmed.00.0_0.cor.fastq" % sample_name
        if skip_correction:
            unpaired_r = "%s_trimmed.fq" % sample_name
        else:
            os.system("spades.py -t %i --only-error-correction --disable-gzip-output -s %s_trimmed.fq -o spades"
                      % (max_threads, sample_name))

        os.system("bowtie2 --phred33 -p %i -x %s -U %s > %s_trimmed.sam"
                  % (max_threads, bowtie2_index, unpaired_r, sample_name))

    alignment_sorting_and_filtering(sample_name, chromosomes_bed_file, mitochondrial_bed_file)


def get_coverage_thresholds(coverage_dist_file, one_side_base_threshold=0.025, minimum_threshold=5):
    #coverage_dist_file - is file like qualimap coverage_histogram.txt derived from alignment statistics

    fd = open(coverage_dist_file, "r")
    fd.readline()
    fd.readline()
    coverage = []
    frequency = []
    for line in fd:
        striped = line.strip()
        if striped == "":
            break
        #print (line)
        striped = striped.split("\t")
        coverage.append(float(striped[0]))
        frequency.append(float(striped[1]))
    fd.close()
    number_of_basses = sum(frequency)
    low_tr = int(one_side_base_threshold * float(number_of_basses))
    high_tr = int((1.00 - one_side_base_threshold) * float(number_of_basses))
    i = 0
    freq = 0
    while freq < low_tr:
        freq += frequency[i]
        i += 1
    min_coverage = coverage[i]
    while freq < high_tr:
        freq += frequency[i]
        i += 1
    max_coverage = coverage[i]
    return int(max(min_coverage, minimum_threshold)), int(max_coverage)


def snp_call(alignment,
             sample_name,
             reference_file,
             min_coverage,
             max_coverage,
             alignment_quality=40,
             snp_quality=100):

    os.system("samtools mpileup  -q %i -ugf %s %s | bcftools view -cvgN - > %s_raw.vcf"
              % (alignment_quality, reference_file, alignment,  sample_name))
    os.system("cat '%s_raw.vcf' | vcfutils.pl varFilter -D %i -d %i > %s.vcf"
              % (sample_name, max_coverage, min_coverage, sample_name))

    os.system("vcftools --vcf %s.vcf --out %s_filtered --remove-indels --recode --recode-INFO-all --minQ %i"
              % (sample_name, sample_name, snp_quality))


def snp_call_pipeline(bowtie2_index,
                      sample_name,
                      min_length,
                      reference_file,
                      reference_index,
                      right_reads,
                      right_trim,
                      left_reads=None,
                      left_trim=None,
                      skip_correction=False,
                      coverage_one_side_base_threshold=0.025,
                      coverage_minimum_threshold=5,
                      alignment_quality=40,
                      snp_quality=40,
                      max_threads=5,
                      chromosomes_bed_file="chromosomes.bed",
                      mitochondrial_bed_file="mt.bed",
                      mitochondrial_region_name="mt"):

    get_chromosomes_bed(reference, reference_index, mitochondrial_region_name=mitochondrial_region_name,
                        chrom_out_file=chromosomes_bed_file, mito_out_file=mitochondrial_bed_file,
                        reference_filetype="fasta")

    get_alignment(bowtie2_index, sample_name, min_length, right_reads,
                  right_trim, chromosomes_bed_file,
                  mitochondrial_bed_file, left_reads=left_reads, left_trim=left_trim,
                  skip_correction=skip_correction, max_threads=max_threads)

    for region in ["mt", "chrom"]:
        min_coverage, max_coverage = \
            get_coverage_thresholds("%s_trimmed_sorted_rm_pcr_%s_stats/raw_data/coverage_histogram.txt"
                                    % (sample_name, region),
                                    one_side_base_threshold=coverage_one_side_base_threshold,
                                    minimum_threshold=coverage_minimum_threshold)
        snp_call("%s_trimmed_sorted_rm_pcr_%s.bam" % (sample_name, region),
                 sample_name + "_" + region,
                 reference_file,
                 min_coverage,
                 max_coverage,
                 alignment_quality=alignment_quality,
                 snp_quality=snp_quality)


if __name__ == "__main__":
    sample_name = "210-L1"
    workdir = "/run/media/mahajrod/Data/data/LAN210/all/%s/trimmed" % sample_name
    os.chdir(workdir)
    reference = "/home/mahajrod/genetics/desaminases/data/LAN210_v0.6m/LAN210_v0.6m.fasta"
    reference_index = "/home/mahajrod/genetics/desaminases/data/LAN210_v0.6m/LAN210_v0.6m.idx"
    get_chromosomes_bed(reference, reference_index, mitochondrial_region_name="mt",
                        chrom_out_file="chromosomes.bed", mito_out_file="mt.bed", reference_filetype="fasta")
    alignment_sorting_and_filtering(sample_name, "chromosomes.bed", "mt.bed")