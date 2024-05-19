from datetime import datetime
import numpy as np
import traceback
import requests
import time, os
import logging
import json
import sys
TARGET_DAYS = 30
target_in_seconds = TARGET_DAYS*24*60*60
PATH = os.path.dirname(os.path.realpath(__file__)) + "/"

QUOTA = 140 # GB
class JsonIt:
    """A class for handling JSON files - creating, reading, and editing."""
    def __init__(self, file_path, default = None):
        """_summary_

        Args:
            file_path (str): The path to the JSON file. if not found it will be created
            default (dict, optional): Default data to save if the file doesn't exist. Defaults to None.
        """
        self.file_path = file_path
        if not os.path.isfile(self.file_path):
            if default is not None:
                self.save_data(default)
            else:
                self.save_data({})


    def save_data(self, data):
        """
        Save data to the JSON file.

        Args:
            data (dict): The data to be saved.
        """
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    def read_data(self):
        """
        Read data from the JSON file.

        Returns:
            dict: The data read from the file.
        """
        with open(self.file_path, 'r') as f:
            return json.load(f)
        
    def __getitem__(self, key):
        """
        Get an item from the data using its key.

        Args:
            key (str): The key of the item to retrieve.

        Returns:
            Any: The value corresponding to the key.
        """
        data = self.read_data()
        return data[key]
    
    def __setitem__(self, key: str, value):
        """
        Set a value in the data using its key.

        Args:
            key (str): The key of the item to set.
            value (Any): The value to set for the key.
        """
        data = self.read_data()
        data[key] = value
        self.save_data(data)
        
    def keys(self):
        """
        Get all keys present in the data.

        Returns:
            dict_keys: A view object providing a dynamic view of all keys.
        """
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

class Logger:
    @staticmethod
    def logIntoFile(file_name):
        # Create the root logger and set its level to DEBUG
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        
        # Create a file handler and set its level to INFO
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Create a console handler and set its level to INFO
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Set custom exception hook to handle uncaught exceptions
        sys.excepthook = Logger.handle_exception

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        # Log unhandled exceptions with traceback
        logging.error(f'Unhandled exception: {exc_type.__name__}: {exc_value}')
        logging.error("".join(traceback.format_tb(exc_traceback)))

Logger.logIntoFile(PATH + "logg.log")

if __name__ == "__main__":
    print(is_connected_to_internet())