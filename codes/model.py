import torch
from torch import nn
from dgl.nn.pytorch import GATv2Conv
from dgl.nn import GlobalAttentionPooling
import dgl 
import pdb 
import copy

class GraphModel(nn.Module):
    def __init__(self, in_dim, graph_hiddens=[64, 128], device='cpu', attn_head=4, activation=0.2, **kwargs):
        super(GraphModel, self).__init__()
        '''
        Params:
            in_dim: the feature dim of each node
        '''
        layers = []

        for i, hidden in enumerate(graph_hiddens):
            in_feats = graph_hiddens[i-1] if i > 0 else in_dim 
            dropout = kwargs["attn_drop"] if "attn_drop" in kwargs else 0
            layers.append(GATv2Conv(in_feats, out_feats=hidden, num_heads=attn_head, 
                                        attn_drop=dropout, negative_slope=activation, allow_zero_in_degree=True)) 
            self.maxpool = nn.MaxPool1d(attn_head)

        self.net = nn.Sequential(*layers).to(device)
        self.out_dim = graph_hiddens[-1]
        self.pooling = GlobalAttentionPooling(nn.Linear(self.out_dim, 1)) 

    
    def forward(self, graph, x):
        '''
        Input:
            x -- tensor float [batch_size*node_num, feature_in_dim] N = {s1, s2, s3, e1, e2, e3}
        '''
        out = None
        for layer in self.net:
            if out is None: out = x
            out = layer(graph, out)
            out = self.maxpool(out.permute(0, 2, 1)).permute(0, 2, 1).squeeze()
        return self.pooling(graph, out) #[bz*node, out_dim] --> [bz, out_dim]

class Chomp1d(nn.Module):
    def __init__(self, chomp_size):
        super(Chomp1d, self).__init__()
        self.chomp_size = chomp_size
    def forward(self, x):
        return x[:, :, :-self.chomp_size].contiguous()

class ConvNet(nn.Module):
    def __init__(self, num_inputs, num_channels, kernel_sizes, dilation=2, dev="cpu"):
        super(ConvNet, self).__init__()
        layers = []
        for i in range(len(kernel_sizes)):
            dilation_size = dilation ** i
            kernel_size = kernel_sizes[i]
            padding = (kernel_size-1) * dilation_size
            in_channels = num_inputs if i == 0 else num_channels[i-1]
            out_channels = num_channels[i]
            layers += [nn.Conv1d(in_channels, out_channels, kernel_size, stride=1, dilation=dilation_size, padding=padding), 
                       nn.BatchNorm1d(out_channels), nn.ReLU(), Chomp1d(padding)]
            
        self.network = nn.Sequential(*layers)
        
        self.out_dim = num_channels[-1]
        self.network.to(dev)
        
    
    def forward(self, x): #[batch_size, T, in_dim]
        x = x.permute(0, 2, 1).float() #[batch_size, in_dim, T]
        out = self.network(x) #[batch_size, out_dim, T]
        out = out.permute(0, 2, 1) #[batch_size, T, out_dim]
        return out

import math
class SelfAttention(nn.Module):
    def __init__(self, input_size, seq_len):
        """
        Args:
            input_size: int, hidden_size * num_directions
            seq_len: window_size
        """
        super(SelfAttention, self).__init__()
        self.atten_w = nn.Parameter(torch.randn(seq_len, input_size, 1))
        self.atten_bias = nn.Parameter(torch.randn(seq_len, 1, 1))
        self.glorot(self.atten_w)
        self.atten_bias.data.fill_(0)

    def forward(self, x):
        # x: [batch_size, window_size, input_size]
        input_tensor = x.transpose(1, 0)  # w x b x h
        input_tensor = (torch.bmm(input_tensor, self.atten_w) + self.atten_bias)  # w x b x out
        input_tensor = input_tensor.transpose(1, 0)
        atten_weight = input_tensor.tanh()
        weighted_sum = torch.bmm(atten_weight.transpose(1, 2), x).squeeze()
        return weighted_sum

    def glorot(self, tensor):
        if tensor is not None:
            stdv = math.sqrt(6.0 / (tensor.size(-2) + tensor.size(-1)))
            tensor.data.uniform_(-stdv, stdv)

class TraceModel(nn.Module):
    def __init__(self, device='cpu', trace_hiddens=[20, 50], trace_kernel_sizes=[3, 3], self_attn=False, chunk_lenth=None, **kwargs):
        super(TraceModel, self).__init__()

        self.out_dim = trace_hiddens[-1]
        assert len(trace_hiddens) == len(trace_kernel_sizes)
        trace_dropout = 0
        #self.net = ConvNet(1, num_channels=trace_hiddens, kernel_sizes=trace_kernel_sizes,
        #            dev=device, dropout=trace_dropout)
        self.net = ConvNet(1, num_channels=trace_hiddens, kernel_sizes=trace_kernel_sizes,
                           dev=device)

        self.self_attn = self_attn
        if self_attn:
            assert (chunk_lenth is not None)
            self.attn_layer = SelfAttention(self.out_dim, chunk_lenth)

    def forward(self, x: torch.tensor): #[bz, T, 1]
        #print(x.size())
        hidden_states = self.net(x)
        if self.self_attn: 
            return self.attn_layer(hidden_states)
        return hidden_states[:,-1,:] #[bz, out_dim]

