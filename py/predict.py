import os
import sys
import argparse
import pickle
import subprocess
from common.config import Config
from binary import Binary


def get_args():
    parser = argparse.ArgumentParser(description='Debin to hack binaries. '\
        'This script takes an stripped binary as input and output a binary with predicted debug information.')

    parser.add_argument('--binary', dest='binary', type=str, default='', required=True,
                        help='path of the binary you want to analyze.')
    parser.add_argument('--output', dest='output', type=str, default='', required=True,
                        help='path of output binary.')
    parser.add_argument('--bap', dest='bap', type=str, default='',
                        help='path of cached BAP-IR file.')
    parser.add_argument('--elf_modifier', dest='elf_modifier', type=str, default='', required=True,
                        help='path of the library for modifying ELF binaries.')

    parser.add_argument('-two_pass', dest='two_pass', action='store_true', default=False,
                        help='whether to use two passes (variable classification and structured prediction). Setting it to false only will only invoke structured prediction.')
    parser.add_argument('--fp_model', dest='fp_model', type=str, default='',
                        help='Path of the models for the first pass (variable classification).')

    parser.add_argument('--n2p_url', dest='n2p_url', type=str, default='', required=True,
                        help='URL of n2p server.')

    args = parser.parse_args()

    return args


def main():
    args = get_args()

    config = Config()

    config.MODE = config.TEST

    config.BINARY_PATH = args.binary
    config.BINARY_NAME = args.binary
    config.OUTPUT_BINARY_PATH = args.output
    config.BAP_FILE_PATH = args.bap
    config.MODIFY_ELF_LIB_PATH = args.elf_modifier

    config.TWO_PASS = args.two_pass
    config.FP_MODEL_PATH = args.fp_model
    if config.TWO_PASS:
        reg_dict = open(os.path.join(config.FP_MODEL_PATH, 'reg.dict'), 'rb')
        reg_model = open(os.path.join(config.FP_MODEL_PATH, 'reg.model'), 'rb')
        reg_support = open(os.path.join(config.FP_MODEL_PATH, 'reg.support'), 'rb')
        config.REG_DICT = pickle.load(reg_dict, encoding='latin1')
        config.REG_SUPPORT = pickle.load(reg_support, encoding='latin1')
        config.REG_DICT.restrict(config.REG_SUPPORT.get_support())
        config.REG_MODEL = pickle.load(reg_model, encoding='latin1')
        config.REG_MODEL.n_jobs = 1

        off_dict = open(os.path.join(config.FP_MODEL_PATH, 'off.dict'), 'rb')
        off_model = open(os.path.join(config.FP_MODEL_PATH, 'off.model'), 'rb')
        off_support = open(os.path.join(config.FP_MODEL_PATH, 'off.support'), 'rb')
        config.OFF_DICT = pickle.load(off_dict, encoding='latin1')
        config.OFF_SUPPORT = pickle.load(off_support, encoding='latin1')
        config.OFF_DICT.restrict(config.OFF_SUPPORT.get_support())
        config.OFF_MODEL = pickle.load(off_model, encoding='latin1')
        config.OFF_MODEL.n_jobs = 1

    config.N2P_SERVER_URL = args.n2p_url

    with open(config.BINARY_PATH, 'rb') as elffile:
        b = Binary(config, elffile)
        b.set_test_result_from_server()
        b.modify_elf()

    if config.TWO_PASS:
        reg_dict.close()
        reg_support.close()
        reg_model.close()
        off_dict.close()
        off_support.close()
        off_model.close()


if __name__ == '__main__':
    main()