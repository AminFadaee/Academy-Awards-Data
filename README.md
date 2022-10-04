# Academy Awards Datasets

This is the dataset for Academy Awards winners and nominees.
I truly and honestly do not have the faintest idea why I gathered this data.
I imagine it was for good reasons.
Anyway, whatever the reasons may be, a simple google search (at the time of writing this) shows that there are no
concrete datasets like this, so, you're most welcome!

![](assets/image.png)

## Schemas

There are 3 different schema for the data which you can choose from:

* Complete Schema
* Short Schema
* Winners Only Schema

The data for each of these schemas can be found in the `data` folder.
Each dataset is denoted by the award's year (the year it was held).

### Winners Only Schema

This is the simplest schema containing only the name of the award, and it's winner.

### Short Schema
This schema has all the nominees in it (not just the winners).

### Complete Schema
This one contains all nominees. Also, nominees can be primary or secondary. For example,
for the best actor awards, the actor is the primary nominee and the movie is secondary.

## Script
There is a **REALLY GOOD CHANCE** that I don't care enough about this project to update it in the future.
So, I leave you with the script I wrote to produce it. 
It uses Python+Scrapy to scrape IMDb.
Run it to reproduce the data. You're welcome again!

## License

I don't know! Do whatever the hell you want with the data! I am scraped it from somewhere else anyway!