class MetricModel(nn.Module):
    def __init__(self, metric_num, device='cpu', metric_hiddens=[64, 128], metric_kernel_sizes=[3, 3], self_attn=False, chunk_lenth=None, **kwargs):
        super(MetricModel, self).__init__()
        self.metric_num = metric_num
        self.out_dim = metric_hiddens[-1]
        in_dim = metric_num

        assert len(metric_hiddens) == len(metric_kernel_sizes)
        #self.net = ConvNet(num_inputs=in_dim, num_channels=metric_hiddens, kernel_sizes=metric_kernel_sizes,
        #                    dev=device, dropout=metric_dropout)
        self.net = ConvNet(num_inputs=in_dim, num_channels=metric_hiddens, kernel_sizes=metric_kernel_sizes,
                           dev=device)

        self.self_attn = self_attn
        if self_attn:
            assert (chunk_lenth is not None)
            self.attn_layer = SelfAttention(self.out_dim, chunk_lenth)

    
    def forward(self, x): #[bz, T, metric_num]
        assert x.shape[-1] == self.metric_num
        hidden_states = self.net(x)
        if self.self_attn: 
            return self.attn_layer(hidden_states)
        return hidden_states[:,-1,:] #[bz, out_dim]

class LogModel(nn.Module):
    def __init__(self, event_num, out_dim):
        super(LogModel, self).__init__()
        self.embedder = nn.Linear(event_num, out_dim) 
    def forward(self, paras: torch.tensor): #[bz, event_num]
        """
        Input:
            paras: mu with length of event_num
        """
        return self.embedder(paras)

