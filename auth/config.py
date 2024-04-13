class Config:
    SECRET_KEY = 'my-secret-key'
    JWT_SECRET_KEY = 'my-jwt-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
