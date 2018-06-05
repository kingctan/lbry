from random import choice
import logging

from twisted.internet import defer
import treq

from lbrynet import conf


log = logging.getLogger(__name__)


class BlobMirror(object):
    def __init__(self, blob_manager, servers=None, client=None):
        self.servers = list(servers or conf.settings['blob_server_domains'])
        self.client = client or treq
        self.blob_manager = blob_manager

    @defer.inlineCallbacks
    def get_all_missing_blobs(self):
        blobs = self.blob_manager.blobs.itervalues()
        needed = [blob for blob in blobs if not blob.get_is_verified()]
        for success, (blob, we_have_it) in (yield defer.DeferredList(map(self.has_blob, needed))):
            if we_have_it:
                self._get_blob(blob)

    @defer.inlineCallbacks
    def has_blob(self, blob):
        print(url_for(choice(self.servers), blob.blob_hash))
        has_it = (yield self.client.head(url_for(choice(self.servers), blob.blob_hash))).code == 200
        defer.returnValue((blob, has_it))

    def get_blob(self, blob_hash):
        if blob_hash in self.blob_manager.blobs:
            return self._get_blob(self.blob_manager.blobs[blob_hash])

    @defer.inlineCallbacks
    def _get_blob(self, blob):
        response = yield self.client.get(url_for(choice(self.servers), blob.blob_hash))
        if response.code == 200 and not blob.is_downloading() and 'mirror' not in blob.writers:
            blob.set_length(response.length)
            writer, finished_deferred = blob.open_for_writing('mirror')
            finished_deferred.addCallback(self._on_completed_blob)
            finished_deferred.addErrback(self._on_failed)
            d = treq.collect(response, writer.write)
            d.addErrback(self._on_failed)
            d.addBoth(lambda _: writer.close())

    def _on_completed_blob(self, blob):
        log.debug('Mirror completed download for %s', blob.blob_hash)

    def _on_failed(self, err):
        log.debug('Mirror failed downloading')


def url_for(server, blob_hash=''):
    return 'http://{}/{}'.format(server, blob_hash)
