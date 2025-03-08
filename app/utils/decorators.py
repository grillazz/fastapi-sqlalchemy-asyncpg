from functools import wraps

from sqlalchemy.dialects import postgresql


def compile_sql_or_scalar(func):
    """
    A decorator that compiles an SQL statement or executes it and returns the first scalar result.

    Args:
        func (Callable): The function to be decorated. It should return an SQLAlchemy statement.

    Returns:
        Callable: A wrapper function that either compiles the SQL statement or executes it and returns the first scalar result.
    """

    @wraps(func)
    async def wrapper(cls, db_session, name, compile_sql=False, *args, **kwargs):
        """
        Wrapper function that either compiles the SQL statement or executes it.

        Args:
            cls (Type): The class on which the method is called.
            db_session (AsyncSession): The SQLAlchemy async session.
            name (str): The name to be used in the SQL statement.
            compile_sql (bool, optional): If True, compiles the SQL statement. Defaults to False.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Compiled SQL statement or the first scalar result of the executed statement.
        """
        stmt = await func(cls, db_session, name, *args, **kwargs)
        if compile_sql:
            return stmt.compile(
                dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
            )
        result = await db_session.execute(stmt)
        return result.scalars().first()

    return wrapper
