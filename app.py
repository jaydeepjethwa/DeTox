from src import toxic_data, toxic_model, pd
from tqdm import tqdm
import time

dataset = pd.read_csv('data/toxic/test/test.csv', chunksize=100)

start = time.time()
i = 50
for data in tqdm(dataset):
    df = data.copy().reset_index(drop=True)
    inference_loader = toxic_data.data_loader(df)

    preds = toxic_model.get_predictions(inference_loader)

    # preds.to_csv('test.csv', index=False, header=False, mode='a')
    i += 1
    if i == 5:
        break

print(f"Time Taken: {time.time() - start}")