#! /usr/bin/env python3
"""block2rdf-cli is the third version of the adapted blocknotify script.

TODO:
- Revisar modo "test".
- "Exit gracefully" cuando el cliente Slimcoin no esté corriendo - sino el script sigue corriendo y hay que "matarlo". 
"""

from rdflib import RDF, URIRef, Graph
from blocknotifybase import BlockChainProcessor, RDFChainProcessor, mainnet, testnet, datadir
import sys
import subprocess
import os
import json
import argparse
import time

global blockhash

class ChainCatchup(BlockChainProcessor, RDFChainProcessor):
    """Inherits the two main classes from blocknotifybase."""

    def __init__(self, network, dataset, store_offset, check_reorgs):

        self.dataset = dataset
        self.store_offset, self.check_reorgs = store_offset, check_reorgs # flags
        BlockChainProcessor.__init__(self, network)

    def store_blockheightfile(self, hdic):
        """Writes a JSON file that contains the last blockheight checked for OP_RETURN or burn transactions.
        The file contains also the height of the last block stored in the RDF dataset."""

        with open(datadir + '/{s}.height.txt'.format(s=self.dataset), 'w') as fp:
            json.dump(hdic, fp)

    def load_blockheightfile(self):
        try:
            with open(datadir + '/{s}.height.txt'.format(s=self.dataset), 'r') as fp:
                return json.load(fp)
        except FileNotFoundError:
            if verbose: print("No blockheight file found. Using current RDF chain block height.")
            return None

    def next_blockheight(self):
        """Returns the height of the block after the last checked/stored block, regardless of mode."""
        if self.store_offset == True:
            bhf_hdict = self.load_blockheightfile()
            try:
                return bhf_hdict["checked_height"] + 1
            except KeyError:
                if verbose: print("Blockheight file not found or corrupted. Starting from chain graph height.")
      
        cg_hdict = self.get_chaingraph_height(self.dataset)
        if cg_hdict is None:
            return 0 # new chain
        else:
            return cg_hdict.get("rdf_height") + 1

    def exit(self, lastheight):
        if verbose or self.store_offset:
            cg_hdict = self.get_chaingraph_height(self.dataset)
        if self.store_offset == True:
            cbhash = self.getblockhash(lastheight)
            cg_hdict.update({"checked_height":lastheight, "checked_blockhash":cbhash})
            self.store_blockheightfile(cg_hdict)
            if verbose: print("Last checked block:", cbhash, "at height", lastheight)        
        if verbose: print("Final stored block:", cg_hdict.get("rdf_blockhash"), "at height", cg_hdict.get("rdf_height"))
        if verbose: print("OK")
        if log: 
            self.log_block(lastheight, self.getblockhash(lastheight), "EXITING")
        sys.exit()

    def log_block(self, blockheight, blockhash, message=""):
            with open(datadir + '/{s}.log'.format(s=self.dataset), 'a') as fp:
                fp.write("{} {} {}\n".format(blockheight, blockhash, message))

    def catchup_main(self, startblock, maxblocks, maxheight, mode="mainnet"):

        if verbose:
            interval = 1
        else:
            interval = 100

        self.setUpGraph() # every loop instance needs a new graph
        # client_prevhash = None
        endblock = min(startblock + maxblocks, maxheight)
        interrupt = False
        
        if self.check_reorgs:
            # checks if RDF graph and client are on the same chain.
            # If not, last block is deleted, and the previous block is checked.
            # The loop then continues with the last common blockheight.
            blockheight = self.reorgcheck(startblock)
        else:
            blockheight = startblock

        while blockheight < endblock:
            try:
                blockhash = self.getblockhash(blockheight)

                if blockheight % interval == 0:
                    print(blockheight)                                 
                self.readblock(blockhash, mode) # calls main routine of b2rbase
                if log:
                    self.log_block(blockheight, blockhash)
                prev_blockhash = blockhash
                blockheight += 1
            except KeyboardInterrupt:
                if verbose: print("KeyboardInterrupt: Stopping.")
                interrupt = True
                break
            except Exception as e:
                if verbose: print("Exception:", e, ". Exiting")
                interrupt = True
                break 
        return blockheight, interrupt


    def reorgcheck(self, height):
        """Checks if RDF graph and client are on the same chain.
        If not, last block is deleted from the RDF graph, and the previous block is checked.
        After processing the first correct block the script catches up to the original "maxheight" value."""
        reorg = False
        if height == 0: # new chain start
            return 0
        if self.store_offset:
            # compares the content of blockheight file with the block hash of the same height.
            # As we have no information of what occurred between last stored block and the last checked block,
            # if there is a reorg between both, the program must continue at the stored height 
            # If the reorg is deeper than the stored height, the program must check
            # all stored blocks until the hashes are consistent
            # so it returns to the standard reorgcheck loop.
            bhf = self.load_blockheightfile()
            if bhf.get("checked_blockhash") == self.getblockhash(bhf.get("checked_height")):
                # checked block is ok: blockheight stays the same
                return height
            elif bhf.get("rdf_blockhash") == self.getblockhash(bhf.get("rdf_height")):
                # last stored block is ok: stored block set as blockheight, blockheightfile updated
                if log:
                    self.log_block(bhf.get("checked_height"), bhf.get("checked_blockhash"), "Reorg detected. Rolling back to last stored block.")
                bhf.update({"checked_height":bhf.get("rdf_height"), "checked_blockhash":bhf.get("rdf_blockhash")})
                self.store_blockheightfile(bhf)

                return bhf.get("rdf_height") + 1

        while True:
            rdf_lastblock = self.get_chaingraph_height(self.dataset)
            chaingraph_height = rdf_lastblock.get("rdf_height")
            chaingraph_bhash = rdf_lastblock.get("rdf_blockhash")
            bestchain_bhash = self.getblockhash(rdf_lastblock.get("rdf_height")) # current best chain as viewed by the client

            if bestchain_bhash != chaingraph_bhash: # reorg
                reorg = True
                if verbose: print("RDF blockchain is on a fork:", chaingraph_bhash, "correct block:", bestchain_bhash)
                if log:
                    if self.store_offset:
                        message = "Reorg detected. Rolling back to next stored block."
                    else:
                        message = "Reorg detected. Rolling back one block."
                    self.log_block(chaingraph_height, chaingraph_bhash, message)
                lastblockgraph = self.get_chaingraph_block(chaingraph_bhash, self.dataset)
                if verbose: print("Blockgraph to be DISCARDED:", lastblockgraph.serialize(format="n3").decode("utf-8"))
                status = self.delete_chaingraph_block(chaingraph_bhash, self.dataset)
                if verbose: print("Graph update operation delivered status:", status)
                bestchain_bhash = None
                time.sleep(10) # minimize database load in long reorgs
                continue
            else:
                if reorg == True:
                    return chaingraph_height + 1
                else:
                    return height



    def catchup_loop(self, offset, loops, maxblocks, maxheight, sleep, mode="mainnet"):
        startblock = offset
        for i in range(loops):

            if verbose: print("Starting loop at height", startblock)
            print(startblock, maxblocks, maxheight, mode)
            blockheight, interrupt = self.catchup_main(startblock, maxblocks, maxheight, mode)

            if len(self.g) == 0:
                if verbose: print("No data to be added. Continuing.")
            else:
                if verbose: print("Transferring data ...")
                self.change_chaingraph(self.dataset)
                if verbose: print("Sleeping for {} seconds.".format(str(sleep)))
                time.sleep(sleep)
            if interrupt == True: # KeyboardInterrupt
                break

            startblock = startblock + maxblocks
            if startblock > maxheight:
                break
                  

        self.exit(blockheight - 1) # last checked block is one less than current height


