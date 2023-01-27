from transformers import BertTokenizer
from torch.utils.data import DataLoader
from .data_class import DetoxDataset
from . import pretrained_path

# parameters for data loader
MAX_LEN = 200
BATCH_SIZE = 8


def load_tokeninzer() -> None:
    """Loads BERT Tokenizer."""
    
    global tokenizer
    tokenizer = BertTokenizer.from_pretrained(pretrained_path)


def data_loader(data) -> DataLoader:
    """Creates and returns a iterative data loader object for making predictions in batch.

    Args:
        data (pandas DataFrame): Dataset of which we need to create data loader.

    Returns:
        PyTorch DataLoader: A python iterable over a dataset.
    """
    
    inference_set = DetoxDataset(data, tokenizer, MAX_LEN)

    inference_params = {
        'batch_size': BATCH_SIZE,
        'shuffle': False,
        'num_workers': 0
    }

    inference_loader = DataLoader(inference_set, **inference_params)

    return inference_loader