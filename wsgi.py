import os

os.environ["DEBUG"] = "1"

from raspapreco.app import app

if __name__ == "__main__":
    app.run()
