# -*- coding: utf-8 -*-

import scrapy
from gba.items import GbaItem
from scrapy.loader import ItemLoader
import re
import csv
import os
from subprocess import call
import codecs
from sqlalchemy import text 

from sqlalchemy.orm import sessionmaker
from gba.models import db_connect



class GbaSpider(scrapy.Spider):

    name = 'gba'
    
    def __init__(self, mode = "update", **kwargs):
        
        if mode != "update":
            try:
                os.remove("gba.db")
            except:
                pass
        
        self.mode = mode         

        super().__init__(**kwargs)  # python3


    start_urls = ['https://www.g-ba.de/informationen/beschluesse/']

    item_id = 1
    debug = False;
    

    def parse(self, response):
        
        for document_url in response.xpath('//table/tbody/tr/td[1]/a/@href').extract():
            
            yield scrapy.Request(
                url=response.urljoin(document_url),
                # dont_filter=True,
                callback=self.parse_document
            )
            
                        
            # Debug
            if self.debug:
                break
        
        #if self.flag > 2 or response.xpath('//li[@class="gba-pagination__nav-item"]/a[@class="gba-pagination__nav-text gba-pagination__nav-arrow"]/@href[contains(.,"ab")]').__len__() == 4:            
    
        next_page_url = response.xpath('//li[@class="gba-pagination__nav-item"]/a[@class="gba-pagination__nav-text gba-pagination__nav-arrow"]/@href[contains(.,"ab")]')[1].extract()

        next = next_page_url.replace("beschluesse/ab/", "")
        next = next.replace("/", "")
        cur = response.url.replace("https://www.g-ba.de/beschluesse/", "")
        cur = cur.replace("ab", "")
        cur = cur.replace("/", "")
        
        if cur == "": 
            cur = "0"

        next = int(next)
        cur = int(cur)

        if next > cur:        
            yield scrapy.Request(
                url=response.urljoin(next_page_url),
                callback=self.parse
            )
                                        
    def parse_document(self, response):
        
        document_id = re.search(r'/(\d+)/$', response.url).group(1)
        
        pdf_index = 1
        
        for pdf_document_url in response.xpath('//ul/li/div/a[@class="download-helper"]/@href[contains(translate(.,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz"),"pdf")]').extract():
            
            if self.mode == "update":
                if self.isExist(pdf_document_url) == True:
                    continue;
            yield scrapy.Request(
                url=response.urljoin(pdf_document_url),
                meta={
                    'document_url': response.url,
                    'document_id': document_id,
                    'pdf_index': pdf_index,
                },
                dont_filter=True,
                callback=self.process_pdf
            )
            
            pdf_index += 1
            
            # Debug
            if self.debug:
                break

    def process_pdf(self, response):
        
        pdf_filename = "output/{document_id}_{pdf_index}.pdf".format(document_id=response.meta["document_id"], pdf_index=response.meta["pdf_index"])
        txt_filename = "output/{document_id}_{pdf_index}.txt".format(document_id=response.meta["document_id"], pdf_index=response.meta["pdf_index"])
        
        with open(pdf_filename, "wb") as f:
            f.write(response.body)

        if os.path.isfile(pdf_filename):
            call(["pdftotext.exe", "-layout", pdf_filename, txt_filename ] )
        
        pdf_data = None
        if os.path.isfile( txt_filename ):
            with codecs.open(txt_filename, encoding='latin-1') as reader:
                pdf_data = reader.read()
        
        try:
            os.remove(pdf_filename)
        except:
            pass
        try:
            os.remove(txt_filename)
        except:
            pass
        
        if pdf_data:
        
            l = ItemLoader(item=GbaItem())
            l.add_value('PdfLink', response.url)            
            l.add_value('PdfText', pdf_data)
            l.add_value('DocumentUrl', response.meta["document_url"])
            
#            l.load_item()
            
            yield l.load_item()
    

    def isExist(self, url):
        engine = db_connect()            

        session = sessionmaker(bind=engine)()
        
        result = session.execute(text("SELECT * FROM Records WHERE PdfLink=:param"), {"param":"https://www.g-ba.de" + url} )
        for row in result:
            session.close()
            return True
        session.close()
        return False
