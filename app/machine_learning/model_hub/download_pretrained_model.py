from transformers import BertModel, BertTokenizer

# get pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# saving the tokenizer and model for offline use
tokenizer.save_pretrained("./pretrained/bert-base-uncased")
model.save_pretrained("./pretrained/bert-base-uncased")