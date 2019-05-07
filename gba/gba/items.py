# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
import re

def clear(value):
    
    if value is None:
        value = ""
    
    if isinstance( value, str ):
        value = value.strip()
        
    if isinstance( value, bytes ):
        value = value.strip()
                
    return value

def fix_price(value):
    
    if isinstance( value, str ):

        value = value.replace(u"£", "")
        value = value.replace(",", "")
    
    if value:
        value = "{:.2f}".format(float(value))
              
    return value


def remove_html_tags(value):
    
    if value is None:
        value = ""
    
    if isinstance( value, str ):
        value = re.sub( r'<[^>]+>', "", value )
        
    return value

class GbaItem(scrapy.Item):


    PdfLink = scrapy.Field( input_processor=MapCompose(clear), output_processor=TakeFirst() )
    PdfText = scrapy.Field( input_processor=MapCompose(clear), output_processor=TakeFirst() )
    DocumentUrl = scrapy.Field( input_processor=MapCompose(clear), output_processor=TakeFirst() )

    
#    PdfLink = scrapy.Field( input_processor=MapCompose(clear), output_processor=TakeFirst() )
#    PdfText = scrapy.Field(input_processor=MapCompose(clear), output_processor=TakeFirst()  )
#    DocumentUrl = scrapy.Field( input_processor=MapCompose(clear), output_processor=TakeFirst() )
