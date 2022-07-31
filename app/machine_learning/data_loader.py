from . import BertTokenizer, DataLoader, pretrained_path
from .data_class import DetoxDataset

MAX_LEN = 200
BATCH_SIZE = 8
tokenizer = BertTokenizer.from_pretrained(pretrained_path)

async def data_loader(data):
    inference_set = DetoxDataset(data, tokenizer, MAX_LEN)

    inference_params = {
        'batch_size': BATCH_SIZE,
        'shuffle': False,
        'num_workers': 0
    }

    inference_loader = DataLoader(inference_set, **inference_params)

    return inference_loader