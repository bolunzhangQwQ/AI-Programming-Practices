import osmnx as ox
import numpy as np
import os
import gc
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

G = ox.graph_from_address('上海交通大学闵行校区', dist=10000, network_type='all')  # 获取道路数据
ox.plot_graph(G,bgcolor='white',node_color='blue',edge_color='grey',node_size=5,show=True)

origin_point = (31.023817,121.437439)  # 出发点经纬度
destination_point = (31.098595,121.446864)  # 终点经纬度

origin_node = ox.nearest_nodes(G, origin_point[1], origin_point[0])  # 获取出发点最邻近的道路节点
destination_node = ox.nearest_nodes(G, destination_point[1], destination_point[0])  # 获取终点最邻近的道路节点


#for node1, node2, data in G.edges(data=True):
    #print(data['length'])
#遍历，权重设为初始统一值
for node1, node2, data in G.edges(data=True):
    data['weight']=[data['length']/11.11]
#print(data['weight'])
#print(nx.get_edge_attributes(G,'length'))
taxi_trajectory_dict = dict()
error_list = []

def read_file(fname):
    with open(fname, 'r') as f:
        try:
            data = f.readlines()
            for i in range(len(data)):
                point_list = data[i].split('|')
                if point_list[1] == 'A' and point_list[2] == '0' and point_list[3] == '0' and (point_list[4] == '0' or point_list[4] == '1') and point_list[9][11] != ' ':
                    #print(point_list[8])
                    if point_list[8][11:16] not in taxi_trajectory_dict.keys():  #取出小时，分钟
                        taxi_trajectory_dict[str(point_list[8][11:16])] = []
                        taxi_trajectory_dict[str(point_list[8][11:16])].append(
                            [float(point_list[10]), float(point_list[11]),float(point_list[12])])   #[8]更改为[9]，对应时间,补充speed字段
                    else:
                        taxi_trajectory_dict[str(point_list[8][11:16])].append(
                            [ float(point_list[10]), float(point_list[11]), float(point_list[12])])
        except Exception as e:
            error_list.append([fname, e])
    print('finish ', fname)
    


count = 0
dir_list = ['07', '08', '09']#, '10', '11', '12', '13', '14', '15', '16', '17','18', '19', '20', '21', '22', '23']
for i in range(len(dir_list)):
    file_list = os.listdir("C:\\Users\\lenovo\\Desktop\\AI Programming Dataset\\AI Programming Dataset\\demo3_datagraph_process\\data\\taxi_data\\shanghai_20180401"+ "\\"+ dir_list[i])
    file_list = sorted(file_list)
    for file in file_list:
        file_name = "C:\\Users\\lenovo\\Desktop\\AI Programming Dataset\\AI Programming Dataset\\demo3_datagraph_process\\data\\taxi_data\\shanghai_20180401"+ "\\" + dir_list[i]+"\\"+ file
        read_file(file_name)
    gc.collect()
np.save('shanghai_taxi_spd_calculation_dict_byTime.npy', taxi_trajectory_dict)
np.savez('error_list.npz', error_list)
list1=list(taxi_trajectory_dict.keys())
i=list1[0]
for j in taxi_trajectory_dict[i]:
    if 121.3234<j[0]<121.5184 and 30.9482<j[1]<31.1153 and j[2]!=0:
        edge=ox.nearest_edges(G,j[0],j[1])
        G[edge[0]][edge[1]][0]['weight']=[G[edge[0]][edge[1]][0]['length']/(j[2]/3.6)]+G[edge[0]][edge[1]][0]['weight']
for node1, node2, data in G.edges(data=True):
    data['weight']=np.mean(data['weight'])
    #print(data['weight'])
    


#print(G.edges(data=True))
#print(origin_node)
#print(destination_node)
route = nx.shortest_path(G, origin_node, destination_node, weight='weight')  # 请求获取最短路径
#print(route)
distance = nx.shortest_path_length(G, origin_node, destination_node, weight='weight')  # 并获取路径长度
#可视化路网结果
fig, ax = ox.plot_graph_route(G,route, route_color='red',node_color='blue',bgcolor='white',edge_color='grey',node_size=5) 
#距离
print(str(distance))
#可视化图结果（小范围有效）
#pos = nx.spring_layout(G)
#nx.draw_networkx_edge_labels(G,pos,font_size=10)
#plt.figure(figsize=(50,70)) 
#nx.draw(G,node_size=50,arrowsize=10,font_size=10,width=5,with_labels=True)
#plt.show()
#映射至地图
G_84 = ox.projection.project_graph(G,to_crs='EPSG:4326')
ox.folium.plot_graph_folium(G_84,edge_linewidth=0.1,tiles='openstreetmap',kwargs={'width':0.1})