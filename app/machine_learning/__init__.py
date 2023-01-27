"""Machine learning modules helping to predict classes."""

# paths
pretrained_path = "machine_learning/model_hub/pretrained/bert-base-uncased"
fine_tuned_path = "machine_learning/model_hub/fine_tuned/toxic_model.pth"

# useful functions for easy access
from .data_loader import load_tokeninzer
from .make_predictions import predict, load_model