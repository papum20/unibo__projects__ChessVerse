
from typing import Optional

from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from database import _DATABASES
from const.users import RANKS



class DatabaseHandlerUsers:

	cursor:Optional[MySQLCursor] = None
	connector:Optional[MySQLConnection]	= None


	def __init__(self):
		pass


	# get functions

	def get_user_rank(self, session_id:str, rank_type:str) -> int:
		"""
		:param session_id: session id field
		:param rank_type: game type, form const.RANKS
		"""

		if rank_type not in RANKS:
			#print("[err][db] Invalid rank type")
			return 0

		if session_id is None:
			#print("[err][db] Invalid session id")
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
		#print(f"[db] rank tuple is:{rank}")
		rank = rank[0]

		#print(f"[db] got rank:{rank}")
		#prendo le informazioni dal database e le salvo in session
		return rank

	# update functions

	def set_user_rank(self, session_id:str, rank_type:str, new_rank:int) -> bool:
		"""
		:param session_id: session id field
		:param rank_type: game type, form const.RANKS
		:param new_rank: new_rank
		
		:return: True if success, False otherwise
		"""

		if rank_type not in RANKS:
			#print("[err][db] Invalid rank type")
			return 0
		
		if session_id is None:
			#print("[err][db] Invalid session id")
			return 0

		self.cursor.execute(
			f"""
			UPDATE {_DATABASES['registered_users']} 
			SET {rank_type} = %(new_rank)s
			WHERE session_id = %(session_id)s
			""",
			{
				'new_rank': new_rank,
				'session_id': session_id
			}
		)
		self.connector.commit()

		#print(f"[db] set rank to:{new_rank}")
		return True