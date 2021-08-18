"""App entry point."""
from application import create_app

from config import (
    DBMS,
    DATABASE_HOST, DATABASE_PORT,
    DATABASE_USERNAME, DATABASE_PASSWORD,
    DATABASE_NAME
)

app = create_app(
    f'{DBMS}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
)

if __name__ == '__main__':
    from pstats import Stats, SortKey
    from cProfile import Profile

    # pr = Profile()
    # pr.enable()

    from werkzeug.middleware.profiler import ProfilerMiddleware
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30], profile_dir='.\\profile')
    app.run(host="0.0.0.0")
    #
    # pr.disable()
    # Stats(pr).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
