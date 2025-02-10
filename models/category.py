from datetime import datetime

class Category:
    def __init__(self, name, image, imageKey):
        self.name = name
        self.image = image
        self.imageKey = imageKey
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            'name': self.name,
            'image': self.image,
            'imageKey': self.imageKey,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 