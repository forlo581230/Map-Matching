import numpy as np
import os
import math
import sys
import glob
# sys.path.append('..')\n",
from tools import haversine, CSVReader_GPS, TimeTranslator, WebCodeTranslator, FillMissingGPSData
from methods import GenGPX, ReadGPX, GraphHopper, SearchNodeID, OrthogonalProjection, VectorsAngle, MapMatching, CSVReader_GPS


from flask import Flask, request, jsonify, Response
import pandas as pd
import json

app = Flask(__name__)
# app.config["DEBUG"] = True


@app.route('/getMapMatch', methods=['POST'])
def home():
    data = request.json
    # print(data)
    data_list = []
    for item in data['latlonList']:
        data_list.append([item['lat'],item['lon']])

    ## RawData Visualization
    txt = ''
    txt_name = 'RawData.txt'
    for i, nd in enumerate(data_list):
        # if n == 2:
        #     txt += 'L.marker(['+str(nd[0])+', '+str(nd[1]) +'], {icon: blueIcon}).addTo(mymap).bindPopup("'+str(i)+'").openPopup()'
        # else:
        txt += 'L.marker(['+str(nd[0])+', '+str(nd[1]) +'], {icon: redIcon}).addTo(mymap).bindPopup("'+str(i)+'").openPopup()'
        txt += ';\n'
    
    # if not os.path.exists('./test_omnieyes/WebVisualizeCode/'):
    #     os.makedirs('./test_omnieyes/WebVisualizeCode/')
    # with open(os.path.join('./test_omnieyes/WebVisualizeCode/', txt_name), 'w') as f:
    #     f.write(txt)
    # print(os.path.join('./test_omnieyes/WebVisualizeCode/', txt_name), ' saved...')



    ## convert GPS data to Pandas:DataFrame Format
    data_colnames_RawData = ['lat', 'lon']
    df_RawData = pd.DataFrame(data_list, columns=data_colnames_RawData)

    # print(df_RawData[df_RawData.timestamp == '02:03:06'])
#     print('len(df_RawData): ', len(df_RawData))
    
    
    gpx_save_name = os.path.join('./GPXdata/', 'test.gpx')
    # Nd_trackpoint = GenGPX(df_RawData, save_name=gpx_save_name)

    try:
        os.remove(gpx_save_name)
        os.system('rm ~/hs_err_pid*.log')
    except OSError as e:
        print(e)
    else:
        print("File is deleted successfully")
        
    ## Gen NewData 
    Nd_trackpoint = GenGPX(df_RawData, save_name=gpx_save_name)

    ## cal. slope
    # slope_start = (Nd_trackpoint[1][1]-Nd_trackpoint[0][1]) / (Nd_trackpoint[1][0]-Nd_trackpoint[0][0])
    # slope_end = (Nd_trackpoint[-1][1]-Nd_trackpoint[-2][1]) / (Nd_trackpoint[-1][0]-Nd_trackpoint[-2][0])
    # print('slope_start, slope_end: ', slope_start, slope_end)
    Nd_trajectory, isMatching = MapMatching(gpx_save_name, './GPXdata/temp.gpx')  

    if isMatching:    
        # print('Nd_trajectory: ', Nd_trajectory)
        data_colnames_trajectory = ['lat', 'lon']
        Df_trajectory = pd.DataFrame(Nd_trajectory, columns=data_colnames_trajectory)
        if not os.path.exists('./test_omnieyes/DF_CSV/'):
            os.makedirs('./test_omnieyes/DF_CSV/')
        Df_trajectory.to_csv(os.path.join('./test_omnieyes/DF_CSV/', '_Df_trajectory.csv'), index=0)

        print()
        ## determine distance
        total_dist = 0
        for i in range(len(Nd_trajectory)-1):
            dist = haversine(Nd_trajectory[i][0], Nd_trajectory[i][1], Nd_trajectory[i+1][0], Nd_trajectory[i+1][1])
            total_dist += dist
        print('gps_csv name: ', 'gps_csv')
        print('number of RawData points: ', len(data_list))
        print('number of map matching nodes: ', len(Nd_trajectory))
        print('total_dist: {} km'.format(total_dist/1000))
        
        
        txt = ''
        txt_name = '_trajectoryNode.txt'
        for i, nd in enumerate(Nd_trajectory):
            # if n == 2:
            #     txt += 'L.marker(['+str(nd[0])+', '+str(nd[1]) +'], {icon: blueIcon}).addTo(mymap).bindPopup("'+str(i)+'").openPopup()'
            # else:
            txt += 'L.marker(['+str(nd[0])+', '+str(nd[1]) +'], {icon: blueIcon}).addTo(mymap).bindPopup("'+str(i)+'").openPopup()'
            txt += ';\n'
        # with open(os.path.join('./test_omnieyes/WebVisualizeCode/', txt_name), 'w') as f:
        #     f.write(txt)
        # print(os.path.join('./test_omnieyes/WebVisualizeCode/', txt_name), ' saved...')
        # print('-------------------------------------')


        ## convert GPS data to Pandas:DataFrame Format\n",


        data_colnames_RawData = ['lat', 'lon']

        df_RawData = pd.DataFrame(Nd_trajectory, columns=data_colnames_RawData)
        # print((df_RawData.to_json(orient='records')))
        # return jsonify(df_RawData.to_json(orient='records'))

        ret_json = {
            'success':True,
            'rawData_points' : len(data_list),
            'map_matching_nodes' : len(Nd_trajectory),
            'total_dist' : total_dist/1000,
            'data' : json.loads(df_RawData.to_json(orient='records'))
        }
    else:
        ret_json = {
            'success':False,
            'rawData_points' : 0,
            'map_matching_nodes' : 0,
            'total_dist' : 0,
            'data' : []
        }

    # print(ret_json)
    return Response(json.dumps(ret_json), mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)