class MultiSourceEncoder(nn.Module):
    def __init__(self, event_num, metric_num, node_num, device, log_dim=64, fuse_dim=64, alpha=0.5, **kwargs):
        super(MultiSourceEncoder, self).__init__()
        self.node_num = node_num
        self.alpha = alpha

        self.trace_model = TraceModel(device=device, **kwargs)
        trace_dim = self.trace_model.out_dim
        self.log_model = LogModel(event_num, log_dim) 
        self.metric_model = MetricModel(metric_num, device=device, **kwargs)
        metric_dim = self.metric_model.out_dim
        fuse_in = trace_dim+log_dim+metric_dim

        if not fuse_dim % 2 == 0: fuse_dim += 1
        self.fuse = nn.Linear(fuse_in, fuse_dim)

        self.activate = nn.GLU()
        self.feat_in_dim = int(fuse_dim // 2)

        
        self.status_model = GraphModel(in_dim=self.feat_in_dim, device=device, **kwargs)
        self.feat_out_dim = self.status_model.out_dim
    
    def forward(self, graph):
        #print("trace size:",graph.ndata["traces"].size())
        trace_embedding = self.trace_model(graph.ndata["traces"]) #[bz*node_num, T, trace_dim]
        log_embedding = self.log_model(graph.ndata["logs"]) #[bz*node_num, log_dim]
        metric_embedding = self.metric_model(graph.ndata["metrics"]) #[bz*node_num, metric_dim]

        # [bz*node_num, fuse_in] --> [bz, fuse_out], fuse_in: sum of dims from multi sources
        feature = self.activate(self.fuse(torch.cat((trace_embedding, log_embedding, metric_embedding), dim=-1))) #[bz*node_num, node_dim]
        embeddings = self.status_model(graph, feature) #[bz, graph_dim]
        return embeddings

class FullyConnected(nn.Module):
    def __init__(self, in_dim, out_dim, linear_sizes):
        super(FullyConnected, self).__init__()
        layers = []
        for i, hidden in enumerate(linear_sizes):
            input_size = in_dim if i == 0 else linear_sizes[i-1]
            layers += [nn.Linear(input_size, hidden), nn.ReLU()]
        layers += [nn.Linear(linear_sizes[-1], out_dim)]
        self.net = nn.Sequential(*layers)
        self.activation = nn.Sigmoid() 

    def forward(self, x: torch.Tensor): #[batch_size, in_dim]
        return self.activation(self.net(x)).squeeze() 

import numpy as np
class MainModel(nn.Module):
    def __init__(self, event_num, metric_num, node_num, device, normal_average, alpha=0.5, debug=False, **kwargs):
        super(MainModel, self).__init__()

        self.normal_average = normal_average
        self.device = device
        self.node_num = node_num
        self.alpha = alpha

        self.encoder = MultiSourceEncoder(event_num, metric_num, node_num, device, debug=debug, alpha=alpha, **kwargs)

        self.detecter = FullyConnected(self.encoder.feat_out_dim, 1, kwargs['detect_hiddens']).to(device)
        self.detecter_criterion = nn.BCELoss()
        #self.localizer = FullyConnected(self.encoder.feat_out_dim, node_num, kwargs['locate_hiddens']).to(device)
        #self.localizer_criterion = nn.CrossEntropyLoss(ignore_index=-1)
        #self.get_prob = nn.Softmax(dim=-1)

    def forward(self, graph, fault_indexs):
        batch_size = graph.batch_size

        embeddings = self.encoder(graph) #[bz, feat_out_dim]
        
        #y_prob: RCL ground_truth 
        y_prob = torch.zeros((batch_size, self.node_num)).to(self.device) 
        for i in range(batch_size):
            if fault_indexs[i] > -1: 
                y_prob[i, fault_indexs[i]] = 1

        #y_anomaly: AD ground_truth 
        y_anomaly = torch.zeros(batch_size).long().to(self.device)
        for i in range(batch_size):
            y_anomaly[i] = int(fault_indexs[i] > -1)

        #locate_logits = self.localizer(embeddings)
        #locate_loss = self.localizer_criterion(locate_logits, fault_indexs.to(self.device))

        detect_logits = self.detecter(embeddings)
        detect_loss = self.detecter_criterion(detect_logits, y_anomaly.float())

        #loss = self.alpha * detect_loss + (1-self.alpha) * locate_loss
        loss = detect_loss
        #node_probs: 각 노드(마이크로서비스)들의 RC일 확률 
        #node_probs = self.get_prob(locate_logits.detach()).cpu().numpy()
        
        y_pred, diff_lists, anomaly_indexs = self.inference(batch_size, graph, detect_logits)
        
        return {'loss': loss, 'y_pred': y_pred, 'y_prob': y_prob.detach().cpu().numpy()} #'pred_prob': node_probs}
        
    def inference(self, batch_size, graph, detect_logits): 
        y_pred = []
        diff_lists = []
        anomaly_indexs = []
        detect_pred = torch.where(detect_logits > 0.9, torch.tensor(1), torch.tensor(0))
        for i in range(batch_size):
            graph_list = dgl.unbatch(graph)

            if detect_pred[i] < 1: 
                y_pred.append([-1]) #anomaly 가 없으면 -1 값 

            else: #anomaly 가 있다면?
                anomaly_indexs.append(i)
                diff_list = []
                current_graph = graph_list[i]
                for j in range(self.node_num): # node 하나씩 제거해보기 
                    masked_graph = self.masking(current_graph, j) #노드 하나씩 제거하는 코드
                    masked_embeddings = self.encoder(masked_graph)
                    masked_detect_logit = self.detecter(masked_embeddings)

                    diff = detect_logits[i] - masked_detect_logit #original anomaly 확률 값 - masked anomaly 확률값의 차이, 이것이 클수록 mask된 노드가 RC일 확률 높음
                    diff_list.append(diff.item())
            

                temp = np.argsort(diff_list)[::-1]
                diff_lists.append(diff_list)
                y_pred.append(temp)


        return y_pred, diff_lists, anomaly_indexs
    
# j 번째 node feature를 normal state일때의 average값으로 변경
    def masking(self, graph, node_index):
        # 그래프 구조만 복제
        subgraph = graph.clone()

        # 각 데이터 항목에 대해 깊은 복사 수행
        subgraph.ndata['logs'] = copy.deepcopy(graph.ndata['logs'])
        subgraph.ndata['metrics'] = copy.deepcopy(graph.ndata['metrics'])
        subgraph.ndata['traces'] = copy.deepcopy(graph.ndata['traces'])

        # 변경하고자 하는 노드의 데이터를 업데이트
        subgraph.ndata['logs'][node_index] = self.normal_average['avg_logs'][node_index].clone()
        subgraph.ndata['metrics'][node_index] = self.normal_average['avg_metrics'][node_index].clone()
        subgraph.ndata['traces'][node_index] = self.normal_average['avg_traces'][node_index].clone()

        return subgraph
    

# # j 번째 node 삭제와, 해당 node와 관련된 edge들까지 삭제해야 함 
#     def masking(self, graph, node_index):
#         #j 번째 node 삭제 
#         unmaksed_index = list(range(self.node_num))
#         unmaksed_index.remove(node_index) 

#         # 남은 노드들로부터 새로운 서브그래프를 생성합니다.
#         subgraph = dgl.node_subgraph(graph, unmaksed_index)

#         return subgraph


    

        

        
