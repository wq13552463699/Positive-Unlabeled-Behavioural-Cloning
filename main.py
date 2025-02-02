#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 22:00:42 2022

@author: qiang
"""
import argparse
import utils
import trainer
import buffer
import d3rlpy
import warnings
warnings.filterwarnings("ignore")

def main_filter(args):
    args = utils.directory_handler(args)
    buff = buffer.PUBuffer(args) # Load and preprocess the dataset
    
    # Classifier training
    classifier = trainer.PUTrainer(buff.args) # Init the classifier
    if args.load_trained_filter:
        classifier.load(buff.classifier_validate) # Load the trained model
        buff.update_pos() # Use the loaded model to filter positive examples from the mixed dataset
    else:
        buff.set_seed_positive() # Init the seed-positive dataset
        # Train
        for t in range(args.iterations):
            classifier.train(buff.torch_loader, args.epochs_per_iteration, t, buff.classifier_validate)
            buff.update_pos() # Update the seed-positive dataset
    
    # Policy training
    if args.train_policy:
        policy_dataset = buff.init_torch_loader_to_train_policy() # Convert the dataset to d3rlpy style
        mdpd_dataset = d3rlpy.dataset.MDPDataset(
                                                observations=policy_dataset['observations'],
                                                actions=policy_dataset['actions'],
                                                rewards=policy_dataset['rewards'],
                                                terminals=policy_dataset['timeouts'],
                                            )
        # Train
        algo = utils.policy_handler(buff.args)
        algo.build_with_dataset(mdpd_dataset)
        algo.fit(mdpd_dataset, n_epochs=200)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-dataset-path', type=str, default='<path to the mixed dataset>', help='Path to the raw mixed dataset')
    parser.add_argument('--pos-seed-dataset-path', type=str, default='<path to the seed dataset (optional)>', help='Path to the seed-positive dataset')
    parser.add_argument('--exp-name', type=str, default="pubc", help='Experiment name')
    parser.add_argument('--models-in-ensemble', type=int, default=3, help='Number of unit models in the ensemble model')
    parser.add_argument('--ensemble-method', type=str, default='vote',  help="'avg' or 'vote'")
    parser.add_argument('--iterations', type=int, default=2, help='Iteration number for each classifier training trail')
    parser.add_argument('--negative-sampler', type=str, default='part', help="'part' or 'full'")
    parser.add_argument('--epochs-per-iteration', type=int, default=20, help='Number of epoch lasts per classifier training iteration')
    parser.add_argument('--pos-seed-rate', type=float, default=0.004, help='The top rewarding trajectaries are selected as the seed-positive dataset if it is not given')
    parser.add_argument('--th-bins', type=int, default=100, help='Adaptive threshold')
    parser.add_argument('--th-high-bound', type=float, default=0.96, help='Adaptive threshold')
    parser.add_argument('--th-fit-pow', type=int, default=10, help='Polynomial order for adaptive threshold')
    parser.add_argument('--seeds', type=int, default=0, help='random seed')
    parser.add_argument('--use-gpu', type=bool, default=True, help='Use GPU for accelerating or not')
    parser.add_argument('--batch-size', type=int, default=1024, help='Classifier training batch size')
    parser.add_argument('--learning-rate', type=int, default=0.001, help='Classifier training learning rate')
    parser.add_argument('--save-path', type=str, default=None, help="Path to save the output results. If it is not given, one folder named 'save' will be created under the root project path for saving the results")
    parser.add_argument('--train-policy', type=bool, default=True, help='Whether train policy')
    parser.add_argument('--policy', type=str, default='bc', help='Train which policy')
    parser.add_argument('--load-trained-filter', type=bool, default=False, help='Whether use the trained filter or train from scratch')
    parser.add_argument('--trained-filter-path', type=str, default=None, help='The path to the filter saved folder RATHER THAN one file path')
    parser.add_argument('--ckpt-iterations', type=int, default=4, help='How many iterations you run in the exist filter')
    args = parser.parse_args()
    main_filter(args)
