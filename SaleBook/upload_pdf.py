import cloudinary.uploader
cloudinary.config(
    cloud_name='drzc4fmxb',
    api_key='422829951512966',
    api_secret='ILJ11vG7Q7OqbjxyhWS1lNJMN5U'
)
response = cloudinary.uploader.upload(
    '/Users/lehoangphuc/Downloads/source-book.pdf',  # Đường dẫn đến file PDF trong máy
    resource_type='raw'
)
print(response['url'])  # In ra URL