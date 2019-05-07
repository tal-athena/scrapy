# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy import signals
from gba.exporters import MyCsvItemExporter, MyHeadlessCsvItemExporter
from sqlalchemy.orm import sessionmaker
from gba.models import GbaData, db_connect, create_tables
import re
import os.path
import io
from gba.items import GbaItem
from scrapy.pipelines.images import ImagesPipeline

class GbaDatabasePipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_tables(engine)

        self.Session = sessionmaker(bind=engine)
        session = self.Session()
        
    def close_spider(self, spider):
        
        session = self.Session()
        session.commit()
        session.close()

    def process_item(self, item, spider):
        """

        This method is called for every item pipeline component.

        """
        session = self.Session()
        record = GbaData(**item)

        try:            
            session.add(record)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()
            raise
        finally:
            session.close()
    
        return record

        


class GbaImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if 'images' in item:
            for image in item['images']:

                request = scrapy.Request( url=image["url"], dont_filter=True )
                request.meta['img_name'] = image["name"]
                yield request
    
    def file_path(self, request, response=None, info=None):
        return request.meta['img_name']

class GbaPipeline(object):
    
    def __init__(self):
        self.exporters = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        
        for item_type in [
                "GbaItem",
            ]:
            
            file_name = item_type.replace( "Item", "" )
            
            file = open(
                'output/' + "{0}.csv".format(file_name), 'w',
                # encoding='utf-8'
            )
            
            exporter = MyCsvItemExporter(file, delimiter=",")
            
            # if add_header:
            #     exporter = MyCsvItemExporter(file, delimiter=",")
            # else:
            #     exporter = MyHeadlessCsvItemExporter(file, delimiter=",")
            
            if item_type == "GbaItem":
                EXPORT_FIELDS = [
        
                    'ItemID',
                    'Title',
                    'Description',
                    'Price',
                    'Category',
                    'URL',
                    'ImageURLs',
                ]
                        
            exporter.fields_to_export = EXPORT_FIELDS
            exporter.start_exporting()

            self.exporters[item_type] = exporter
            
    def spider_closed(self, spider):
        for exporter in self.exporters.values(): 
            exporter.finish_exporting()

    def process_item(self, item, spider):

        if isinstance(item, GbaItem):
            exporter = "GbaItem"
            
        self.exporters[exporter].export_item(item)
        return item
