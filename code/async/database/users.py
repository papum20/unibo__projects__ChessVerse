
from typing import Optional

from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from database import _DATABASES
from const.users import RANKS



class DatabaseHandlerUsers:

<<<<<<< HEAD
	cursor:Optional[MySQLCursor]	= None
=======
	cursor:Optional[MySQLCursor] = None
>>>>>>> merge-ranked
	connector:Optional[MySQLConnection]	= None


	def __init__(self):
		pass

<<<<<<< HEAD
	def __init__(self, cursor:MySQLCursor, connector:MySQLConnection):
		self.cursor = cursor
		self.connector = connector

=======
>>>>>>> merge-ranked

	# get functions

	def get_user_rank(self, session_id:str, rank_type:str) -> int:
		"""
		:param session_id: session id field
		:param rank_type: game type, form const.RANKS
		"""

		if rank_type not in RANKS:
			print("Invalid rank type")
			return 0

		if session_id is None:
			print("Invalid session id")
			return 0
		
		self.cursor.execute(
			f"""
			SELECT {rank_type} 
			FROM {_DATABASES['registered_users']} 
			WHERE session_id = %s
			""",
			(session_id,)
		)
		rank = self.cursor.fetchone()

		print(f"[db] got rank:{rank}")
		#prendo le informazioni dal database e le salvo in session
		return rank

	# update functions

	def set_user_rank(self, session_id:str, rank_type:str, diff:int) -> bool:
		"""
		:param session_id: session id field
		:param rank_type: game type, form const.RANKS
		:param diff: `new_rank-old_rank`
		
		:return: True if success, False otherwise
		"""

		if rank_type not in RANKS:
			print("Invalid rank type")
			return 0
		
		if session_id is None:
			print("Invalid session id")
			return 0

		old_rank = self.get_user_rank(session_id, rank_type)

		self.cursor.execute(
			f"""
			UPDATE {_DATABASES['registered_users']} 
			SET {rank_type} = %(new_rank)s
			WHERE session_id = %(sid)s
			""",
			{
				'new_rank': old_rank + diff,
				'sid': session_id
			}
		)
		self.connector.commit()

		print(f"[db] set rank to:{old_rank + diff}")
		return True