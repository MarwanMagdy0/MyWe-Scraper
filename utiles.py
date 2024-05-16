import json
import numpy as np
from datetime import datetime
import requests
import time, os
TARGET_DAYS = 30
target_in_seconds = TARGET_DAYS*24*60*60
PATH = os.path.dirname(os.path.realpath(__file__)) + "/"

QUOTA = 140 # GB
class JsonIt:
    def __init__(self, file_path, default = None):
        self.file_path = file_path
        if not os.path.isfile(self.file_path):
            if default is not None:
                self.save_data(default)
            else:
                self.save_data({})


    def save_data(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    def read_data(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)
        
    def __getitem__(self, key):
        data = self.read_data()
        return data[key]
    
    def __setitem__(self, key: str, value):
        data = self.read_data()
        data[key] = value
        self.save_data(data)
        
    def keys(self):
        data = self.read_data()
        return data.keys()
    

class Fitter:
    def __init__(self,x_axis,y_axis,power):
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.power = power
        self.coffs = np.polyfit(x_axis,y_axis,power)
    def sub(self,input_x_to_fit):
        fitted = []
        value = 0
        for idx,x in enumerate(input_x_to_fit):
            for powinv,coff in enumerate(self.coffs):
                value += coff * x**(self.power-powinv)
                if idx==0:
                    # print(f"coff of {powinv} : {coff}")
                    pass
            fitted.append(value)
            value = 0
        return fitted


def is_connected_to_internet():
    try:
        if requests.get('https://google.com').ok:
            return True
    except:
        return False

def timestamp2date(timestamp):
    date_of_value = datetime.fromtimestamp(int(timestamp))
    date_of_value = str(date_of_value.strftime("%Y-%m-%d %I:%M %p"))
    return date_of_value

def get_params(time_value : dict):
    """
    this function returns the first value in the time_value
    also the coordinates of the last predicted value from usages
    also the predection of the end date
    """
    timestamps = [int(ts) for ts in time_value.keys()]
    usages = list(time_value.values())
    if len(timestamps)<=1:
        return [[timestamps, usages], [0,0], None, len(timestamps)]
    
    fitter = Fitter(timestamps, usages, 1)
    zero_date = timestamp2date(-fitter.coffs[1]/fitter.coffs[0]) # the date at which it is predicted that the internet will end at
    last_prediction = fitter.coffs[0] * timestamps[-1] + fitter.coffs[1]
    target_slop = -max(QUOTA,usages[0])/(target_in_seconds)
    target_intercepted = -(timestamps[0] + (target_in_seconds)) * target_slop
    return [[timestamps, usages], [target_slop, target_intercepted], last_prediction, zero_date]

if __name__ == "__main__":
    print(is_connected_to_internet())