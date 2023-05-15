from collections import defaultdict

from app.database import db
from fastapi import APIRouter, Body, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pymongo import ReturnDocument

router = APIRouter()

@router.post("/login", response_description="User Login")
async def login(kpi_id: str, feature: FeatureIn = Body(...)):
    ...

@router.post("", response_description="Add new feature", response_model=Feature)
async def create(kpi_id: str, feature: FeatureIn = Body(...)):
    kpi = KeyPerformanceIndicator(**await db["kpis"].find_one({"_id": kpi_id}))
    if len(feature.features) > 0:
        kpi.generate_time_feature_manual(feature.features)
        new_kpi = await db["kpis"].find_one_and_update(
            {"_id": kpi_id},
            {"$set": {"features": jsonable_encoder(kpi.features)}},
            return_document=ReturnDocument.AFTER,
        )

    return JSONResponse(new_kpi, status_code=status.HTTP_201_CREATED)


@router.get("/{feature_id}/series", response_description="get series data of one feature")
async def get_series(kpi_id: str, feature_id: str, start: int, stop: int, request: Request):
    start = pd.to_datetime(start, utc=True, unit="ms")
    stop = pd.to_datetime(stop, utc=True, unit="ms")

    kpi = await db["kpis"].find_one({"_id": kpi_id})
    if kpi is None:
        return JSONResponse(None, status_code=status.HTTP_404_NOT_FOUND)

    kpi = KeyPerformanceIndicator(**kpi)
    feature = kpi.get_feature_by_id(feature_id)
    if feature is None:
        return JSONResponse(None, status_code=status.HTTP_404_NOT_FOUND)

    # must filter group items for performance reason
    filters = defaultdict(list)
    for query_key, query_value in request.query_params.multi_items():
        if query_key not in ("start", "stop"):
            if isinstance(query_value, list):
                filters[query_key].extend(query_value)
            else:
                filters[query_key].append(query_value)
    filter_keys = filters.keys()
    if not all(name in filter_keys for name in kpi.group_names):
        return JSONResponse("group features must be filtered", status_code=status.HTTP_400_BAD_REQUEST)

    series = await kpi.get_series(db, feature, start, stop, filters=list(filters.items()))
    return Response(
        series.to_json(orient="split", index=False),
        status_code=status.HTTP_200_OK,
        media_type="application/json",
    )


@router.delete(
    "/{feature_id}",
    response_description="delete feature",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_by_id(kpi_id: str, feature_id: str):
    await db["kpis"].find_one_and_update({"_id": kpi_id}, {"$pull": {"features": {"_id": feature_id}}})


@router.post("/cn-holiday", response_description="Add new holiday feature", response_model=Feature)
async def create_cn_holiday(kpi_id: str):
    kpi = KeyPerformanceIndicator(**await db["kpis"].find_one({"_id": kpi_id}))
    kpi.generate_cn_holiday_feature()
    await kpi.save(db)

    return JSONResponse(jsonable_encoder(kpi), status_code=status.HTTP_201_CREATED)
