from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000.")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value.strip():
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string.")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        from employee import Employee  # Ensure Employee class is accessible

        if isinstance(value, int):
            employee = CURSOR.execute("SELECT id FROM employees WHERE id = ?", (value,)).fetchone()
            if employee:
                self._employee_id = value
                return

        raise ValueError("employee_id must be the ID of a persisted Employee.")

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
        INSERT INTO reviews(year, summary, employee_id)
        VALUES(?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        self.id = CURSOR.lastrowid

        CONN.commit()
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        new_review = cls(year, summary, employee_id)

        new_review.save()
        return new_review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        id = row[0]

        if id in cls.all:
            instance = cls.all[id]
            instance.year = row[1]
            instance.summary = row[2] 
            instance.employee_id = row[3]

        else:
            instance = cls(
                year=row[1],
                summary=row[2],
                employee_id=row[3]
            )
            instance.id = id  
            cls.all[id] = instance
    
        return instance


    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        
        sql = """
            SELECT *
            FROM reviews
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()

        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
        UPDATE reviews
        SET year = ?, summary = ?, employee_id = ?
        WHERE id = ?
        """

        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        
        sql = """
        DELETE FROM reviews
        WHERE id = ?
        """

        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        if self.id in type(self).all:
            del type(self).all[self.id]
        
        self.id = None


    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        
        reviews = []
        for row in rows:
            
            id, year, summary, employee_id = row
            review = cls(year, summary, employee_id)
            review.id = id
            cls.all[id] = review  
            reviews.append(review)

        return reviews

