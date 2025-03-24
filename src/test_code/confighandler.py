import os.path
from typing import Optional, Union, Dict, List, Any
from config.json_handler import JsonHandler
from config.default_config import DEFAULT_CONFIG 
from cv import CameraInfo, Camera
import copy


class ConfigHandlerMeta(type):
    """
    A metaclass for creating a singleton PlayerInfo class.
    
    This ensures that only one instance of PlayerInfo exists throughout the application.
    """
    
    _instances = {}  # Dictionary to store the single instance of PlayerInfo

    def __call__(cls, *args, **kwargs):
        """
        Ensures that only one instance of the class exists.
        
        If an instance of the class does not exist, it creates one. 
        Otherwise, it returns the existing instance.

        Returns:
            PlayerInfo: The singleton instance of the class.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else: 
            if args:
                cls._instances[cls].load(*args)
        return cls._instances[cls]


class ConfigHandler(JsonHandler,  metaclass= ConfigHandlerMeta):
    """
    Handles the loading, saving, and updating of camera configurations in a JSON file.

    This class extends the `JsonHandler` class to provide additional functionality
    for managing camera configurations. It allows you to retrieve, add, or update
    camera configurations, and also read and validate configuration data.

    Attributes:
         json_file_path (str): The path to the JSON configuration file.
        config_data (dict): The configuration data loaded from the JSON file.
    """
    def __init__(self, path = '') -> None:
        """
        Initializes the ConfigHandler with the specified JSON file path.
        Args:
            path: The path to the JSON configuration file. Defaults to 'config.json'.

        """
        if path:
            super(ConfigHandler, self).__init__(path)
        else: 
            super(ConfigHandler, self).__init__()  
        
        self.json_default_data = copy.deepcopy(DEFAULT_CONFIG)
        if self.json_data:
            self.json_save_data = copy.deepcopy(self.json_data)
        else:
            self.json_save_data = copy.deepcopy(DEFAULT_CONFIG)
            self.json_data = copy.deepcopy(DEFAULT_CONFIG)
            
      

    def changed(self): 
        if self.json_data != self.json_save_data:
            print("Data Changed")
            return True
        else: 
            print("Data NOT Changed")
            return False
    
    def get_key_value_extended(self, keys: List[str], data: dict = None):
        
        if not data:
            if self.json_data:
                return self.get_key_value(keys)
            else:
                return self.get_key_value(keys, self.json_default_data)
        else:
            return self.get_key_value(keys,data)


    def set_key_value_extended(self, keys: List[str], new_value, as_backup = False) -> None:

        if as_backup: 
            json_data = self.json_save_data
        else:
            json_data = self.json_data
        self.set_key_value(keys,new_value,json_data)


    def restore_key_value(self, keys: List[str]):
        saved_value = self.get_key_value_extended(keys,self.json_save_data)
        old_value = self.get_key_value_extended(keys)

        if saved_value != old_value: 
            self.set_key_value(keys,old_value, self.json_save_data)

    def save_key_value(self, keys: List[str]):
        saved_value = self.get_key_value_extended(keys,self.json_save_data)
        old_value = self.get_key_value_extended(keys)
        if saved_value != old_value: 
            self.set_key_value(keys,saved_value)


#-------------------------
#---- Getter -------------
#-------------------------

    def get_camera_name(self, camera_idx: int): 
        return self.get_key_value_extended(['cameras',camera_idx,'name'])
    

    def get_camera_device_id(self, camera_idx: int):
        return self.get_key_value_extended(['cameras',camera_idx,'device_id'])

        
    def get_camera_chessboard_corner_x(self, camera_idx: int):
        return self.get_key_value_extended(['cameras',camera_idx,'chessboard', 'corners','X'])
        
    
    def get_camera_chessboard_corner_y(self, camera_idx: int):
        return self.get_key_value_extended(['cameras',camera_idx,'chessboard', 'corners','Y'])
      
    
    def get_camera_chessboard_resolution_x(self, camera_idx: int):
        return self.get_key_value_extended(['cameras',camera_idx,'chessboard', 'resolution','X'])

    def get_camera_chessboard_resolution_y(self, camera_idx: int):
        return self.get_key_value_extended(['cameras',camera_idx,'chessboard', 'resolution','Y'])
       
    def get_camera_calibration_matrix(self, camera_idx: int):
        return self.get_key_value_extended(['cameras',camera_idx,'calibration','camera_matrix'])
       
    
    def get_camera_calibration_dist_coefficient(self, camera_idx: int):
        return self.get_key_value_extended(['cameras',camera_idx,'calibration','dist_coeffs'])
       
#-------------------------
#---- Setter -------------
#-------------------------

    def set_camera_name(self, camera_idx: int, name: str, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'name'], name, as_backup)
    

    def set_camera_device_id(self, camera_idx: int, device_id: str, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'device_id'], device_id, as_backup)
        
    
    def set_camera_chessboard_corner_x(self, camera_idx: int, corners: int, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'chessboard', 'corners','X'], corners, as_backup)
        
    
    def set_camera_chessboard_corner_y(self, camera_idx: int, corners: int, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'chessboard', 'corners','Y'], corners, as_backup)
        
    
    def set_camera_chessboard_resolution_x(self, camera_idx: int, resolution: int, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'chessboard', 'resolution','X'], resolution, as_backup)
       
    
    def set_camera_chessboard_resolution_y(self, camera_idx: int, resolutions: int, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'chessboard', 'resolution','Y'], resolutions, as_backup)
        

    def set_camera_calibration_matrix(self, camera_idx: int, matrix, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'calibration','camera_matrix'], matrix, as_backup)
      
    
    def set_camera_calibration_dist_coefficient(self, camera_idx: int, coefficent, as_backup: bool = False):
        self.set_key_value_extended(['cameras',camera_idx,'calibration','dist_coeffs'], coefficent, as_backup)


#-------------------------
#---- Restore ------------
#-------------------------

    def resotre_camera_name(self, camera_idx: int): 
        self.restore_key_value(['cameras',camera_idx,'name'])
    

    def restore_camera_device_id(self, camera_idx: int):
        self.restore_key_value(['cameras',camera_idx,'device_id'])
        
    
    def restore_camera_chessboard_corner_x(self, camera_idx: int):
        self.restore_key_value(['cameras',camera_idx,'chessboard', 'corners','X'])
        
    
    def restore_camera_chessboard_corner_y(self, camera_idx: int):
        self.restore_key_value(['cameras',camera_idx,'chessboard', 'corners','Y'])
        
    
    def restore_camera_chessboard_resolution_x(self, camera_idx: int):
        self.restore_key_value(['cameras',camera_idx,'chessboard', 'resolution','X'])
       
    
    def restore_camera_chessboard_resolution_y(self, camera_idx: int):
        self.restore_key_value(['cameras',camera_idx,'chessboard', 'resolution','Y'])
        

    def restore_camera_calibration_matrix(self, camera_idx: int):
       self.restore_key_value(['cameras',camera_idx,'calibration','camera_matrix'])
      
    
    def restore_camera_calibration_dist_coefficient(self, camera_idx: int):
       self.restore_key_value(['cameras',camera_idx,'calibration','dist_coeffs'])


#-------------------------
#---- Save ------------
#-------------------------

    def save_camera_name(self, camera_idx: int): 
        self.save_key_value(['cameras',camera_idx,'name'])


    def save_camera_device_id(self, camera_idx: int):
        self.save_key_value(['cameras',camera_idx,'device_id'])
        

    def save_camera_chessboard_corner_x(self, camera_idx: int):
        self.save_key_value(['cameras',camera_idx,'chessboard', 'corners','X'])
        

    def save_camera_chessboard_corner_y(self, camera_idx: int):
        self.save_key_value(['cameras',camera_idx,'chessboard', 'corners','Y'])
        

    def save_camera_chessboard_resolution_x(self, camera_idx: int):
        self.save_key_value(['cameras',camera_idx,'chessboard', 'resolution','X'])
        

    def save_camera_chessboard_resolution_y(self, camera_idx: int):
        self.save_key_value(['cameras',camera_idx,'chessboard', 'resolution','Y'])
        

    def save_camera_calibration_matrix(self, camera_idx: int):
        self.save_key_value(['cameras',camera_idx,'calibration','camera_matrix'])
        

    def save_camera_calibration_dist_coefficient(self, camera_idx: int):
        self.save_key_value(['cameras',camera_idx,'calibration','dist_coeffs'])


if __name__ == '__main__':
    config = ConfigHandler()
    config.set_camera_chessboard_corner_x(0,20, as_backup= True)
    config.set_camera_chessboard_corner_x(0,20)
    config.restore_camera_chessboard_corner_x(0)

    print("pause")
