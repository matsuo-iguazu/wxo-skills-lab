from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from pydantic import BaseModel, Field
from typing import Optional


class CoffeeRequestResult(BaseModel):
    """コーヒーリクエスト受付結果"""
    accepted: bool = Field(description="リクエストを受け付けたかどうか")
    confirmation_message: str = Field(description="依頼者への確認メッセージ")
    staff_notification: str = Field(description="給仕担当者への通知メッセージ")
    rejection_reason: Optional[str] = Field(default=None, description="受付不可の場合の理由")


@tool(permission=ToolPermission.READ_WRITE)
def m_accept_coffee_request(
    room_name: str,
    cup_count: int,
    coffee_type: str,
    requester_name: Optional[str] = None,
) -> CoffeeRequestResult:
    """
    コーヒーのリクエストを受け付け、給仕担当者への通知メッセージを生成する。

    物理的な作業（コーヒーを淹れる・運ぶ）は人間の給仕担当者が行う。
    このツールはリクエストの受付・バリデーション・通知メッセージ生成までを担当する。

    Args:
        room_name (str): 届け先の会議室名（例: 会議室A、第1会議室）
        cup_count (int): コーヒーの杯数（1以上）
        coffee_type (str): コーヒーの種類（例: ブラック、ミルクあり、砂糖あり）
        requester_name (Optional[str]): 依頼者の名前（省略可）

    Returns:
        CoffeeRequestResult: 受付結果・確認メッセージ・担当者通知メッセージ
    """
    # バリデーション: 杯数チェック
    if cup_count < 1:
        return CoffeeRequestResult(
            accepted=False,
            confirmation_message="申し訳ありません、杯数は1杯以上で指定してください。",
            staff_notification="",
            rejection_reason="杯数が0以下です。",
        )

    # バリデーション: 会議室名チェック（空文字禁止）
    if not room_name or not room_name.strip():
        return CoffeeRequestResult(
            accepted=False,
            confirmation_message="申し訳ありません、届け先の会議室名を教えてください。",
            staff_notification="",
            rejection_reason="会議室名が指定されていません。",
        )

    requester_info = f"（{requester_name}様より）" if requester_name else ""

    confirmation = (
        f"承りました{requester_info}。"
        f"**{room_name}** に **{coffee_type}** を **{cup_count}杯** お届けします。"
        f"しばらくお待ちください。"
    )

    notification = (
        f"【コーヒーリクエスト】\n"
        f"届け先: {room_name}\n"
        f"種類: {coffee_type}\n"
        f"杯数: {cup_count}杯\n"
        f"依頼者: {requester_name if requester_name else '不明'}\n"
        f"対応をお願いします。"
    )

    return CoffeeRequestResult(
        accepted=True,
        confirmation_message=confirmation,
        staff_notification=notification,
        rejection_reason=None,
    )
