import csv
import json
import psycopg2 as ps
import base64 as b64


def initialise_config():
    with open("config.json", 'r') as f:
        config = json.loads(f.read())
        config['password'] = b64.b64decode(config['password']).decode()
    return config


def read_from_database(sql_query: str, config: dict):
    try:
        with ps.connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                response = cursor.fetchall()
                # for item in cursor.description:
                #     print(item.name)  -> list comprehension:
                columns = [item.name for item in cursor.description]

                new_data = []
                for employee in response:
                    new_data.append(dict(zip(columns, employee)))
                return new_data

    except Exception as e:
        print(f"Failure on reading from database. Error: {e}")

def execute_query(sql_query: str, config: dict):
    try:
        with ps.connect(**config) as conn:
            with conn.cursor() as cursor:
                a = cursor.execute(sql_query)
                print("Successfully executed!")
                return True
    except Exception as e:
        print(f"Failure on reading from database. Error: {e}")
        return False


if __name__ == '__main__':
    budget_cap = 0.8
    menu = """"
    1. Show all employees
    2. Show all employeed by department
    3. Show all projects of a certain employee
    4. Change salary of employy
    5. Hire new employee
    6. Fire employee
    """

    config = initialise_config()

    user_pick = input(menu + "\n")
    match user_pick:
        case "1":
            emps = read_from_database("select * from company.employees", config)
            print(json.dumps(emps, indent=4))
        case "2":

            departments = read_from_database("select * from company.departments", config)
            for department in departments:
                print(f"{department['department_id']}. {department['name']}")
            department_pick = input("Choose a department: ")
            emps = read_from_database(f"select * from company.employees where department_id = {department_pick}", config)
            print(json.dumps(emps, indent=4))
        case "3":


            pass
        case "4":
            emp= {}
            emps = read_from_database("select emp_id, name, salary from company.employees", config)
            for emp in emps:
                print(f"{emp['emp_id']}. {emp['name']}")
            emp_pick = input("Choose employee")
            for emp in emps:
                if emp_pick == emp['emp_id']:
                    break

            available_budget_query = f"""select sum(p.budget) from company.projects p 
                                        join company.contracts c on c.project_id = p.project_id 
                                        join company.employees e on e.emp_id = c.emp_id 
                                        where e.emp_id = {emp_pick};"""
            budget = read_from_database(available_budget_query,config)
            percentage = input("What is the raise in percentage? ")
            new_salary = emp['salary'] + emp['salary'] * float(percentage)/100

            if new_salary < budget[0]['sum'] * budget_cap:
                execute_query(f"UPDATE company.employees set salary = {new_salary} where emp_id = {emp_pick}", config)
            else:
                print("Not enough money for the raise")

        case "5":
            emps = read_from_database("select emp_id, name from company.employees", config)
            departments = read_from_database("select department_id, name from company.departments", config)
            new_emp_data = input("Enter all data about employee: name/date_of_birth/salary/starting_date \n")
            new_emp_data = new_emp_data.split("/")
            for department in departments:
                print(f"{department['department_id']}, {department['name']}")
            department_choice = input()

            if new_emp_data[0] not in str(emps):
                query = (f"INSERT into company.employees(name,date_of_birth,salary,starting_date,department_id) values ('{new_emp_data[0]}', '{new_emp_data[1]}', {new_emp_data[2]}, '{new_emp_data[3]}', {department_choice})")
                execute_query(query, config)

            pass
        case "6":
            emps = read_from_database("select emp_id, name from company.employees", config)
            for emp in emps:
                print(f"{emp['emp_id']}. {emp['name']}")
            emp_pick = input("Choose employee")
            consent = input("Are you sure you want to fire the employee? Y/N ")
            if consent.lower() == "y":
                execute_query(f"DELETE from company.employees where emp_id = {emp_pick}", config)

        case _:
            print("Wrong option")