
class Company:
    def __init__(self, name, Departments):
        self.name = name
        self.depts = Departments

    def __str__(self):
        return 'Company {} {}'.format(self.name, map(str, self.depts))

class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def __str__(self):
        return 'Employee {} {}'.format(self.name, self.salary)

class Department:
    def __init__(self, name, manager, subunits):
        self.name = name
        self.manager = manager
        self.subunits = subunits

    def __str__(self):
        return 'Department "{}" ({}) [{}]'.format(self.name, self.manager, ', '.join(map(str, self.subunits)))

company = Company(
    name = "Meganalysis",
    Departments = [
        Department(
            name = "Research",
            manager = Employee(
                name = "Craig",
                salary = 123456.0
            ),
            subunits = [
                Employee(
                    name = "Erik",
                    salary = 12345.0
                ),
                Employee(
                    name = "Ralf",
                    salary = 1234.0
                )
            ]
        ),
        Department(
            name = "Development",
            manager = Employee(
                name = "Ray",
                salary = 234567.0
            ),
            subunits = [
                Department(
                    name = "Dev1",
                    manager = Employee(
                        name = "Klaus",
                        salary = 23456.0
                    ),
                    subunits = [
                        Department(
                            name = "Dev1.1",
                            manager = Employee(
                                name = "Karl",
                                salary = 2345.0
                            ),
                            subunits = [
                                Employee(
                                    name = "Joe",
                                    salary = 2344.0
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


