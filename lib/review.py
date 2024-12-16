from __init__ import CURSOR, CONN

class Review:
    # Dictionary to store instances
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # Triggers setter for 'year'
        self.summary = summary  # Triggers setter for 'summary'
        self.employee_id = employee_id  # Triggers setter for 'employee_id'

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):  # Ensure year is an integer
            raise ValueError("Year must be an integer.")
        if value < 2000:  # Ensure year is >= 2000
            raise ValueError("Year must be greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):  # Ensure summary is a string
            raise ValueError("Summary must be a string.")
        if len(value.strip()) == 0:  # Ensure summary is not empty
            raise ValueError("Summary must have at least one character.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):  # Ensure employee_id is an integer
            raise ValueError("Employee ID must be an integer.")
        
        # Import Employee class locally to avoid circular imports
        from employee import Employee
        
        # Check if the employee exists in the database
        employee = Employee.find_by_id(value)
        if not employee:
            raise ValueError(f"Employee with ID {value} does not exist.")
        
        self._employee_id = value

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """Create a new table to persist Review instances."""
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
        """Drop the reviews table."""
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row into the reviews table."""
        if self.id is None:  # New Review instance, insert into database
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid  # Get the primary key (ID) of the new row
            
            # Save the instance in the class-level dictionary
            Review.all[self.id] = self
        else:  # Existing Review instance, update the database row
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save it to the database."""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        if row[0] in cls.all:  # Check if instance already exists in the dictionary
            return cls.all[row[0]]
        
        review = cls(year=row[1], summary=row[2], employee_id=row[3], id=row[0])
        cls.all[row[0]] = review  # Store the instance in the dictionary
        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance by its ID."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """Update the table row for the current Review instance."""
        if self.id is None:
            raise ValueError("Cannot update a review that hasn't been saved to the database yet.")
        
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the row corresponding to this Review instance."""
        if self.id is None:
            raise ValueError("Cannot delete a review that hasn't been saved to the database yet.")
        
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        # Remove from the class-level dictionary
        del Review.all[self.id]
        self.id = None  # Reset the ID attribute

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances."""
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        
        reviews = []
        for row in rows:
            reviews.append(cls.instance_from_db(row))
        
        return reviews
