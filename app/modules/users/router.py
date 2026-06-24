from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import CurrentUser, DBSession, S3UploaderDep
from app.modules.users.schemas import UserProfileResponse, UserProfileUpdate
from app.modules.users.service import UserProfileService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user: CurrentUser) -> UserProfileResponse:
    return UserProfileResponse.model_validate(current_user)


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    payload: UserProfileUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> UserProfileResponse:
    service = UserProfileService(db)
    updated_user = service.update_profile(current_user.id, payload)
    return UserProfileResponse.model_validate(updated_user)


@router.put("/me/avatar", response_model=UserProfileResponse)
def update_my_avatar(
    current_user: CurrentUser,
    db: DBSession,
    s3_uploader: S3UploaderDep,
    avatar: UploadFile = File(...),
) -> UserProfileResponse:
    service = UserProfileService(db, s3_uploader=s3_uploader)
    updated_user = service.update_avatar(
        current_user.id,
        fileobj=avatar.file,
        filename=avatar.filename or "avatar",
        content_type=avatar.content_type,
    )
    return UserProfileResponse.model_validate(updated_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_account(current_user: CurrentUser, db: DBSession) -> None:
    service = UserProfileService(db)
    service.deactivate_account(current_user.id)
