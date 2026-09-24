import os
import torch
import torch.nn as nn
import pandas as pd
import numpy as np

class NeuMF(nn.Module):
    def __init__(self, num_users, num_items, latent_dim_mf=32, latent_dim_mlp=32, mlp_hidden_dims=[64, 32, 16]):
        super(NeuMF, self).__init__()
        self.user_embed_mf = nn.Embedding(num_users, latent_dim_mf)
        self.item_embed_mf = nn.Embedding(num_items, latent_dim_mf)
        
        self.user_embed_mlp = nn.Embedding(num_users, latent_dim_mlp)
        self.item_embed_mlp = nn.Embedding(num_items, latent_dim_mlp)
        
        mlp_layers = []
        input_dim = latent_dim_mlp * 2
        for h_dim in mlp_hidden_dims:
            mlp_layers.append(nn.Linear(input_dim, h_dim))
            mlp_layers.append(nn.ReLU())
            mlp_layers.append(nn.Dropout(0.2))
            input_dim = h_dim
        self.mlp = nn.Sequential(*mlp_layers)
        
        final_dim = latent_dim_mf + mlp_hidden_dims[-1]
        self.prediction_layer = nn.Linear(final_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, user_indices, item_indices):
        user_mf = self.user_embed_mf(user_indices)
        item_mf = self.item_embed_mf(item_indices)
        mf_vector = user_mf * item_mf
        
        user_mlp = self.user_embed_mlp(user_indices)
        item_mlp = self.item_embed_mlp(item_indices)
        mlp_input = torch.cat([user_mlp, item_mlp], dim=-1)
        mlp_vector = self.mlp(mlp_input)
        
        combined = torch.cat([mf_vector, mlp_vector], dim=-1)
        logits = self.prediction_layer(combined)
        return self.sigmoid(logits)

def train_ncf(cleaned_dir='data/cleaned', out_dir='data/score_matrices', epochs=15):
    os.makedirs(out_dir, exist_ok=True)
    print("--- Step 5: Training Neural Collaborative Filtering (NCF) ---")
    
    train_df = pd.read_csv(os.path.join(cleaned_dir, 'train.csv'))
    full_df = pd.read_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'))
    
    all_users = full_df['Reviewer'].unique().tolist()
    all_courses = full_df['Course Name'].unique().tolist()
    
    user2id = {u: i for i, u in enumerate(all_users)}
    item2id = {c: i for i, c in enumerate(all_courses)}
    
    n_users = len(all_users)
    n_items = len(all_courses)
    
    u_idx = torch.tensor([user2id[u] for u in train_df['Reviewer'] if u in user2id], dtype=torch.long)
    i_idx = torch.tensor([item2id[c] for c in train_df['Course Name'] if c in item2id], dtype=torch.long)
    ratings = torch.tensor((train_df['Individual Rating'] / 5.0).values, dtype=torch.float32).unsqueeze(1)
    
    model = NeuMF(n_users, n_items)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
    
    model.train()
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        preds = model(u_idx, i_idx)
        loss = criterion(preds, ratings)
        loss.backward()
        optimizer.step()
        
        if epoch % 5 == 0 or epoch == epochs:
            print(f"  NCF Epoch {epoch}/{epochs} - MSE Loss: {loss.item():.4f}")
            
    # Full prediction matrix
    model.eval()
    score_matrix = np.zeros((n_users, n_items))
    with torch.no_grad():
        for u in range(n_users):
            u_t = torch.tensor([u] * n_items, dtype=torch.long)
            i_t = torch.arange(n_items, dtype=torch.long)
            p = model(u_t, i_t).squeeze().numpy()
            score_matrix[u] = p
            
    score_df = pd.DataFrame(score_matrix, index=all_users, columns=all_courses)
    out_path = os.path.join(out_dir, 'scoring_matrix_ncf.csv')
    score_df.to_csv(out_path)
    print(f"NCF scoring matrix saved to {out_path} (Shape: {score_df.shape})")
    return score_df

if __name__ == '__main__':
    train_ncf()
