import os
import math
import numpy as np
import pandas as pd
import subprocess

def GenGPX(df_RawData, save_name):
    ## 1. generate GPX file, 
    lat = df_RawData['lat'].values
    lon = df_RawData['lon'].values
    with open('./GPXdata/template.gpx', 'r')as f:
        txt = f.readlines()
    Nd_trackpoint = []
    with open(save_name, 'w') as f:
        f.writelines(txt)
        for i in range(len(lat)):
            line = '<trkpt lat=\"'+ str(lat[i]) +'\" lon=\"' + str(lon[i]) + '\"><time></time></trkpt>\n'
            Nd_trackpoint.append([lat[i], lon[i]])
            f.write(line)
        f.write('</trkseg>\n</trk>\n</gpx>\n')
        print(save_name + ' saved...')
    return Nd_trackpoint
def ReadGPX(filename, getWebCode=False):
    '''
    INPUT 
        filename: type(String), './filepath/filename.gpx'
        getWebCode: type(Bool), if u want to show results on the website, print the JS code
    OUTPUT
        Nd_trajectory: type([[lat, lon], ...])
        visualweb_code: code       
    '''
    visualweb_code = ''
    Nd_trajectory = []
    if '.res.gpx' in filename:
        lastone_count_ornot = 4
    else:
        lastone_count_ornot = 3
    with open(filename, 'r') as f:
        txt = f.readlines()    
        for i in range(3, len(txt)-lastone_count_ornot):
            word = txt[i].split('"')
            lat = word[1]
            lon = word[3]
            Nd_trajectory.append([float(lat), float(lon)])
            if getWebCode:
                visualweb_code += 'L.marker(['+ lat +', '+ lon + '], {icon: goldIcon}).addTo(mymap).bindPopup("''").openPopup()\n'        
    return Nd_trajectory, visualweb_code


def GraphHopper(gpxfile):
    # !bash ./mm.sh {gpxfile}
    process = subprocess.Popen(('bash ./mm.sh ' + gpxfile).split(), stdout=subprocess.PIPE)
    process.wait()
    output, error = process.communicate()
    
    rows = len(output.decode().split('\n'))
    
    if rows >=8:
        return True
    else:
        return False

def SearchNodeID(df_Node, pos):
    '''
    INPUT
        df_Node: Nodes info, type(pd.dataframe)
        pos: type([[lat, lon], ...])
    OUTPUT
        nodeID: type([int, ...]), or None
    '''
    IDList = []
    print('input position: ', pos)
    for pid in range(len(pos)):
        NodeID = None
        lat = pos[pid][0]
        lon = pos[pid][1]
        for i in range(len(df_Node)):
            if math.fabs(df_Node.iloc[i].lat-pos[pid][0]) < 0.00001:
                if math.fabs(df_Node.iloc[i].lon-pos[pid][1]) < 0.00001:
                    NodeID = df_Node.iloc[i].node
                    lat = df_Node.iloc[i].lat
                    lon = df_Node.iloc[i].lon
                    break
        IDList.append([NodeID, lat, lon])
#     print('IDList: ', IDList)
    return IDList
    
def OrthogonalProjection(AB, AP):
    ## projection
    PROJ = (np.dot(AB, AP) / np.dot(AB, AB)) * AB
    return PROJ

def VectorsAngle(A, B):
    ## /pi *180
    return math.acos(np.dot(A, B) / np.sqrt(np.dot(A, A)*np.dot(B, B)))
    
    
def MapMatching(gpxfile, tempfile):
    pass
    data, _ = ReadGPX(gpxfile)
    data_colnames_RawData = ['lat', 'lon']
    NofSeg = 300000
    NofCover = 30
    Nd_trajectory = []
    iters = math.ceil(max((len(data)-NofSeg), 0)/(NofSeg-NofCover)) + 1
#     print(iters)
    ## split gpx data
    for i in range(iters):
        if i != iters-1:
            raw_data = pd.DataFrame(data[(NofSeg-NofCover)*i:(NofSeg-NofCover)*i+NofSeg], columns=data_colnames_RawData)
            GenGPX(raw_data, tempfile)
            print('input points: {}~{}'.format((NofSeg-NofCover)*i, (NofSeg-NofCover)*i+NofSeg))
        else:
            raw_data = pd.DataFrame(data[(NofSeg-NofCover)*i:], columns=data_colnames_RawData)
            GenGPX(raw_data, tempfile)
            print('input points: {}~{}'.format((NofSeg-NofCover)*i, len(data)-1))

        ## Do MapMatching through GraphHopper
        isMatching = GraphHopper(tempfile)
        
        ## Read Mapping results
        nodes, _ = ReadGPX(tempfile+'.res.gpx')
#         print(Nd_trajectory)
        if len(Nd_trajectory) != 0:
#             if Nd_trajectory[-1] == nodes[0]:
#                 Nd_trajectory.extend(nodes[1:])
#             else:
#                 Nd_trajectory.extend(nodes)
            for nd in nodes:
#                 print(nd)
#                 input()
                if nd in Nd_trajectory:
                    pass
                else:
                    Nd_trajectory.extend([nd])
        else:
            Nd_trajectory.extend(nodes)
            
    return Nd_trajectory, isMatching

def CSVReader_GPS(data, video_list):           
    raw_data = [] 
    for video_name in video_list:
        d = data.loc[data['video_name']==video_name]
        label = np.array(d['time'])
        longitude = np.array(d['longitude'])
        latitude = np.array(d['latitude'])
        for i in range(len(label)):
            raw_data.append([label[i], latitude[i], longitude[i]])
    return raw_data
