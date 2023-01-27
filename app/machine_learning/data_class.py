import torch
from torch.utils.data import Dataset

class DetoxDataset(Dataset):
    """PyTorch dataset class."""

    def __init__(self, dataframe, tokenizer, max_len) -> None:
        """Constructor for class.

        Args:
            dataframe (pandas DataFrame): DataFrame under consideration for prediction.
            tokenizer : BERT tokenizer object.
            max_len (int): Maximum length for sentences.
        """
        self.tokenizer = tokenizer
        self.data = dataframe
        self.comment_id = dataframe.id
        self.comment_text = self.data.comment_text
        self.max_len = max_len

    def __len__(self) -> int:
        """Identifies no. of instances (rows) in dataset
        Returns:
            int: Length (instances) of current dataset.
        """
        
        return len(self.comment_text)

    def __getitem__(self, index) -> dict:
        """Returns instance from dataset that is ready to be passed to ml model.
        Args:
            index (int): Index of instance to be returned.

        Returns:
            dict: Dictionary containing comment_id, ids(mappings between tokens and their respective IDs), mask(prevent the model from looking at padding tokens) and token type ids(represents sentence id).
        """
        
        comment_text = str(self.comment_text[index])
        comment_text = " ".join(comment_text.split())

        inputs = self.tokenizer.encode_plus(
            comment_text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            return_token_type_ids=True,
            truncation=True
        )
        
        ids = inputs['input_ids']
        mask = inputs['attention_mask']
        token_type_ids = inputs["token_type_ids"]


        return {
            'comment_id': self.comment_id[index],
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long)
        }