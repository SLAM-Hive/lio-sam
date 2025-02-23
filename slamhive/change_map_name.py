import os
import time


folder_path = "/root/catkin_ws/pcd/"  # 更改为你要监视的文件夹路径
files = os.listdir(folder_path)
os.rename(folder_path+files[0], "/root/catkin_ws/pcd/Map.pcd")