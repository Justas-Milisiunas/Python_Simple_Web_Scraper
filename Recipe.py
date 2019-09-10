class Recipe:
    def __init__(self, name, products, steps, portionsAmount,
                 preparationTime, description, viewCount, rating,
                 votesCount, photos, tags):
        self.name = name
        self.products = products
        self.steps = steps
        self.portions_amount = portionsAmount
        self.preparation_time = preparationTime
        self.description = description
        self.viewCount = viewCount
        self.rating = rating
        self.votesCount = votesCount
        self.photos = photos
        self.tags = tags