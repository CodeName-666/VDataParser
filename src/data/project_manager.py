from pathlib import Path
from .json_handler import JsonHandler   
from .base_data import BaseDataMeta




class ProjectManager(JsonHandler, metaclass=BaseDataMeta):
    """
    ProjectManager is a class that manages project data, including loading and saving project files.
    It uses JsonHandler for JSON operations and BaseDataMeta for metadata management.
    """ 

    def __init__(self, project_path: str | Path = "", file_name: str = "project.json"):
        """
        Initializes the ProjectManager with a specified project path and file name.
        
        :param project_path: The path to the project directory.
        :param file_name: The name of the project file.
        """
        super().__init__(project_path, file_name)
        





