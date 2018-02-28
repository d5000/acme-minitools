# ACME Mini-Tools

The ACME Mini-Tools are a collection of Python scripts to be able to create and provide a (public or private) dataset of a RDF version of a cryptocurrency blockchain, using the CCY and DOACC ontologies. The scripts are written for Slimcoin, but can be used / adapted for all Bitcoin-based coins.

The scripts are based on the scripts provided by ACME to create and actualize its dataset. In contrast to the full ACME the Mini-Tools are not meant as a full-fledged block explorer. They don't provide a graphical user interface, the goal is to provide Web services that provide certain blockchain data like publications and the available coin supply.

The ACME Mini-Tools work with the SPARQL server Apache Jena Fuseki 2. Other dependencies include the Python libraries RDFLib and Requests.

## How it works

The ACME Mini-Tools "translate" the output of the JSON RPC from Slimcoin to the CCY and DOACC OWL ontologies, block by block. Then the data is provided to the running Fuseki server, where it can be stored in a TDB database.

There are two main "methods" to run the Mini-Tools:

* as a blocknotify script. Each time the Slimcoin client detects a new block, the script is invoked.
* manually by the user via the command line. This is useful when a major "catchup" is needed. The script provides some options to control the block processing.

The script can check for blockchain reorganizations: If a block stored at the dataset is detected that was discarded as an orphan (stale block) by the client, it "rolls back" the RDF blockchain deleting the last block entries, until the last common block is found.

A KeyboardInterrupt will end the script and transfer the already processed data to Fuseki.

## Configuration

The file **coin.ini** contains the basic configuration. Rename **coin.ini.sample** to **coin.ini** and complete missing information (mandatory: Fuseki directory and directory for storage of data files). 

## Special modes

The script can create partial blockchain datasets. This is meant to provide a better performance / lesser load for some applications. There are two modes, adopted to the Slimcoin blockchain:

* **Publication mode:** The script only saves blocks that contain OP_RETURN transactions. This is useful for Web2Web gateways and other apps that track publications.
* **Burn address following mode:** (specific for Slimcoin's Proof-of-Burn concept) The script only saves blocks that contain burn transactions. This is useful to follow not only the amount of burnt coins, but also to control the available supply of the currency, because burnt coins are taken out of circulation forever.

To simplify catchups, a JSON "blockheight file" is created after each time the script runs in these special modes; it stores the last checked block height and blockhash, even if it's not stored in the RDF dataset.

The current way these special modes work should be seen as **unstable**. Later versions probably will only save transactions that satisfy the mentioned requirements and will discard other transactions and most of the block header. Also, the new "burnt" parameter could be processed, that should be much more efficient than to track the burn address. A third possible improvement is a new special ontology for publication indices and/or coin supply tools; it could store the inscriptions directly, discarding the rest of the transaction data; also this ontology could provide a way to discard the JSON blockheight file.

## Scripts

* blocknotifybase.py: Provides the basic classes and methods for the tools to work.
* block2rdf-cli.py: Provides a simple command line interface. This script can be invoked as a simpĺe blocknotify script (via the -b option) or used manually as a catchup script.

## Missing features (can be added later)

* The script does not check the whole RDF blockchain for consistency, only a reorg-check for the last processed block is provided.
* There is no automatic mode which decides if the "blocknotify" or the "catchup" mode is used. If a catchup is required, it must be invoked manually by the user. In the case of an outage, or even a large reorganization, this *can* lead to incomplete blockchain datasets, if the Slimcoin client continues to invoke the blocknotify script while the RDF blockchain is not updated to the last block. However, a manual catchup should be always able to repair the dataset.
* There is no "catchup and delete old RDF chain" mode. Every time the script is invoked - with the exception of reorg checks - the block data is added to the RDF dataset, without deleting the existing data.
* Address entries in the RDF blockchain are not completely deleted when a reorganized blockchain is "rolled back"; only the associated transactions are deleted. This should only be an issue if there are double spends, in this case, unused address entries could be created.
