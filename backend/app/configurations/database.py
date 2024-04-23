from sqlmodel import create_engine

"""
==========================================================================
 ➠ Database Configuration File
 ➠ Section By: Fabricio Abreu
 ➠ Related system: Database (SQLite)
==========================================================================
"""

engine = create_engine("sqlite:///app/database/twitter.db")
