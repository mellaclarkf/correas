from strategies.exe_data_loader_strategy import ExeDataLoadStrategy
from strategies.excel_data_loader_strategy import ExcelDataLoadStrategy
from strategies.txt_data_loader_strategy import TxtDataLoadStrategy
from strategies.db_data_loader_strategy import DBLoader
from strategies.video_data_loader_strategy import VideoLoaderStrategy


class DataLoadFactory:
    def __init__(self, boundingbox_service=None, historial_repository=None, images_folder=None):
        self.boundingbox_service = boundingbox_service
        self.historial_repository = historial_repository
        self.images_folder = images_folder

    def get_data_loader(self, source_type):
        if source_type == "exe":
            return ExeDataLoadStrategy()
        elif source_type == "excel":
            return ExcelDataLoadStrategy()
        elif source_type == "txt":
            return TxtDataLoadStrategy()
        elif source_type == "db":
            return DBLoader()
        elif source_type == "video":
            # Pasar los parámetros pero NO inicializar VideoService todavía
            return VideoLoaderStrategy(
                self.boundingbox_service,
                self.historial_repository,
                self.images_folder
            )
        else:
            raise ValueError(f"Unknown data source type: {source_type}")
