import yaml, time, subprocess
from string import Template
# Generate mappingtask.yaml according to template.yaml and config.yaml
config_raw = open("/slamhive/config.yaml",'r',encoding="UTF-8").read()
config_dict = yaml.load(config_raw, Loader=yaml.FullLoader)
algo_dict = config_dict["algorithm-parameters"]
datatset_dict = config_dict["dataset-parameters"]
all_dict = {}
for key, value in algo_dict.items():
    all_dict.update({key: value})
for key, value in datatset_dict.items():
    all_dict.update({key: value})
template_raw = Template(open("/slamhive/template.yaml",'r',encoding="UTF-8").read())
# template = template_raw.safe_substitute(config_parsed)#Replaces existing dictionary values, preserving non-existing replacement symbols.
template = template_raw.substitute(all_dict)#An exception occurs when all parameter values required by the template are not provided.
# Write template to mappingtask.yaml
with open("/slamhive/mappingtask.yaml","w") as f:
    f.write(template)

# Read algorithm-remap from config.yaml for mono.launch
algo_remap_dict = config_dict["algorithm-remap"]
algo_remap_list = []
if(algo_remap_dict is not None):
    for key, value in algo_remap_dict.items():
        algo_remap_list.append(key + ":=" + value)
algo_remap = ' '.join(algo_remap_list)


general_dict = config_dict["general-parameter"]
save_map = False
if general_dict is not None:
    for key, value in general_dict.items():
        if key == "save_map":
            if value == 1 or value == "1":
                save_map = True



print("Begin")
roslaunch_command = "roslaunch /slamhive/liosam.launch"
# subprocess.run("bash -c 'source /opt/ros/kinetic/setup.bash;  \
#                 source /root/catkin_ws/devel/setup.bash; \
#                 roscore'", shell=True)
# subprocess.run("bash -c 'source /opt/ros/kinetic/setup.bash;  \
#                 source /root/catkin_ws/devel/setup.bash; \
#                 rosbag record -O traj /lio_sam/mapping/odometry'", shell=True)




subprocess.run("bash -c 'source /opt/ros/kinetic/setup.bash;  \
                source /root/catkin_ws/devel/setup.bash; "
                + roslaunch_command 
                + " & sleep 10s ;'", shell=True)


subprocess.Popen("bash -c 'source /opt/ros/kinetic/setup.bash;  \
                source /root/catkin_ws/devel/setup.bash; "
                + " mkdir /root/catkin_ws/pcd ;\
                cd /root/catkin_ws/pcd ;\
                rosrun pcl_ros pointcloud_to_pcd input:=/lio_sam/mapping/map_global;'", shell=True)


subprocess.Popen("bash -c 'source /opt/ros/kinetic/setup.bash;  \
                source /root/catkin_ws/devel/setup.bash; "
                + " python3 /slamhive/pcd_monitor.py'", shell=True)

subprocess.run("bash -c 'source /opt/ros/kinetic/setup.bash;  \
                source /root/catkin_ws/devel/setup.bash; \
                python3 /slamhive/dataset/rosbag_play.py; \
                rosnode kill -a ; \
                sleep 1s; \
                python3 /slamhive/change_map_name.py; \
                python /slamhive/BAG2TUM.py; \
                mv /root/catkin_ws/traj.txt /slamhive/result/traj.txt;'", shell=True)


if save_map :
    subprocess.run("bash -c 'mv /root/catkin_ws/pcd/Map.pcd /slamhive/result/Map.pcd;'", shell=True)
subprocess.run("bash -c 'touch /slamhive/result/finished ;'", shell=True)
