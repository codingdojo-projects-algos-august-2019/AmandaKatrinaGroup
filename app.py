from config import app
import routes
from models import User, Blog, Comment

if __name__ == "__main__":
    app.run(debug=False)
