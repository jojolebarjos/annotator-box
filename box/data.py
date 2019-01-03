# -*- coding: utf-8 -*-


import asyncio
import base64
import io
import json
import os
import random


# Sample container
class Data:
    def __init__(self, metadata_path, image_folder, annotation_path, executor):
        self.metadata_path = metadata_path
        self.image_folder = image_folder
        self.annotation_path = annotation_path
        self.executor = executor
        self.lock = asyncio.Lock()
    
    # Acquire metadata
    def get_metadata(self):
        # TODO maybe cache this
        metadata = {}
        if os.path.exists(self.metadata_path):
            with io.open(self.metadata_path, 'r', encoding='utf-8') as file:
                metadata = json.load(file)
        return metadata
    
    # Acquire available images
    def get_available_images(self):
        # TODO allow recursive discovery
        # TODO more lenient name filter
        return [name for name in os.listdir(self.image_folder) if name.lower().endswith('.jpg')]
    
    # Acquire annotations
    def get_annotations(self):
        # TODO maybe cache this (and check file modification date)
        annotations = {}
        if os.path.exists(self.annotation_path):
            with io.open(self.annotation_path, 'r', encoding='utf-8') as file:
                for line in file:
                    annotation = json.loads(line)
                    annotations[annotation['name']] = annotation
        return annotations
    
    # Run safely in background
    async def do(self, f):
        async with self.lock:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, f)
    
    # Choose next image to be sent to annotator
    async def get_next_sample(self):
        def run():
            
            # Get metadata
            metadata = self.get_metadata()
        
            # Select random image
            # TODO better policy, possibly based on current model
            candidates = self.get_available_images()
            if len(candidates) == 0:
                return None
            index = random.randint(0, len(candidates) - 1)
            name = candidates[index]
            
            # Load image bytes
            path = os.path.join(self.image_folder, name)
            with io.open(path, 'rb') as file:
                data = file.read()
            content = base64.b64encode(data).decode('ascii')
            mime_type = 'image/jpeg'
            data = f'data:{mime_type};base64,{content}'
            
            # Load current annotations
            annotations = self.get_annotations()
            annotation = annotations.get(name)
            if annotation is None:
                annotation = {
                    'name': name,
                    'boxes': []
                }
            
            # Build payload
            payload = {
                **annotation,
                'image': data,
                'metadata': metadata
            }
            return payload
        
        # Run safely in background
        return await self.do(run)
    
    # Store sample
    async def add_annotation(self, annotation):
        def run():
            copy = dict(annotation)
            if 'image' in copy:
                del copy['image']
            if 'metadata' in copy:
                del copy['metadata']
            # TODO add timestamp
            # TODO maybe validate content
            line = json.dumps(copy)
            with io.open(self.annotation_path, 'a', encoding='utf-8', newline='\n') as file:
                file.write(f'{line}\n')
            return {'ok': True}
            
        # Run safely in background
        return await self.do(run)
