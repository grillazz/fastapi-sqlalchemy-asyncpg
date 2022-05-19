from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
import pandas as pd
from pathlib import Path
import inspect
import numpy as np
import pydantic
from typing import Union, Dict, Type
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


from the_app.utils import get_logger

router = APIRouter(prefix="/v1/upload")

logger = get_logger(__name__)

@router.post("/uploadcsv")
async def upload_csv(csv_file: UploadFile = File(...)):
    df = pd.read_csv(csv_file.file)
    print(df)

def create_query_param(name: str, type_: Type, default) -> pydantic.fields.ModelField:
    """Create a query parameter just like fastapi does."""
    param = inspect.Parameter(
        name=name,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=default,
        annotation=type_,
    )
    field = fastapi.dependencies.utils.get_param_field(
        param=param, param_name=name, default_field_info=fastapi.params.Query
    )
    return field

def dtype_to_type(dtype) -> Type:
    """Convert numpy/pandas dtype to normal Python type."""
    if dtype == np.object:
        return str
    else:
        return type(np.zeros(1, dtype).item())

def as_int_or_float(val):
    """Infers Python int vs. float from string representation."""
    if type(val) == str:
        ret_val = float(val) if '.' in val else int(val)
        return ret_val
    return val


