from sqlite3 import Connection


# ###### ОЧИЩЕННЯ УЧАСНИКІВ НАРЯДУ / DELETE WORK PERMIT PARTICIPANTS ######
def delete_work_permit_participants(connection: Connection, work_permit_id: int) -> None:
    """Видаляє учасників наряду перед повторним записом контрольованого списку.
    Deletes work permit participants before writing the controlled list again.
    """

    connection.execute(
        "DELETE FROM work_permit_participants WHERE work_permit_id = ?;",
        (work_permit_id,),
    )