def main():
    global test
    global debug
    global verbose
    global log


    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--loops", type=int, default=1, help="Loop (catchup) mode; loop the main cycle X times (Default: 1).")
    group.add_argument("-b", "--blockhash", type=str, help="Blockhash mode; adds only the block with the given blockhash. To be triggered by blocknotify.")
    parser.add_argument("-m", "--maxblocks", type=int, default=100, help="Number of blocks in each cycle (default: 100).")
    parser.add_argument("-s", "--sleep", type=int, default=2, help="Time (in seconds) to sleep between each cycle (default: 2).")
    parser.add_argument("-o", "--offset", type=int, help="Block-height offset.")
    parser.add_argument("-O", "--storeoffset", action="store_true", help="Stored offset mode: retrieves offset value from file.")
    parser.add_argument("-t", "--test", action="store_true", help="Test mode. Does not transfer data to Fuseki, but prints one cycle to stdout.") # implement for delete
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode.")
    parser.add_argument("-L", "--log", action="store_true", help="Log block output.")
    parser.add_argument("-r", "--reorgcheck", action="store_true", help="Checks for reorgs (more expensive).")
    parser.add_argument("-R", "--repair", type=int, help="Repair mode. Begins X blocks before the current RDF blockchain height, to prevent incomplete blocks (e.g. if the script was interrupted).")
    parser.add_argument("-S", "--safe", type=int, const=100, nargs="?", help="Safe mode. Catches up to X blocks before the current real blockchain height (X defaults to 100, can be increased if there is reorg danger).", dest="blocklimit")
    parser.add_argument("-P", "--only-publications", help="Publication mode. Only records blocks that contain OP_RETURN transactions.", action="store_const", dest="mode", const="pub")
    parser.add_argument("-B", "--only-burn-address", help="Burn address mode. Only records blocks which affect the balance of the burn address.", action="store_const", dest="mode", const="burn")
    parser.add_argument("-T", "--testnet", help="Testnet mode.", action="store_const", dest="mode", const="testnet")
    

    args = parser.parse_args()
    test, debug, verbose, log = args.test, args.debug, args.verbose, args.log
    blockhash = args.blockhash

    if args.mode is None:
       args.mode = "mainnet"
       dataset = mainnet.get('symbol').lower()
       network = mainnet
    elif args.mode == "testnet":
       dataset = testnet.get('symbol').lower()
       network = testnet
    else:
       dataset = args.mode + "_" + mainnet.get('symbol').lower()
       network = mainnet

    if args.mode in ("pub","burn"):
        args.storeoffset = True

    if blockhash is not None:
        # Blocknotify mode.
        c = ChainCatchup(network, dataset, args.storeoffset, True)
        if verbose: print("Notify mode. Adding block:", blockhash)
        maxheight = c.getblockdata(blockhash).get("height", 0)
        next_blockheight = c.next_blockheight()
        # check if there are blocks missing since last run, if yes, catch up.
        if maxheight > next_blockheight:
            args.offset = next_blockheight
            args.maxblocks = maxheight - args.offset
            if args.maxblocks > 100: # large catchups: loop mode
                args.loops = int(args.maxblocks / 100) + 1
                args.maxblocks = 100
        else:
            args.offset = maxheight

    else:
        c = ChainCatchup(network, dataset, args.storeoffset, args.reorgcheck)
        next_blockheight = c.next_blockheight()
        if args.offset is None:
            if args.repair is not None:
                args.offset = next_blockheight - args.repair
            else:
                args.offset = next_blockheight


        if args.blocklimit is not None:
            maxheight = c.binfo.get('blocks') - args.blocklimit
        else:
            maxheight = c.binfo.get('blocks') + 1
     
        if maxheight < args.offset:
            raise ValueError("Endblock has lower height than starting block.")

        if verbose: print("End height block: {}".format(maxheight))
        if verbose: print("Offset: {} Maxblocks: {}".format(args.offset, args.maxblocks))

    if args.offset == 0:
         c.start_new_chain()

    print(maxheight, next_blockheight, args.offset, args.maxblocks, args.loops)
    print(args.offset, args.loops, args.maxblocks, maxheight, args.sleep, args.mode)

    c.catchup_loop(args.offset, args.loops, args.maxblocks, maxheight, args.sleep, args.mode)

if __name__ == "__main__":
    main()

