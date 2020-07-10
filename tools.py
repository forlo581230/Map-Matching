from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
import os
import math

def haversine(lat1, lon1, lat2, lon2): # 經度１，緯度１，經度２，緯度２（單位十進制度）
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # 將十進制度轉換成弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
 
    # haversine公式
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # 地球平均半徑，單位為公里
    return c * r * 1000  #  單位：公尺

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


def TimeTranslator(time, frame2sec):
    ## time: str, sec: int, return type(str)
    hr, minute, second = [int(i) for i in time.split(':')]
    if int((frame2sec+second)/60)+minute > 59:
        hr = int((int((frame2sec+second)/60)+minute)/60) + hr
        minute = (int((frame2sec+second)/60)+minute)%60
        second = (frame2sec+second)%60
    elif int(frame2sec+second) > 59:
        minute = int((frame2sec+second)/60)+minute
        second = (frame2sec+second)%60
    else:
        second = (frame2sec+second)
    t_str = ''
    for i in [hr, minute, second]:
        if i == 0:
            t_str = t_str+'00'
        elif i < 10:
            t_str = t_str+'0'+str(i)
        else:
            t_str = t_str+str(i)
        t_str = t_str+':'
    return t_str[:-1]

def WebCodeTranslator(data, video_list, predict_list, merge_video_info):  
    '''
    INPUT
        data: type(pd.DataFrame) 
    
    OUTPUT
        txt: type(String), Visual Web Code
    '''
    txt = ''
#     print(video_list)
#     input()
#     print(data)
#     input()
#     new_data = []
    for video_name in video_list:
        df_RawData = data.loc[data['video_name']==video_name]
#         print(df_RawData)
#         input()
        longitude = np.array(df_RawData['longitude'])
        latitude = np.array(df_RawData['latitude'])
        timing = np.array(df_RawData['time'])
        predict_list_2sec = [int(i/24) for i in predict_list]
#         print(predict_list_2sec)
        new_data = []
        
        ExitInts_RawPos = []
        for i in range(len(df_RawData)):
            
            if i in predict_list_2sec:
                pred_id = predict_list_2sec.index(i)
                pred = predict_list[pred_id]
               
                intd = int(pred/24)
                t = TimeTranslator('00:00:00', intd) + str((pred%24)/24)[1:]
                if intd >= len(latitude)-1:
                    lat = (latitude[intd]-latitude[intd-1])*(pred%24)/24 + \
                        latitude[intd]
                    lon = (longitude[intd]-longitude[intd-1])*(pred%24)/24 + \
                        longitude[intd]            
                else:
                    lat = (latitude[intd+1]-latitude[intd])*(pred%24)/24 + \
                        latitude[intd]
                    lon = (longitude[intd+1]-longitude[intd])*(pred%24)/24 + \
                        longitude[intd]
                ExitInts_RawPos.append([lat, lon])
                txt += 'L.marker(['+str(lat)+', '+str(lon)
                txt += '], {icon: goldIcon}).addTo(mymap).bindPopup'
                txt += '("{}.{};frame:{};{},{}").openPopup()'.format(TimeTranslator('00:00:00', intd), (pred%24)/24, pred, str(lat), str(lon))
                txt += ';\n'
                new_data.append([t, lat, lon])
                
            
            t = TimeTranslator('00:00:00', i)
            lat = latitude[i]
            lon = longitude[i]
            txt += 'L.marker(['+str(latitude[i])+', '+str(longitude[i])
            txt += ']).addTo(mymap).bindPopup'
            txt += '("{};;{},{}").openPopup()'.format(TimeTranslator('00:00:00', i), str(latitude[i]), str(longitude[i]))
            txt += ';\n'
                
            new_data.append([t, lat, lon])
        data_colnames_NewData = ['timestamp', 'lat', 'lon']          
        df_NewData = pd.DataFrame(new_data, columns=data_colnames_NewData)


    return txt, ExitInts_RawPos, df_NewData

    
    
    
