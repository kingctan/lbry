from collections import Counter

from twisted.internet import defer

from lbrynet.core.Peer import Peer
from lbrynet.dht.peerfinder import DummyPeerFinder


class DummyPeerManager(object):
    def get_peer(self, host, port):
        return Peer(host, port)


class DummyNode(object):
    """ Used when DHT is disabled. Doesn't do anything, just bypass calls. """
    def __init__(self, *args, **kwargs):
        self.peer_manager = DummyPeerManager()
        self.peer_finder = DummyPeerFinder()

    def announceHaveBlob(self, key):
        return defer.succeed([])

    def joinNetwork(self, *args, **kwargs):
        return defer.succeed(None)

    def stop(self, *args, **kwargs):
        return defer.succeed(None)

    def getPeersForBlob(self, *args, **kwargs):
        return defer.succeed([])

    def get_most_popular_hashes(self, num_to_return):
        return defer.succeed(Counter([]))

    def addContact(self, contact):
        pass

    def removeContact(self, contactID):
        pass

    def findContact(self, contactID):
        pass

class DummyAnnouncer(object):
    def start(self):
        return defer.succeed(None)

    def stop(self):
        return defer.succeed(None)

    def hash_queue_size(self):
        return 0
