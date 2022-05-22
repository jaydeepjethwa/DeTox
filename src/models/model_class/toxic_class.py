from ... import BertModel, Module, Dropout, Linear

class DetoxClass(Module):
    def __init__(self):
        super(DetoxClass, self).__init__()
        self.l1 = BertModel.from_pretrained('models/pretrained/bert-base-uncased')
        self.l2 = Dropout(0.3)
        self.l3 = Linear(768, 6)
    
    def forward(self, ids, mask, token_type_ids):
        _, output_1= self.l1(ids, attention_mask = mask, token_type_ids = token_type_ids, return_dict=False)
        output_2 = self.l2(output_1)
        output = self.l3(output_2)
        
        return output