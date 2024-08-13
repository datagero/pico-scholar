#!/usr/bin/env python3

import connexion

from swagger_server import encoder


def main(test=False):
    if test:
        app = connexion.App(__name__, specification_dir='./swagger-test/')
    else:
        app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Research Project API'}, pythonic_params=True)
    app.run(port=8080)


if __name__ == '__main__':
    main(test=True)
