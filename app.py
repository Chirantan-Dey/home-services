from . import create_app
import os
flask_app = create_app()
if __name__ == '__main__':
    
    flask_app.run(host='0.0.0.0', port=8080, debug=True)