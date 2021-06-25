import os
from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='routes/templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'wuxia.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from wuxia.routes import auth
    app.register_blueprint(auth.bp)

    from wuxia.routes import users
    app.register_blueprint(users.bp)

    from wuxia.routes import story
    app.register_blueprint(story.bp)

    from wuxia.routes import misc
    app.register_blueprint(misc.bp)

    from wuxia.routes import challenges
    app.register_blueprint(challenges.bp)

    from wuxia import errors

    # from . import validation
    # validation.init_app(app)

    # Add custom jinja2 filters
    app.jinja_env.filters['basename'] = os.path.basename

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
