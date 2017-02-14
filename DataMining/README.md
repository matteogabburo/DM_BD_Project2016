## Data sets

1. miniset : 10 files with 100 rows for each file
2. mediumset : 10 files with 3000 rows for each file
3. bigset : 10 files with 10000 rows for each file
4. fullset : 10 files with 200000 rows for each file


## Tests

### Selected urls
1. perplexity

### Miniset
1. [4] S : 5, 10, 20, 40 
2. [4] RemoveJunk: (2,2),(2,4),(4,2),(4,4)
3. [4] Merge : 2*merge, 2*mergecluster 

### Mediumset
1. [6] Approximation Tree levels 3, 4, 5, 6, 7, 8

### Bigset



## conf.json parameters:

The name of the current test	
>`"test_name": "template",`
 MongoDB host name
>`"host": "localhost",`
 MongoDB port
>`"port": 27017,`

Directory that contain the datasets
>`"txt_directory": "/home/matteo/Desktop/DataMining/mediumset",`

DB name
>`"db_name":"db_geo_index",`
Collection where the url extracting from the files were put
>`"url_collection": "clicks_mediumset_dm1",`
Collection that contains the globals information about the dataset
>`"dbstat_collection":"globals_mediumset_dm1",`
Number of threads that read the files and persist them to the above collection
>`"geo_indexing_nthread":5,`

Selector of the removeJunk function
1. Static remover
2. Dinamic remover \[NOT TESTED\]
3. Don't use a removeJunk
>`"junk_function":1,`
Low threshold for the removeJunk
>`"junk_low_threshold":4,`
High threshold for the removeJunk
>`"junk_high_threshold":8,`

If True the program try to keep every possible information of any possible url in the dataset but with a loss of performance and without a possible improvement of the accuracy. If False, the program cut every not working url, best performances
>`"maximize_links":false,`
Name of the collection that contains the topics
>`"collection_topics":"topics_mediumset_dm1",`
Size of each cell of the grid
>`"s":10,`
Locs of the area where we want to run the program
>`"bounded_locs": [[35.515482, 6.958351],[46.897953, 18.457763]],`
Number of threads that work on the download and the lda of the urls
>`"topicsClustering_nthread": 250,`
Timeout for each http request
>`"max_waiting_time_http": 1,`
If true, verbose mode
>`"log": "True",`

Number of topics extracted by lda
>`"lda_ntopics":20,`
Number of passes of lda
>`"lda_npasses":2,`
Number of words for each topic
>`"lda_nwordsfortopic":20,`

Name of the collection that contains the approximated topics
>`"collection_approximation" : "topics_approximated_mediumset_dm1",`
Merge function selector
1. Merge_cluster using K-means
2. Merge (best time performance)
>`"merge_algorithm" : 2,`
Number of levels of the approximation tree
>`"n_approximation_levels": 4,`
Number of children for any level of the approximation tree
>`"n_approximation_partition": 4`
