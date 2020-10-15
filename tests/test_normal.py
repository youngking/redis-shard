#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from redis_shard.shard import RedisShardAPI
from redis_shard._compat import b
from redis import __version__ as REDIS_VERSION
from nose.tools import eq_
from .config import settings


class TestShard(unittest.TestCase):

    def setUp(self):
        self.client = RedisShardAPI(**settings)
        self.clear_db()

    def tearDown(self):
        pass

    def clear_db(self):
        self.client.delete('testset')
        self.client.delete('testzset')
        self.client.delete('testlist')
        self.client.delete('test1')
        self.client.delete('test2')
        self.client.delete('test3')
        self.client.delete('test7')
        self.client.delete('test8')

    def test_zset(self):
        if REDIS_VERSION.startswith('2.'):
            self.client.zadd('testzset', 'first', 1)
            self.client.zadd('testzset', 'second', 2)
        else:
            self.client.zadd('testzset', {'first': 1})
            self.client.zadd('testzset', {'second': 2})
        self.client.zrange('testzset', 0, -1) == ['first', 'second']

    def test_list(self):
        self.client.rpush('testlist', 0)
        self.client.rpush('testlist', 1)
        self.client.rpush('testlist', 2)
        self.client.rpush('testlist', 3)
        self.client.rpop('testlist')
        self.client.lpop('testlist')
        self.client.lrange('testlist', 0, -1) == ['1', '2']

    def test_mget(self):
        self.client.set('test1', 1)
        self.client.set('test2', 2)
        self.client.set('test3', 3)
        eq_(self.client.mget('test1', 'test2', 'test3'), [b('1'), b('2'), b('3')])

    def test_mset(self):
        self.client.mset({'test4': 4, 'test5': 5, 'test6': 6})
        eq_(self.client.get('test4'), b('4'))
        eq_(self.client.mget('test4', 'test5', 'test6'), [b('4'), b('5'), b('6')])

    def test_eval(self):
        self.client.eval("""
            return redis.call('set', KEYS[1], ARGV[1])
        """, 1, 'test7', '7')
        eq_(self.client.get('test7'), b('7'))

    def test_evalsha(self):
        sha = self.client.script_load("""
            return redis.call('set', KEYS[1], ARGV[1])
        """)
        eq_(self.client.evalsha(sha, 1, 'test8', b('8')), b('OK'))
        eq_(self.client.get('test8'), b('8'))

    def test_bytes_key(self):
        sha = self.client.script_load("""
            return redis.call('set', KEYS[1], ARGV[1])
        """)
        eq_(self.client.evalsha(sha, 1, b'test8', b('8')), b('OK'))
        eq_(self.client.get(b'test8'), b('8'))

