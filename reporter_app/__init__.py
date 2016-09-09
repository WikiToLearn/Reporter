from flask import Flask

app = Flask(__name__,instance_relative_config=True)
app.config.from_object('reporter_app.config')

import reporter_app.reporter_ui
