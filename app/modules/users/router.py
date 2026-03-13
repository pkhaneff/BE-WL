from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
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


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_account(current_user: CurrentUser, db: DBSession) -> None:
    service = UserProfileService(db)
    service.deactivate_account(current_user.id)
