import pymysql
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pylab as pl
from pylab import mpl
import warnings
warnings.filterwarnings("ignore")
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus']=False


#-------------用户样本特征---------------
def plot_user_distribution():
    '''
    对所有用户的特征进行统计
    '''
    conn = pymysql.connect(host='localhost', user='root', password='123456',
                        port=3306, db='bilibili')

    user_data = pd.read_sql('select * from userdata where follower > 1500000', conn)  
    conn.close()
    # 用户特征分类
    feature_list = ['following', 'follower', 'level']
    
    # 用户性别比率
    gender_dic = {"男":0,"女":0,"保密":0}
    for gender in user_data["sex"]:
        if gender == '男':
            gender_dic["男"] = gender_dic["男"] + 1
        elif gender == '女':
            gender_dic["女"] = gender_dic["女"] + 1
        else:
            gender_dic["保密"] = gender_dic["保密"] + 1
    plt.title("用户性别比率")
    plt.pie(gender_dic.values(), labels=gender_dic.keys())
    plt.show()

    for feature in feature_list:    
        pl.figure(feature)
        pl.title(feature)
        pl.xlabel("users")
        pl.ylabel("number of "+feature)
        user = list(range(len(user_data)))

        #对用户特征的数目进行排序
        feature_value = sorted(list(user_data[feature]), reverse=True)
        pl.scatter(user, feature_value)
        print("所有用户{feature}特征的平均数是:".format(feature = feature),np.mean(list(user_data[feature])))
        print("所有用户{feature}特征的中位数是:".format(feature = feature),np.median(list(user_data[feature])))
        print("所有用户{feature}特征的标准差是:".format(feature = feature),np.std(list(user_data[feature])))
        print("---------------------------------------------")
        pl.savefig('所有用户的{feature}特征分布'.format(feature = feature))

        pl.show()
    

#--------------网络特征-------------

def network_structure():
    # 图结构初始化
    conn = pymysql.connect(host='localhost', user='root', password='123456',
                            port=3306, db='bilibili')

    fanid = pd.read_sql(
        """select fanid from user_fans WHERE mid in (
                select mid from userdata where follower > 1500000
            )""", conn)

    mid = pd.read_sql(
        """select mid from user_fans WHERE mid in (
            select mid from userdata where follower > 1500000
        )""", conn)

    name = pd.read_sql("select mid,name from userdata", conn)
    conn.close()
    name_dic = {}

    for i in range(len(name)):
        name_dic[name['mid'][i]] = name['name'][i]

    G = nx.Graph()
    for i in range(len(mid)):
        G.add_edge(name_dic[fanid['fanid'][i]],name_dic[mid['mid'][i]])



    # 网络度分布
    degree=nx.degree_histogram(G)
    x=range(len(degree))
    y=[z/float(sum(degree))for z in degree]  # 将频次转化为频率
    plt.title('网络度分布')
    plt.scatter(x,y)
    plt.show()

    # 聚类系数
    centrality = nx.degree_centrality(G)
    x=range(len(centrality))
    y = centrality.values()
    plt.title('聚类系数')
    plt.scatter(x,y)
    plt.show()

    # 图的密度
    print('图的密度:', nx.density(G))

    # 网络直径
    G_child=list(G.subgraph(c) for c in nx.connected_components(G))
    cnt = 1
    for g in G_child:
        print('连通子网络%d的直径:' % cnt, nx.diameter(g))
        cnt = cnt+1


#------------用户影响力发掘---------------

def get_user_rank():
    # 图结构初始化
    conn = pymysql.connect(host='localhost', user='root', password='123456',
                            port=3306, db='bilibili')

    fanid = pd.read_sql(
        """select fanid from user_fans WHERE mid in (
                select mid from userdata where follower > 1500000
            )""", conn)

    mid = pd.read_sql(
        """select mid from user_fans WHERE mid in (
            select mid from userdata where follower > 1500000
        )""", conn)

    name = pd.read_sql("select mid,name from userdata", conn)
    conn.close()
    name_dic = {}

    for i in range(len(name)):
        name_dic[name['mid'][i]] = name['name'][i]

    G = nx.DiGraph()
    cnt = 0
    for i in range(len(mid)):
        G.add_edge(name_dic[fanid['fanid'][i]],name_dic[mid['mid'][i]])
        cnt += 1

    print('网络中边的数量', cnt)
    pl.figure()
    d = dict(G.degree)
    nx.draw(G, with_labels=True, node_size=[v * 100 for v in d.values()], style='dotted')
    pl.show()

    # PageRank
    pr = nx.pagerank(G)
    prsorted = sorted(pr.items(), key=lambda x: x[1], reverse=True)
    print('基于pagerank算法的用户影响力前10名\n')
    for p in prsorted[:10]:
        print(p[0], p[1])
    print("----------------------------------------\n")
    # HITS
    hub, auth = nx.hits(G)
    print('基于HITS(hub)算法的用户影响力前10名\n')
    for h in sorted(hub.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(h[0], h[1])
    print("----------------------------------------\n")
    
    print('基于HITS(auth)算法的用户影响力前10名\n')    
    for a in sorted(auth.items(), key=lambda x: x[1], reverse=True)[:10]:     
        print(a[0], a[1])



if __name__ == '__main__':

    '''
    用户统计
    '''
    plot_user_distribution()

    '''
    网络性质
    '''
    get_user_rank()
    network_structure()