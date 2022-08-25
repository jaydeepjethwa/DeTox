from .model_class import DetoxClass
from . import torch, np, pd, fine_tuned_path


# function to load the ml model
def load_model():
    global device, model
    
    model = DetoxClass()
    device = 'cpu'
    
    if torch.cuda.is_available():
        device = 'cuda'
        model.load_state_dict(torch.load(fine_tuned_path))
        model.to(device)
    else:
        model.load_state_dict(torch.load(fine_tuned_path, map_location=device))


# predict classes of the comments
async def predict(inference_loader):

    model.eval()
    comment_id = []
    preds = []
    
    for _, data in enumerate(inference_loader, 0):

        comment_id.extend(data['comment_id'])

        ids = data['ids'].to(device, dtype = torch.long)
        mask = data['mask'].to(device, dtype = torch.long)
        token_type_ids = data['token_type_ids'].to(device, dtype = torch.long)

        outputs = model(ids, mask, token_type_ids)
        preds.extend(torch.sigmoid(outputs).cpu().detach().numpy().tolist())

    preds = np.array(preds) >= 0.5
    
    # return comment_id, preds
    predictions = {
        'id': comment_id,
        'labels': [pred for pred in preds]
    }

    predictions = pd.DataFrame.from_dict(predictions)
    labels = ['Toxic', 'Severe Toxic', 'Obscene', 'Threat', 'Insult', 'Identity Hate']
    predictions[labels] = pd.DataFrame(predictions.labels.tolist(), index = predictions.index)
    predictions.drop(columns=['labels'], axis=1, inplace=True)
    predictions.replace({False: 0, True: 1}, inplace=True)

    return predictions