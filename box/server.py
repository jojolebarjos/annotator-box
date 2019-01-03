# -*- coding: utf-8 -*-


import aiohttp
from aiohttp import web
import argparse
import asyncio
import concurrent.futures
import io
import os

from .data import Data


# Local resources
HERE = os.path.dirname(os.path.realpath(__file__))
INDEX_HTML = os.path.join(HERE, 'index.html')
D3_JS = os.path.join(HERE, 'd3.v4.min.js')


# Handler factory for static files
def static_handler(path):
    async def handler(request):
        return web.FileResponse(path)
    return handler


# Acquire sample
async def get_api_annotation(request):
    data = request.app['data']
    payload = await data.get_next_sample()
    return web.json_response(payload)


# Save annotation result
async def post_api_annotation(request):
    data = request.app['data']
    payload = await request.json()
    result = await data.add_annotation(payload)
    return web.json_response(result)


# Run service
def run(host, port, metadata_path, image_folder, annotation_path):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        
        # Create application
        app = web.Application()
        app.add_routes([
            web.get('/', static_handler(INDEX_HTML)),
            web.get('/d3.v4.min.js', static_handler(D3_JS)),
            web.get('/api/annotation', get_api_annotation),
            web.post('/api/annotation', post_api_annotation)
        ])
        app['executor'] = executor
        app['data'] = Data(metadata_path, image_folder, annotation_path, executor)
        app['annotation_path'] = annotation_path
        
        # Start server
        runner = web.AppRunner(app)
        loop = asyncio.get_event_loop()
        async def start():
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()
        loop.run_until_complete(start())
        print(f'Running on {host}:{port}')
        
        # Run forever (hack to avoid blocking select on Windows with default loop)
        async def foo():
            while True:
                await asyncio.sleep(1.0)
        try:
            loop.run_until_complete(foo())
        except KeyboardInterrupt:
            pass
        
        # Cleanup
        loop.run_until_complete(runner.cleanup())


# Standalone usage
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Box annotator service')
    parser.add_argument('-H', '--host', nargs='?', default='0.0.0.0', help='Host address bound')
    parser.add_argument('-P', '--port', nargs='?', type=int, default=80, help='Port used')
    parser.add_argument('-M', '--metadata', nargs='?', default='./metadata.json', help='Metadata file')
    parser.add_argument('-I', '--images', nargs='?', default='./images/', help='Image folder')
    parser.add_argument('-A', '--annotation', nargs='?', default='./annotation.json', help='Annotation file')
    args = parser.parse_args()
    run(args.host, args.port, args.metadata, args.images, args.annotation)
