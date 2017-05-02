#! /usr/bin/env python
#################################################################################
#     File Name           :     run_assessment.py
#     Created By          :     qing
#     Creation Date       :     [2017-04-24 12:34]
#     Last Modified       :     [2017-04-25 19:57]
#     Description         :      
#################################################################################
from __future__ import print_function
import numpy as np

def label(sequence):
    ret = []
    curr_label = 0
    for char in sequence:
        if char == '-':
            ret.append(-1)
        else:
            if char.islower():
                ret.append(-1)
            else:
                ret.append(curr_label)
            curr_label += 1
    return ret

def n_correctly_aligned(struct_align, seq_align):
    struct_a, struct_b = [label(seq) for seq in struct_align]
    seq_a, seq_b = [label(seq) for seq in seq_align]
    truth = {k:v for k, v in zip(struct_a, struct_b)}
    n_correct = 0
    for pos_a, pos_b in zip(seq_a, seq_b):
        if pos_a == -1 or pos_b == -1:
            continue
        if pos_a in truth and pos_b == truth[pos_a]:
            n_correct += 1
    return n_correct

def n_aligned(alignment):
    aligned = np.ones(len(alignment[0]), dtype='int')
    for seq in alignment:
        for i, code in enumerate(seq):
            if code == '-' or code.islower():
                aligned[i] = 0
    return np.sum(aligned)

def developer_score(struct_align, seq_align):
    return n_correctly_aligned(struct_align, seq_align) / float(n_aligned(struct_align))

def modeller_score(struct_align, seq_align):
    return n_correctly_aligned(struct_align, seq_align) / float(n_aligned(seq_align))

if __name__ == "__main__":
    struct_align = ['IE-YFXGPV-E-EVX',
                    'VEXFF-SPAXLQ--G']
    seq_align = ['IE-YFX-GP-V-EEVX',
                 'VEX-FF-SPAXLQG--' ]
    assert n_aligned(struct_align) == 9
    assert n_correctly_aligned(struct_align, seq_align) == 4
    print(developer_score(struct_align, seq_align))
    print(modeller_score(struct_align, seq_align))
