# Library Imports

import os, sys, io
import time
from pathlib import Path
CWD = Path.cwd().resolve()
import socket
import json
from datetime import date, datetime, timedelta
from tqdm import tqdm
import subprocess
import signal

from functools import partial, wraps
from typing import Callable, Optional, Dict, Union, Type, List, cast
from mode.utils.typing import Counter, Deque
from pydantic import field_validator, model_validator, BaseModel as BM, Field
from omegaconf import OmegaConf

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
from faust.types import TP
from http import HTTPStatus

# Logging imports

import logging
from logging.handlers import TimedRotatingFileHandler
from utils.logging import Logging, get_logger, get_logger_with_file
logger = get_logger()

# Local Imports
