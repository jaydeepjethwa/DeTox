import torch
import numpy as np
import pandas as pd
from .model_class import DetoxClass
from .data_loader import data_loader
from . import fine_tuned_path


def load_model() -> None:
    """Loads fine-tuned model for prediction."""
    
    global device, model
    
    model = DetoxClass()
    
    # loads model to GPU if available else on CPU
    device = 'cpu' 
    if torch.cuda.is_available():
        device = 'cuda'
        model.load_state_dict(torch.load(fine_tuned_path))
        model.to(device)
    else:
        model.load_state_dict(torch.load(fine_tuned_path, map_location=device))


def predict(data: pd.DataFrame) -> pd.DataFrame:
    """Predics classes of the comments.

    Args:
        inference_loader (PyTorch DataLoader): A python iterable over a dataset.

    Returns:
        pandas DataFrame: DataFrame containing predicted class for comments.
    """

    # get data loader
    inference_loader = data_loader(data)
    
    # set model to evaluation (inference) mode
    model.eval()
    comment_id = []
    preds = []
    
    # iterate over every batch of dataset using data loader and make predictions
    for _, data in enumerate(inference_loader, 0):

        comment_id.extend(data['comment_id'])

        ids = data['ids'].to(device, dtype = torch.long)
        mask = data['mask'].to(device, dtype = torch.long)
        token_type_ids = data['token_type_ids'].to(device, dtype = torch.long)

        outputs = model(ids, mask, token_type_ids)
        preds.extend(torch.sigmoid(outputs).cpu().detach().numpy().tolist())

    # activate a class if logit value crosses threshold
    preds = np.array(preds) >= 0.5
    
    predictions = {
        'id': comment_id,
        'labels': [pred for pred in preds]
    }

    # convert dict to pandas DataFrame
    predictions = pd.DataFrame.from_dict(predictions)
    labels = ['Toxic', 'Severe Toxic', 'Obscene', 'Threat', 'Insult', 'Identity Hate']
    predictions[labels] = pd.DataFrame(predictions.labels.tolist(), index = predictions.index)
    predictions.drop(columns=['labels'], axis=1, inplace=True)
    predictions.replace({False: 0, True: 1}, inplace=True)

    return predictions