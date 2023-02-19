import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from fastapi import Depends, APIRouter, HTTPException
from src.gps_tracker.manager import GpsTrackerManager
from src.home_assistant.client import HomeAssistant
from src.owntracks.manager import OwntracksManager
from src.owntracks.schema import OwntracksEncryptedRecordBase


router = APIRouter(
    prefix="/owntracks",
    tags=["owntracks"],
)

@router.post('/{url_id}/', response_model=dict, status_code=200)
async def create_owntracks_record(
    encrypted_record: OwntracksEncryptedRecordBase,
    url_id: str = None
):
    # check if it's a known owntracks tracker (by checking the url_id)
    gps_tracker = await GpsTrackerManager().get_gpstracker_by_url_id(url_id=url_id)
    if gps_tracker:
        otm = OwntracksManager(encrypted_record=encrypted_record)
        asyncio.create_task(otm.create_owntracks_record(gpstracker=gps_tracker))
        if otm.raw_record['_type'] in ['location', 'transition']:
            if os.environ.get('FORWARD_TO_HA') in ['true','True','yes','Yes']:
                asyncio.create_task(HomeAssistant.forward(encrypted_record.data))
            return await otm.build_ot_reply()
        return []
    raise HTTPException(status_code=422, detail="Tracker not found")