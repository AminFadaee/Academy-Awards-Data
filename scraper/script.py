import json
import logging
import os.path
import re
from enum import Enum

import scrapy
from scrapyscript import Job, Processor


class DataMode(Enum):
    complete = 0
    short = 1
    winners_only = 2

    def __str__(self):
        return self.name


def get_crawler(data_mode: DataMode, dump_on: str = None):
    class IMDbAwardsSpider(scrapy.Spider):
        name = 'Academy Awards Spider'
        mode = data_mode
        dump_path = dump_on
        start_urls = [
            f'https://www.imdb.com/event/ev0000003/{year}/1/'
            for year in range(1929, 2023)
        ]

        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)
            logging.getLogger('scrapy').propagate = False

        def collect(self):
            job = Job(self.__class__)
            processor = Processor()
            data = processor.run([job])
            return data

        def parse(self, response, **kwargs):
            scripts = response.xpath('//script').getall()
            data = dict()
            for script in scripts:
                for line in script.split('\n'):
                    if 'IMDbReactWidgets.NomineesWidget.push' in line:
                        jsons = re.findall(r'{.*}', line)
                        if jsons:
                            data = json.loads(jsons[0])
            data = self.prepare_data(data)
            if self.dump_path:
                file_name = response.url.split('/')[-3] + '.json'
                folder = os.path.join(self.dump_path, str(self.mode))
                if not os.path.isdir(folder):
                    os.makedirs(folder)
                file = open(os.path.join(folder, file_name), 'w')
                file.write(json.dumps(data, indent=3))
                file.close()
            return data

        def prepare_winners_only_data(self, data):
            return [
                {
                    'category': award['categoryName'],
                    'winners': [
                        [primary['name'] for primary in nomination['primaryNominees']]
                        for nomination in award['nominations']
                        if nomination['isWinner']
                    ][0]  # 1 Winner only
                }
                for award in data
            ]

        def prepare_short_data(self, data):
            return [
                {
                    'category': award['categoryName'],
                    'nominations': [
                        {
                            'won': nomination['isWinner'],
                            'nominees': [primary['name'] for primary in nomination['primaryNominees']]
                        }
                        for nomination in award['nominations']
                    ]
                }
                for award in data
            ]

        def prepare_complete_data(self, data):
            return [
                {
                    'category': award['categoryName'],
                    'nominations': [
                        {
                            'notes': nomination['notes'],
                            'won': nomination['isWinner'],
                            'primary': [primary['name'] for primary in nomination['primaryNominees']],
                            'secondary': [secondary['name'] for secondary in nomination['secondaryNominees']]
                        }
                        for nomination in award['nominations']
                    ]
                }
                for award in data
            ]

        def prepare_data(self, data):
            if not data:
                return data
            data = data['nomineesWidgetModel']['eventEditionSummary']['awards'][0]['categories']
            if self.mode == DataMode.winners_only:
                return self.prepare_winners_only_data(data)
            if self.mode == DataMode.short:
                return self.prepare_short_data(data)
            return self.prepare_complete_data(data)

    return IMDbAwardsSpider()


spider = get_crawler(DataMode.complete, dump_on='out')
spider.collect()
