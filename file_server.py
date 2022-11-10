import os
from app import create_app, db

# 创建应用
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db
    )


@app.cli.command()
def test():
    """单元测试"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
