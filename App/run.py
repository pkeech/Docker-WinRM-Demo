## Import Flask App
from src import create_app

## Start Application
app = create_app()

## USWIGI
if __name__ == "__main__":
    app.run()