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
            print(response.url.split('/'))
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
                file_name = response.url.split('/')[-3]+'.json'
                folder = os.path.join(self.dump_path, str(self.mode))
                if not os.path.isdir(folder):
                    os.makedirs(folder)
                file = open(os.path.join(folder, file_name), 'w')
                file.write(json.dumps(data, indent=3))
                file.close()
            return data

        def prepare_data(self, data):
            if not data:
                return data
            data = data['nomineesWidgetModel']['eventEditionSummary']['awards'][0]['categories']
            prepared_data = []
            for award in data:
                prepared_award = dict()
                prepared_award['category'] = award['categoryName']
                prepared_award['nominations'] = []
                for nomination in award['nominations']:
                    prepared_nomination = {
                        'notes': nomination['notes'],
                        'won': nomination['isWinner']
                    }
                    if data_mode == DataMode.winners_only and not prepared_nomination['won']:
                        continue
                    primary_nominations = [
                        {
                            'name': primary['name'],
                            'notes': primary['note'],
                            'imdb_id': primary['const']
                        }
                        for primary in nomination['primaryNominees']
                    ]
                    if data_mode == DataMode.winners_only:
                        prepared_nomination = [
                            primary_nomination['name']
                            for primary_nomination in primary_nominations
                        ]
                        while isinstance(prepared_nomination, list) and len(prepared_nomination) == 1:
                            prepared_nomination = prepared_nomination[0]
                    elif self.mode == DataMode.short:
                        prepared_nomination['nominees'] = [
                            primary_nomination['name']
                            for primary_nomination in primary_nominations
                        ]
                        prepared_nomination.pop('notes')
                    else:
                        prepared_nomination['primary'] = primary_nominations
                        prepared_nomination['secondary'] = [
                            {
                                'name': secondary['name'],
                                'notes': secondary['note'],
                                'imdb_id': secondary['const']
                            }
                            for secondary in nomination['secondaryNominees']
                        ]
                    prepared_award['nominations'].append(prepared_nomination)
                prepared_data.append(prepared_award)
            return prepared_data

    return IMDbAwardsSpider()


spider = get_crawler(DataMode.winners_only, dump_on='out')
spider.collect()
