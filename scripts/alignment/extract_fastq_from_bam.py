#!/usr/bin/env python
__author__ = 'Sergei F. Kliver'

import argparse
from os import path

from Routines import FileRoutines
from Tools.Samtools import SamtoolsV1
from Tools.Bedtools import BamToFastq

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", action="store", dest="input", required=True,
                    help="Input bam file")
parser.add_argument("-t", "--threads", action="store", dest="threads", type=int, default=1,
                    help="Number of threads to use. Default - 1")
parser.add_argument("-p", "--prepare_bam", action="store_true", dest="prepare_bam",
                    help="Prepare bam for reads extraction(filter out supplementary and not primary alignments"
                         "and sort by name)")
parser.add_argument("-e", "--prepared_bam", action="store", dest="prepared_bam",
                    help="File to write sorted bam file. Required if -p/--prepare_bam option is set")
parser.add_argument("-d", "--temp_dir", action="store", dest="temp_dir",
                    help="Directory to use for temporary files. Required if -p/--prepare_bam option is set")
parser.add_argument("-o", "--out_prefix", action="store", dest="out_prefix", required=True,
                    help="Prefix of output fastq files")
parser.add_argument("-s", "--single_ends", action="store_false", dest="paired", default=True,
                    help="Reads are SE")
parser.add_argument("-m", "--max_memory_per_thread", action="store", dest="max_memory_per_thread", default="1G",
                    help="Maximum memory per thread. Default - 1G")
args = parser.parse_args()

if args.sort_by_name and ((not args.sorted_bam) or (not args.temp_dir)):
    raise ValueError("Options -e/--prepared_bam and -m/--temp_dir must be set if -p/--prepare_bam option is used")

SamtoolsV1.threads = args.threads

if args.prepare_bam:
    FileRoutines.save_mkdir(FileRoutines.check_path(args.temp_dir))
    SamtoolsV1.prepare_bam_for_read_extraction(args.input, args.prepared_bam, temp_file_prefix=args.temp_dir,
                                               max_memory_per_thread=args.max_memory_per_thread)

if args.paired:
    left_fastq = "%s_1.fastq" % args.out_prefix
    right_fastq = "%s_2.fastq" % args.out_prefix
else:
    left_fastq = "%s.fastq" % args.out_prefix
    right_fastq = None

BamToFastq.convert(args.prepared_bam if args.prepare_bam else args.input, left_fastq, out_right_fastq=right_fastq)


