import base64
import json
import zlib


class Blueprint:
    @staticmethod
    def import_blueprint(string):
        return json.loads(
            str(zlib.decompress(
                base64.b64decode(string[1:]), wbits=0), 'utf-8'
                ))

    @staticmethod
    def export_blueprint(blueprint):
        return "0" + str(base64.b64encode(
            zlib.compress(
                json.dumps(blueprint, separators=(',', ':')).encode('utf-8'), 9)
        ), 'utf-8')

    @staticmethod
    def empty():
        return {
            "blueprint": {
                "entities": [],
                "icons": [],
                "item": "blueprint",
                "version": 73016672256
            }
        }
