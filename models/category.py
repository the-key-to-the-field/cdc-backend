from datetime import datetime

class Category:
    # Class-level set to store unique category names
    _names = set()

    def __init__(self, name, image, imageKey):
        if name in Category._names:
            raise ValueError(f"Category name '{name}' already exists.")
        self.name = name
        Category._names.add(name)
        
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