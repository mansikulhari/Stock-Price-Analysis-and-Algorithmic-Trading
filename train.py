from models.time_series_transformer import TimeSeriesTransformer
import torch
from torch.utils.data import DataLoader, TensorDataset, random_split
import torch.optim as optim
import numpy as np
import mysql.connector
import matplotlib.pyplot as plt


def smape_loss(y_pred, y_true):
    epsilon = 1e-8
    summ = torch.abs(y_true) + torch.abs(y_pred) + epsilon
    smape = torch.abs(y_pred - y_true) / summ * 2.0

    return torch.mean(smape)


def gen_trg_mask(size, device):
    mask = torch.triu(torch.ones(size, size) == 1, diagonal=1).to(device)
    mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
    return mask


def get_data(symbol, context_length):
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="easy",
        database="stock_data",
        connection_timeout=5
    )
    cursor = conn.cursor()

    pricesQuery = "SELECT close FROM StockData WHERE symbol = '%s' ORDER BY date ASC;" % symbol
    cursor.execute(pricesQuery)
    data = [row[0] for row in cursor.fetchall()]  # list of prices
    # Create sequences
    X, Y = [], []
    for i in range(len(data) - context_length):
        X.append(data[i:i + context_length])
        Y.append(data[i + context_length])

    # write data to file
    with open('data.txt', 'w') as f:
        for i in range(len(X)):
            f.write(f"{','.join([str(v) for v in X[i]])},{str(Y[i])}\n")



    # Convert to numpy arrays and reshape
    X = np.array(X).reshape(-1, context_length)
    Y = np.array(Y).reshape(-1, 1)

    # Normalize data here if needed

    # Convert to PyTorch tensors
    X_tensor = torch.FloatTensor(X)
    Y_tensor = torch.FloatTensor(Y)

    return X_tensor, Y_tensor


def train(symbol, context_length):
    X, Y = get_data(symbol, context_length)
    train_size = int(0.8 * len(X))
    test_size = len(X) - train_size

    # Randomly split dataset
    train_dataset, test_dataset = random_split(TensorDataset(X, Y), [train_size, test_size])

    # Create data loaders
    train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    model = TimeSeriesTransformer(
        n_encoder_inputs=1,
        n_decoder_inputs=1,
        channels=512,
        dropout=0.1,
        lr=1e-4,
    )

    # Initialize the optimizer
    optimizer = optim.Adam(model.parameters(), lr=model.lr)

    n_epochs = 1
    loss = None
    true_values = []
    predicted_values = []
    # Training loop
    for epoch in range(n_epochs):
        model.train()
        for batch_idx, (src, trg) in enumerate(train_dataloader):
            if batch_idx == len(train_dataloader) - 1:
                break
            optimizer.zero_grad()

            src = src.unsqueeze(2)  # Adding an extra dimension, changing shape from (32, 30) to (32, 30, 1)
            trg_in = src  # For sequence-to-one, src and trg_in would be same
            trg_out = trg  # The value you want to predict

            loss = model.training_step((src, trg_in, trg_out), batch_idx)
            loss.backward()
            optimizer.step()

        model.eval()
        val_loss = 0

        with torch.no_grad():
            for batch_idx, (src, trg) in enumerate(val_dataloader):
                if batch_idx == len(val_dataloader) - 1:
                    break
                true_values = []
                predicted_values = []
                src = src.unsqueeze(2)
                trg_in = src  # src and trg_in are the same in your context
                trg_out = trg  # the value you want to predict

                y_hat = model((src, trg_in))  # your prediction
                val_loss += model.validation_step((src, trg_in, trg_out), batch_idx)

                true_values.extend(trg_out.squeeze(1).cpu().numpy())
                predicted_values.extend(y_hat.squeeze(1).cpu().numpy())

            val_loss /= len(val_dataloader)

        print(f"Epoch {epoch + 1}, Train Loss: {loss.item()}, Validation Loss: {val_loss}")

    plt.figure(figsize=(14, 5))
    plt.plot(true_values, label='True Values', color='blue')
    plt.plot(predicted_values, label='Predictions', color='red')
    plt.legend()
    plt.show()
