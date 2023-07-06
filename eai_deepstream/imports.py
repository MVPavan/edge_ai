import os, sys, io
import time
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
from utils.logging import Logging, start_logging
logger = start_logging()

from urllib.request import pathname2url
from urllib.parse import urljoin
from functools import partial, wraps
from typing import Callable, Optional, Dict, Union, Type, List
from pydantic import validator, BaseModel as BM, Field

class BaseModel(BM):
    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True

from dataclasses import dataclass, field
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig


import requests
from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
from fastapi import FastAPI, Depends, WebSocket, Query, Request
from fastapi import APIRouter, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse, JSONResponse, RedirectResponse
from fastapi.testclient import TestClient

# from celery import Celery
# from celery.schedules import crontab

import gi # noqa:F401,F402
gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GLib, Gst, GstRtspServer # noqa:F401,F402
import pyds # noqa:F401,F402