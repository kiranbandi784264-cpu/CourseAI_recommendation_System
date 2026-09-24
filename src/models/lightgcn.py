import os
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import scipy.sparse as sp

class LightGCN(nn.Module):
    def __init__(self, num_users, num_items, emb_dim=64, num_layers=3):
        super(LightGCN, self).__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.num_layers = num_layers
        
        self.user_embedding = nn.Embedding(num_users, emb_dim)
        self.item_embedding = nn.Embedding(num_items, emb_dim)
        
        nn.init.normal_(self.user_embedding.weight, std=0.1)
        nn.init.normal_(self.item_embedding.weight, std=0.1)
        
    def forward(self, adj):
        ego_embeddings = torch.cat([self.user_embedding.weight, self.item_embedding.weight], dim=0)
        all_embeddings = [ego_embeddings]
        
        for _ in range(self.num_layers):
            ego_embeddings = torch.sparse.mm(adj, ego_embeddings)
            all_embeddings.append(ego_embeddings)
            
        final_embeddings = torch.mean(torch.stack(all_embeddings, dim=0), dim=0)
        user_all, item_all = torch.split(final_embeddings, [self.num_users, self.num_items])
        return user_all, item_all

def train_lightgcn(cleaned_dir='data/cleaned', out_dir='data/score_matrices', epochs=15):
    os.makedirs(out_dir, exist_ok=True)
    print("--- Step 4: Training LightGCN Graph Neural Network ---")
    
    train_df = pd.read_csv(os.path.join(cleaned_dir, 'train.csv'))
    full_df = pd.read_csv(os.path.join(cleaned_dir, 'final_users_courses.csv'))
    
    all_users = full_df['Reviewer'].unique().tolist()
    all_courses = full_df['Course Name'].unique().tolist()
    
    user2id = {u: i for i, u in enumerate(all_users)}
    item2id = {c: i for i, c in enumerate(all_courses)}
    
    n_users = len(all_users)
    n_items = len(all_courses)
    
    # Construct Bipartite Graph Adjacency Matrix
    user_ids = [user2id[u] for u in train_df['Reviewer'] if u in user2id]
    item_ids = [item2id[c] for c in train_df['Course Name'] if c in item2id]
    
    R = sp.dok_matrix((n_users, n_items), dtype=np.float32)
    for u, i in zip(user_ids, item_ids):
        R[u, i] = 1.0
        
    R = R.tocsr()
    
    # Normalized Adjacency A_tilde
    adj_mat = sp.dok_matrix((n_users + n_items, n_users + n_items), dtype=np.float32)
    adj_mat = adj_mat.tolil()
    adj_mat[:n_users, n_users:] = R
    adj_mat[n_users:, :n_users] = R.T
    adj_mat = adj_mat.tocsr()
    
    rowsum = np.array(adj_mat.sum(1))
    d_inv = np.power(rowsum, -0.5).flatten()
    d_inv[np.isinf(d_inv)] = 0.
    d_mat = sp.diags(d_inv)
    
    norm_adj = d_mat.dot(adj_mat).dot(d_mat).tocoo()
    
    indices = torch.from_numpy(np.vstack((norm_adj.row, norm_adj.col)).astype(np.int64))
    values = torch.from_numpy(norm_adj.data.astype(np.float32))
    shape = torch.Size(norm_adj.shape)
    sparse_adj = torch.sparse_coo_tensor(indices, values, shape)
    
    model = LightGCN(n_users, n_items, emb_dim=64, num_layers=3)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    # Train BPR loss
    model.train()
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        u_emb, i_emb = model(sparse_adj)
        
        # Sample BPR triplets
        u_samples = torch.tensor(user_ids, dtype=torch.long)
        pos_i_samples = torch.tensor(item_ids, dtype=torch.long)
        neg_i_samples = torch.randint(0, n_items, (len(user_ids),), dtype=torch.long)
        
        u_e = u_emb[u_samples]
        pos_e = i_emb[pos_i_samples]
        neg_e = i_emb[neg_i_samples]
        
        pos_scores = torch.sum(u_e * pos_e, dim=1)
        neg_scores = torch.sum(u_e * neg_e, dim=1)
        
        loss = -torch.mean(torch.log(torch.sigmoid(pos_scores - neg_scores) + 1e-8))
        loss.backward()
        optimizer.step()
        
        if epoch % 5 == 0 or epoch == epochs:
            print(f"  LightGCN Epoch {epoch}/{epochs} - BPR Loss: {loss.item():.4f}")
            
    # Calculate full prediction matrix
    model.eval()
    with torch.no_grad():
        u_final, i_final = model(sparse_adj)
        scores = torch.matmul(u_final, i_final.T).numpy()
        
    score_df = pd.DataFrame(scores, index=all_users, columns=all_courses)
    out_path = os.path.join(out_dir, 'scoring_matrix_lightgcn.csv')
    score_df.to_csv(out_path)
    print(f"LightGCN scoring matrix saved to {out_path} (Shape: {score_df.shape})")
    return score_df

if __name__ == '__main__':
    train_lightgcn()
