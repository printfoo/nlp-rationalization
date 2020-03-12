# coding: utf-8


# Catch passed auguments from run script.
import sys, os
import argparse
parser = argparse.ArgumentParser()

# Mode arguments.
parser.add_argument("--mode", type=str, default="train",
                    help="Run mode, train or eval.")

# Environment arguments.
parser.add_argument("--data_dir", type=str, default="data",
                    help="Data folder name.")
parser.add_argument("--output_dir", type=str, default="output",
                    help="Output folder name.")
parser.add_argument("--random_seed", type=int, default=0,
                    help="Random seed.")
parser.add_argument("--cuda", type=bool, default=True,
                    help="If use CUDA GPU.")
parser.add_argument("--gpu_id", type=str, default="1",
                    help="ID of the GPU chip to use.")

# Data arguments.
parser.add_argument("--data_name", type=str, default="beer_reviews",
                    help="Dataset name.")
parser.add_argument("--embedding_name", type=str, default="glove",
                    help="Embedding name.")
parser.add_argument("--freq_threshold", type=int, default=1,
                    help="Minimum frequency for vocabulary.")
parser.add_argument("--truncate_num", type=int, default=300,
                    help="Maximum number of tokens to truncate.")

# Model arguments.,
parser.add_argument("--model_type", type=str, default="RNN",
                    help="Model type, RNN or CNN.")
parser.add_argument("--hidden_dim", type=int, default=400,
                    help="Dimension of hidden states.")
parser.add_argument("--z_dim", type=int, default=2,
                    help="Dimension of rationale mask, always 2 for now.")
parser.add_argument("--embedding_dim", type=int, default=100,
                    help="Dimension of word embeddings.")
parser.add_argument("--fine_tuning", type=bool, default=False,
                    help="Whether to fine tune embeddings or not.")
parser.add_argument("--layer_num", type=int, default=1,
                    help="If RNN, number of RNN layers.")
parser.add_argument("--cell_type", type=str, default="GRU",
                    help="If RNN, cell type, GRU or LSTM.")
parser.add_argument("--kernel_size", type=int, default=5,
                    help="If CNN, kernel size of the conv1d.")
parser.add_argument("--batch_size", type=int, default=64,
                    help="Batch size.")
parser.add_argument("--lr", type=float, default=0.001,
                    help="Learning rate.")
parser.add_argument("--lambda_sparsity", type=float, default=1.0,
                    help="Control the importance of sparsity.")
parser.add_argument("--lambda_continuity", type=float, default=1.0,
                    help="Control the importance of continuity.")
parser.add_argument("--lambda_anti", type=float, default=1.0,
                    help="Control the importance of anti-predictor.")
parser.add_argument("--exploration_rate", type=float, default=0.05,
                    help="Exploration rate.")
parser.add_argument("--rationale_len", type=int, default=8,
                    help="Suggested length of rationales.")
parser.add_argument("--rationale_num", type=int, default=4,
                    help="Suggested number of rationales.")

# Training arguments.
parser.add_argument("--num_iteration", type=int, default=2000,
                    help="Number of iterations to train.")
parser.add_argument("--display_iteration", type=int, default=100,
                    help="Number of iterations to display results.")
parser.add_argument("--eval_iteration", type=int, default=100,
                    help="Number of iterations to evaluate.")

# Parse arguments.
args, extras = parser.parse_known_args()
args.extras = extras
args.command = " ".join(["python"] + sys.argv)
print("Command with argumanets:", args.command)

# Additional arguments.
args.working_dir = os.path.join(args.output_dir, args.data_name)
args.embedding_dir = os.path.join(args.data_dir, args.embedding_name, args.embedding_name + ".6B.%sd.txt" % args.embedding_dim)

if args.mode == "train":

    # Set random seeds.
    import torch
    import numpy as np
    import random
    torch.manual_seed(args.random_seed)
    np.random.seed(args.random_seed)
    random.seed(args.random_seed)

    # Load data and embeddings.
    from datasets.dataset_loader import SentenceClassification
    data_path = os.path.join(args.data_dir, args.data_name)
    data = SentenceClassification(data_path, args)  # Load data.
    args.num_labels = len(data.label_vocab)  # Number of labels.
    embeddings = data.initial_embedding(args.embedding_dim, args.embedding_dir)  # Load embeddings.
    print("Data and embeddings successfully loaded:", data, embeddings.shape)

    # Initialize model.
    from models.rationale_3player_classification import Rationale3PlayerClassification
    model = Rationale3PlayerClassification(embeddings, args)
    print("Model successfully initialized:", model)

    # Train model.
    from runner.trainer import train
    train(model, data, args)
    print("Model successfully trained.")

elif args.mode == "test":

    # Test data loader.
    from datasets.dataset_loader import test_data
    data_path = os.path.join(args.data_dir, args.data_name)
    data = test_data(data_path, args)  # Load data.
    print("Data loader is tested")

elif args.mode == "purge":

    # Perge all checkpoints.
    from utils.checkpointer import purge
    purge(args.working_dir)
    print("All checkpoints purged.")

else:
    exit("Wrong mode.")
