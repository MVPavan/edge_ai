import os, sys
from dataclasses import dataclass
from pathlib import Path
import json
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
from utils.logging import Logging, start_logging

logger = start_logging()

from enum import Enum
from datetime import datetime
from typing import Optional, Union, Literal, TYPE_CHECKING, Any
from pydantic import BaseModel as BM


class BaseModel(BM):
    class Config:
        orm_mode = True
        validate_assignment = True


from pydantic import conlist, constr, ValidationError, validator
from pydantic.dataclasses import dataclass

from sqlmodel import SQLModel as SQLM

class SQLModel(SQLM):
    class Config:
        validate_assignment = True

from sqlmodel import (
    create_engine, Session,  MetaData,
    select, Relationship, Field, text
)
import uuid

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
