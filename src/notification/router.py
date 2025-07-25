import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text

import src.accounts.service as account_service
import src.notification.service as notification_service
import src.users.service as user_service
from src.admins.schemas import Admin
from src.database import get_db
from src.exc import EloraApplicationError
from src.utils.exc import InvalidJSONFormatError
from src.notification.schemas import (
    NotificationsResponse,
    NotificationStatus,
    NotificationType,
    NotificationResponse,
    NotificationCreate,
    NotificationModify,
)

notification_router = APIRouter()

logger = logging.getLogger("uvicorn.error")


@notification_router.get(
    "/notifications/", tags=["Notification"], response_model=NotificationsResponse
)
def get_notifications(
    offset: int = None,
    limit: int = None,
    sort: str = None,
    approve: int = -1,
    status: NotificationStatus = None,
    type_: NotificationType = None,
    account_id: int = 0,
    user_id: int = 0,
    q: str = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    if sort is not None:
        opts = sort.strip(",").split(",")
        sort = []
        for opt in opts:
            try:
                sort.append(notification_service.NotificationSortingOptions[opt])
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f'"{opt}" is not a valid sort option'
                )

    notifications, count = notification_service.get_notifications(
        db=db,
        offset=offset,
        limit=limit,
        sort=sort,
        status=status,
        approve=approve,
        account_id=account_id,
        user_id=user_id,
        notification_type=type_,
        q=q,
    )

    return {"notifications": notifications, "total": count}


@notification_router.post("/notifications/bulk_send", tags=["Notification"])
def bulk_send_notification(
    notification: NotificationCreate,
    user_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):

    target_user_ids = []

    if user_ids is not None:
        for uid in user_ids:  # Renamed for clarity that it's a string
            try:
                # Attempt to convert each item to an integer
                # This will skip non-integer strings like ""
                if uid:
                    target_user_ids.append(int(uid))
            except (ValueError, TypeError):
                # Handle cases where uid_str is not a valid integer or is None/empty string
                continue  # Skip invalid entries

    # The rest of your logic remains the same.
    # It will now correctly trigger if the user_ids list was empty or contained only invalid entries.
    if not target_user_ids:
        # If user_ids is None or empty after cleaning, fetch all user_ids
        result = db.execute(text("SELECT user_id FROM club_profile"))
        target_user_ids = [row[0] for row in result.fetchall()]

    if not target_user_ids:
        print("No user IDs to send notifications to.")
        return

    try:
        notification_service.create_bulk_notification(
            db=db,
            user_ids=target_user_ids,
            notification=notification,
        )
    except InvalidJSONFormatError as error:
        raise HTTPException(status_code=400, detail=error.message())
    except IntegrityError as error:
        logger.error(error)
        raise HTTPException(status_code=409, detail="Error in create notifications")
    except EloraApplicationError as error:
        raise HTTPException(status_code=409, detail=error.message())


@notification_router.post(
    "/notifications/", tags=["Notification"], response_model=NotificationResponse
)
def add_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_user = user_service.get_user(db, notification.user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_account = None

    if notification.account_id and notification.account_id != 0:
        db_account = account_service.get_account(
            db=db, account_id=notification.account_id
        )

        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")

    try:
        db_notification = notification_service.create_notification(
            db=db,
            db_user=db_user,
            db_account=db_account if db_account else None,
            notification=notification,
        )
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Notification already exists")
    except EloraApplicationError as error:
        raise HTTPException(status_code=409, detail=error.message())

    return db_notification


@notification_router.put(
    "/notifications/{notification_id}",
    tags=["Notification"],
    response_model=NotificationResponse,
)
def modify_notification(
    notification_id: int,
    notification: NotificationModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_notification = notification_service.get_notification(
        db, notification_id=notification_id
    )
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification_service.update_notification(
        db=db, db_notification=db_notification, modify=notification
    )


@notification_router.delete("/notifications/{notification_id}", tags=["Notification"])
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    db_notification = notification_service.get_notification(
        db, notification_id=notification_id
    )
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification_service.remove_notification(db=db, db_notification=db_notification)

    return {}
