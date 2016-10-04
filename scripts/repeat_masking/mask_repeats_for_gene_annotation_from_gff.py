#!/usr/bin/env python
__author__ = 'Sergei F. Kliver'

import argparse

from Tools.RepeatMasking import RepeatMasker
from Tools.Bedtools import MaskFasta

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input_file", action="store", dest="input", required=True,
                    help="Input file with RepeatMasker output")
parser.add_argument("-g", "--genome_fasta", action="store", dest="genome_fasta", required=True,
                    help="Fasta file with genome to mask")
parser.add_argument("-p", "--output_prefix", action="store", dest="output_prefix", required=True,
                    help="Prefix for output files")

args = parser.parse_args()

output_gff = "%s.gff" % args.output_prefix
repeat_classes = "%s.repeat_classes" % args.output_prefix
repeat_families = "%s.repeat_families" % args.output_prefix
extracted_gff = "%s.selected_repeat_classes.gff" % args.output_prefix
output_fasta = "%s.selected_repeat_classes.masked.fasta"

RepeatMasker.convert_rm_out_to_gff(args.input, output_gff, repeat_classes, repeat_families)

RepeatMasker.extract_repeats_used_for_gene_annotation(output_gff, extracted_gff)
MaskFasta.mask(args.genome_fasta, output_fasta, extracted_gff, softmasking=True)
