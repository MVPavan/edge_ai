import os, sys
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
from utils.logging import Logging, start_logging
logger = start_logging()

from pydantic import BaseModel as BM

class BaseModel(BM):
    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True

from pydantic.dataclasses import dataclass
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

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GLib, Gst, GstRtspServer
import pyds