#     txt = ''
#     for video_name in video_list:
#         d = data.loc[data['video_name']==video_name]
#         longitude = np.array(d['longitude'])
#         latitude = np.array(d['latitude'])
#         predict_list_2sec = [int(i/24) for i in predict_list]
# #         print(predict_list_2sec)
#         for i in range(len(d)):
#             txt += 'L.marker(['+str(latitude[i])+', '+str(longitude[i])
#             if i in predict_list_2sec:
# #                 print(TimeTranslator('00:00:00', i))
#                 txt += '], {icon: goldIcon}).addTo(mymap).bindPopup'
#                 txt += '("{};;{},{}").openPopup()'.format(TimeTranslator('00:00:00', i), str(latitude[i]), str(longitude[i]))
             
#             else:
#                 txt += ']).addTo(mymap).bindPopup'
#                 txt += '("{};;{},{}").openPopup()'.format(TimeTranslator('00:00:00', i), str(latitude[i]), str(longitude[i]))

#             txt += ';\n'
#     return txt
            
#         label = np.array(d['time'])
#         time_start = label[0]
#         time_string_list = []
#         count = 0
#         flag = -1
#         for p in predict_list:
#             while p > count:
#                 compare = count
#                 flag += 1
#                 count += merge_video_info[flag][1]
#             time_string_list.append(TimeTranslator(time_start, int((p-compare)/24)+flag*60))
#             print(flag, count, compare, TimeTranslator(time_start, int((p-compare)/24)+flag*60))
            
#         print(time_string_list)
#         longitude = np.array(d['longitude'])
#         latitude = np.array(d['latitude'])
#         for i in range(len(label)):
#             txt += 'L.marker(['+str(latitude[i])+', '+str(longitude[i])
#             popup_txt = TimeTranslator(time_start, i)
#             if label[i] in time_string_list:
#                 idx = time_string_list.index(label[i])
#                 print('idx: ', idx)
#                 txt += '], {icon: goldIcon}).addTo(mymap).bindPopup("'+TimeTranslator('00:00:00', int(predict_list[idx]/24))+'").openPopup()';
#             else:
#                 txt += ']).addTo(mymap).bindPopup("'+label[i]+'").openPopup()';
#             txt += ';\n'
#     return txt



def FillMissingGPSData(df_RawData):
    ## correct missing gps data
    data_colnames_RawData = ['timestamp', 'lat', 'lon']
    start_time = df_RawData.timestamp.values[0]
    end_time = df_RawData.timestamp.values[-1]
    current_time = start_time
    count = 0
    new_dict = []
    while TimeTranslator(current_time, 1) != end_time:
        if df_RawData.timestamp.values[count] == TimeTranslator(start_time, count):
            pass
        else:
            i = 0
            while TimeTranslator(start_time, count+i) != df_RawData.timestamp.values[count]:
                i += 1
#             print(TimeTranslator(start_time, count), i)
            lat = (df_RawData.lat.values[count]-df_RawData.lat.values[count-1])/(i+1) + \
                df_RawData.lat.values[count-1]
            lon = (df_RawData.lon.values[count]-df_RawData.lon.values[count-1])/(i+1) + \
                df_RawData.lon.values[count-1]
            list_RawData = df_RawData.values.tolist()
            list_RawData.insert(count, [TimeTranslator(start_time, count), lat, lon])
            df_RawData = pd.DataFrame(list_RawData, columns=data_colnames_RawData)
        current_time = TimeTranslator(start_time, count)
        count += 1
    return df_RawData

def GenGPX(df_RawData, save_name):
    ## 1. generate GPX file, 
    lat = df_RawData['lat'].values
    lon = df_RawData['lon'].values
    with open('./../data/GPXdata/template.gpx', 'r')as f:
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

def ReadGPX(filename, getWebCode):
    pass
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


