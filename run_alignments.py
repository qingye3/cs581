#! /usr/bin/env python
#################################################################################
#     File Name           :     run_alignments.py
#     Created By          :     qing
#     Creation Date       :     [2017-04-20 06:41]
#     Last Modified       :     [2017-05-01 20:48]
#     Description         :      
#################################################################################
from __future__ import print_function
import os
import subprocess
import schedule
import cPickle
import shutil

N_PROCESSES = 32
PASTA = "/data/work/qing/software/pasta/run_pasta.py"
BALIPHY = "/data/work/qing/software/bali-phy-2.3.8/bin/bali-phy"

def parse_alignment(alignment_string):
    ret = dict()
    for line in alignment_string.split(">"):
        if line:
            line = line.split('\n')
            id = line[0]
            seq = "".join(line[1:])
            seq = seq.replace('.', '-')
            ret[id] = seq
    return ret

def run_mafft_batch(input_files):
    return list(schedule.schedule(run_mafft, input_files, N_PROCESSES))

def run_mafft(input_file):
    with open(os.devnull, 'w') as devnull:
        output = subprocess.check_output(["mafft", input_file], stderr=devnull)
    ret = parse_alignment(output)
    return ret


def mkdir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

def run_pasta(input_file, output_dir):
    input_file = os.path.abspath(input_file)
    mkdir_if_not_exists(output_dir)
    with open(os.devnull, 'w') as devnull:
        output = subprocess.check_output(["python", PASTA, "--input", input_file, "--datatype", "Protein", "-o", output_dir]).split(">")
    for f in os.listdir(output_dir):
        f = os.path.join(output_dir, f)
        if not f.endswith(".aln"):
            continue
        with open(f) as f_in:
            alignment_string = f_in.read()
        return parse_alignment(alignment_string)

def run_pasta_worker(args):
    input_file, output_dir = args
    return run_pasta(input_file, output_dir)

def run_pasta_batch(input_files, output_base="../result/pasta_output"):
    mkdir_if_not_exists(output_base)
    args = list()
    for f in input_files:
        args.append((f, os.path.join(output_base, os.path.basename(f))))
    return list(schedule.schedule(run_pasta_worker, args, N_PROCESSES))

def run_bali_phy(input_file, output_dir, iterations=100000):
    input_file = os.path.abspath(input_file)
    mkdir_if_not_exists(output_dir)
    shutil.copy(input_file, output_dir)
    output = subprocess.check_output([BALIPHY, input_file, '--iterations', str(iterations)], cwd=output_dir)

def seek_to_last_iter(file_descriptor):
    location = file_descriptor.tell()
    n_iterations = None
    for line in iter(file_descriptor.readline, ''):
        if line.startswith("iterations = "):
            n_iterations = int(line.split('=')[1])
            location = file_descriptor.tell()
    file_descriptor.seek(location)
    return n_iterations

def seek_to_iter(file_descriptor, iterations):
    for line in file_descriptor:
        if line.startswith("iterations = %d"%iterations):
            return

def parse_bali_result(filename, iterations=None):
    if filename is None or not os.path.exists(filename):
        return None

    with open(filename) as fin:
        n_iterations = None
        try:
            if iterations is None:
                n_iterations = seek_to_last_iter(fin)
            else:
                seek_to_iter(fin, iterations)
            next(fin)
        except StopIteration:
            return None
        text = []
        for line in fin:
            text.append(line.strip())
        text = "\n".join(text)
    return parse_alignment(text), n_iterations

def run_bali_phy_worker(args):
    input_file, output_dir = args
    return run_bali_phy(input_file, output_dir)

def run_bali_batch(input_files, output_base="../result/bali_output"):
    mkdir_if_not_exists(output_base)
    args = list()
    for f in input_files:
        args.append((f, os.path.join(output_base, os.path.basename(f))))
    return list(schedule.schedule(run_bali_phy_worker, args, N_PROCESSES))

def find_bali_output(seq_id, bali_output):
    folders = []
    for folder in os.listdir(os.path.join(bali_output, seq_id)):
        if folder.startswith(seq_id) and folder != seq_id:
            folders.append(folder)
    folders = sorted(folders, reverse=True, key=lambda x: int(x.split('-')[-1]))
    return os.path.join(bali_output, seq_id, folders[-1], 'C1.P1.fastas')

def combine_bali_result(seq_ids, bali_output, iterations=None):
    result = []
    for seq_id in seq_ids:
        try:
            output = find_bali_output(seq_id, bali_output)
        except OSError:
            output = None
        result.append(parse_bali_result(output, iterations))
    return result

def combine_ground_truth(ids, ground_truth_dir):
    result = []
    for id in ids:
        with open(os.path.join(ground_truth_dir, id)) as fin:
            result.append(parse_alignment(fin.read()))
    return result


if __name__ == "__main__":
    input_files = []
    with open("../data/bench1.0/bali3pdb/info/ids.txt") as fin:
        for line in fin:
            if line.strip():
                input_files.append(os.path.join("../data/bench1.0/bali3pdb/in", line.strip()))
    # mafft_result=run_mafft_batch(input_files)
    # with open("../result/mafft.pickle", "w") as f_out:
    #     cPickle.dump(mafft_result, f_out)

    # pasta_result=run_pasta_batch(input_files)
    # with open("../result/pasta.pickle", "w") as f_out:
    #     cPickle.dump(pasta_result, f_out)

    baliphy_result = run_bali_batch(input_files, output_base="../result/bali_output_5000")
        
    #  ids = []
    #  with open("../data/bench1.0/bali3pdb/info/ids.txt") as fin:
    #      for line in fin:
    #          ids.append(line.strip())
    #  baliphy_result = combine_bali_result(ids, '../result/bali_output_24h')
    #  with open("../result/baliphy_24h_with_iterations.pickle", "w") as f_out:
    #      cPickle.dump(baliphy_result, f_out)

    # ground_truth = combine_ground_truth(ids, '../data/bench1.0/bali3pdb/ref')
    # with open("../result/ground_truth.pickle", "w") as f_out:
    #     cPickle.dump(ground_truth, f_out)
