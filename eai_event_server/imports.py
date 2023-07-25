# Library Imports

import os, sys, io
import time
from pathlib import Path
import socket
import json
from datetime import date
from tqdm import tqdm
import subprocess
import signal

from functools import partial, wraps
from typing import Callable, Optional, Dict, Union, Type, List
from pydantic import validator, BaseModel as BM, Field

class BaseModel(BM):
    class Config:
        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True

from dataclasses import dataclass, field

from faker import Faker
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer

import asyncio
import faust
from faust import Worker, Record
from faust.serializers import codecs

# Logging imports

import logging
from logging.handlers import TimedRotatingFileHandler
from utils.logging import Logging, start_logging
logger = start_logging()

# Local Imports
