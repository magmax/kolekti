#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import platform
import logging
from colorlog import ColoredFormatter
LOG = logging.getLogger(__name__)

import Ice
import IceStorm
THISDIR = os.path.dirname(__file__)
Ice.loadSlice(os.path.join(THISDIR, '..', '..', 'slice', 'kolekti.ice'))
import Kolekti


def configure_log():
    logging.basicConfig(
        level=logging.INFO,
    )
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%',
    )

    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)


class MetricProducerI(Kolekti.MetricProducer):
    def list_metrics(self, current=None):
        LOG.info("Event received: {0}".format(message))
        return ['foo', 'bar']

    def get_metric(self, name, args, current=None):
        return 'this.is.an.example 12345 %s' % int(time.time())


class Server(Ice.Application):
    def get_topic_manager(self):
        LOG.info('Connecting to Topic Manager')
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            LOG.warning("Property %s not set", key)
            return None

        LOG.info("Using IceStorm in: '%s'", proxy)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        LOG.info('Starting server...')
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            LOG.error(': invalid proxy')
            return 2

        LOG.info('Connecting to broker...')
        ic = self.communicator()
        servant = MetricProducerI()
        adapter = ic.createObjectAdapter("MetricProducerAdapter")
        subscriber = adapter.addWithUUID(servant)

        LOG.info('Registering Topics')
        topics = []
        for topic_name in ('all', platform.system().lower(), platform.node().lower()):
            LOG.info('Registering to Topic %s', topic_name)
            qos = {}
            try:
                topic = topic_mgr.retrieve(topic_name)
            except IceStorm.NoSuchTopic:
                topic = topic_mgr.create(topic_name)

            topics.append(topic)
            topic.subscribeAndGetPublisher(qos, subscriber)

        LOG.info('Server running.')
        LOG.info('Waiting events on %s', subscriber)

        adapter.activate()
        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        LOG.info('Stopping server...')
        LOG.info('Unregistering topics...')
        for topic in topics:
            LOG.info('Unregistering from %s', topic)
            topic.unsubscribe(subscriber)
        LOG.info('Server stopped.')

        return 0


configure_log()
sys.exit(Server().main(sys.argv))
