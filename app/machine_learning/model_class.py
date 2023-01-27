from transformers import BertModel
from torch.nn import Module, Dropout, Linear
from . import pretrained_path

class DetoxClass(Module):
    """PyTorch Model Class."""
    
    def __init__(self) -> None:
        """Constructor. Defines layers of the model."""
        
        super(DetoxClass, self).__init__()
        self.l1 = BertModel.from_pretrained(pretrained_path)
        self.l2 = Dropout(0.3)
        self.l3 = Linear(768, 6)
    
    def forward(self, ids, mask, token_type_ids):
        """Defines forward pass of the model.

        Args:
            ids (list): Output from BERT Tokenizer. A mapping between tokens and their respective IDs.
            mask (list): Output from BERT Tokenizer. Prevents the model from looking at padding tokens.
            token_type_ids (list): Output from BERT Tokenizer. Represents sentence id.

        Returns:
            torch Tensor: Output tensor containing logits for classes.
        """
        
        _, output_1= self.l1(ids, attention_mask = mask, token_type_ids = token_type_ids, return_dict=False)
        output_2 = self.l2(output_1)
        output = self.l3(output_2)
        
        return output