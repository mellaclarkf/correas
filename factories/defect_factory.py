from models.defect import Defect

class DefectFactory:
    @staticmethod
    def create_from_row(row):
        return Defect(*row)

