class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, table_name, columns):
        if table_name in self.tables:
            print(f"Error: Table {table_name} already exists.")
            return

        table_structure = {
            "columns": [],
            "data": [],
            "indexed_columns": {}
        }

        for column in columns:
            parts = column.split()
            column_name = parts[0]
            is_indexed = len(parts) > 1 and parts[1].upper() == "INDEXED"
            table_structure["columns"].append(column_name)
            if is_indexed:
                table_structure["indexed_columns"][column_name] = {}

        self.tables[table_name] = table_structure
        print(f"Table {table_name} has been created.")

    def insert_into(self, table_name, values):
        if table_name not in self.tables:
            print(f"Error: Table {table_name} does not exist.")
            return

        table = self.tables[table_name]
        if len(values) != len(table["columns"]):
            print(f"Error: Column count does not match value count.")
            return

        row_id = len(table["data"])
        row = dict(zip(table["columns"], values))
        table["data"].append(row)

        for column_name, index in table["indexed_columns"].items():
            value = row[column_name]
            if value not in index:
                index[value] = []
            index[value].append(row_id)

        print(f"1 row has been inserted into {table_name}.")

    def select_from(self, table_name, where_clause=None, order_by_clause=None):
        if table_name not in self.tables:
            print(f"Error: Table {table_name} does not exist.")
            return

        table = self.tables[table_name]
        columns = table["columns"]

        rows = []
        if where_clause:
            column_name, operator, value, constant = where_clause
            if operator == "=" and column_name in table["indexed_columns"] and constant:
                index = table["indexed_columns"][column_name]
                if value in index:
                    row_ids = index[value]
                    rows = [table["data"][row_id] for row_id in row_ids]
            else:
                rows = [row for row in table["data"] if self.evaluate_where(row, where_clause)]
        else:
            rows = table["data"]

        if order_by_clause:
            for column_name, order in reversed(order_by_clause):
                reverse = order.upper() == "DESC"
                rows.sort(key=lambda r: r[column_name], reverse=reverse)

        self.print_table(columns, rows)

    def evaluate_where(self, row, where_clause):
        column_name, operator, value, constant = where_clause
        left_value = row[column_name].upper()
        right_value = value.upper() if constant else row[value].upper()

        if operator == ">" and left_value.upper() > right_value.upper():
            return True
        elif operator == "<" and left_value.upper() < right_value.upper():
            return True
        elif operator == ">=" and left_value.upper() >= right_value.upper():
            return True
        elif operator == "<=" and left_value.upper() <= right_value.upper():
            return True
        elif operator == "=" and left_value.upper() == right_value.upper():
            return True
        return False

    def print_table(self, columns, rows):
        column_widths = {col: len(col) for col in columns}

        for row in rows:
            for col in columns:
                column_widths[col] = max(column_widths[col], len(row[col]))

        separator = "+" + "+".join(["-" * (column_widths[col] + 2) for col in columns]) + "+"
        header = "| " + " | ".join([col.ljust(column_widths[col]) for col in columns]) + " |"

        print(separator)
        print(header)
        print(separator)

        for row in rows:
            line = "| " + " | ".join([row[col].ljust(column_widths[col]) for col in columns]) + " |"
            print(line)

        print(separator)

    def show_indexed_columns(self, table_name):
        if table_name not in self.tables:
            print(f"Error: Table {table_name} does not exist.")
            return

        table = self.tables[table_name]
        indexed_columns = table["indexed_columns"]

        if not indexed_columns:
            print(f"No indexed columns in table {table_name}.")
            return

        print(f"Indexed columns in table '{table_name}':")
        for column, index_data in indexed_columns.items():
            print(f"  - {column}: {index_data}")

# Парсинг команд
def parse_command(command, db):
    command = command.split(';')[0].strip()
    if command.upper().startswith("CREATE"):
        parse_create(command, db)
    elif command.upper().startswith("INSERT"):
        parse_insert(command, db)
    elif command.upper().startswith("SELECT"):
        parse_select(command, db)
    elif command.upper().startswith("SHOW INDEXES"):
        table_name = command.split(' ')[2].strip()
        db.show_indexed_columns(table_name)
    else:
        print(f"Unknown command: {command}")

def parse_create(command, db):
    command = command.split(' ', 1)[1].strip()
    parts = command.split(' ', 1)
    table_name = parts[0]
    columns_def = parts[1].split('(')[1].split(')')[0]
    columns = columns_def.split(',')
    for i in range(len(columns)):
        columns[i] = columns[i].strip()
    db.create_table(table_name, columns)

def parse_insert(command, db):
    command = command.split(' ', 1)[1].strip()
    if command.upper().startswith("INTO"):
        command = command.split(' ', 1)[1].strip()
    parts = command.split(' ', 1)
    table_name = parts[0]
    values = parts[1].split('(')[1].split(')')[0]
    values = values.split(',')
    for i in range(len(values)):
        values[i] = values[i].strip().strip('"').strip("'")
    db.insert_into(table_name, values)

def parse_select(command, db):
    where_clause = None
    order_by_clause = None
    command = command.split(';')[0].strip()
    command = command.split(' ', 1)[1].strip()
    command = command.split(' ', 1)[1].strip()
    parts = command.split(' ', 1)
    table_name = parts[0]
    if len(parts) > 1:
        parts[1] = parts[1].strip()
        if parts[1].upper().startswith("WHERE"):
            parts[1] = parts[1].split(' ', 1)[1].strip()
            where_column_name = parts[1].split(' ', 1)[0].strip()
            parts[1] = parts[1].split(' ', 1)[1].strip()
            operator = parts[1].split(' ', 1)[0].strip()
            parts[1] = parts[1].split(' ', 1)[1].strip()
            if parts[1].upper().startswith('"'):
                constant = True
                parts[1] = parts[1].strip('"').strip()
                value = parts[1].split(' ', 1)[0].strip() if len(parts[1].split(' ', 1)) > 1 else parts[1].strip()
                parts[1] = parts[1].split(' ', 1)[1].strip() if len(parts[1].split(' ', 1)) > 1 else None
            else:
                constant = False
                value = parts[1].split(' ', 1)[0].strip() if len(parts[1].split(' ', 1)) > 1 else parts[1].strip()
                parts[1] = parts[1].split(' ', 1)[1].strip() if len(parts[1].split(' ', 1)) > 1 else parts[1].strip()
            where_clause = [where_column_name, operator, value, constant]
        if parts[1] != None and parts[1].upper().startswith("ORDER_BY"):
            order_by_clause = []
            parts[1] = parts[1].split(' ', 1)[1].strip()
            while parts[1] != None:
                order_by_column_name = parts[1].split(' ', 1)[0].strip()
                parts[1] = parts[1].split(' ', 1)[1].strip()
                order = parts[1].split(' ', 1)[0].strip()
                parts[1] = parts[1].split(' ', 1)[1].strip() if len(parts[1].split(' ', 1)) > 1 else None
                if parts[1] != None and parts[1].startswith(","):
                    parts[1] = parts[1].split(' ', 1)[1].strip()
                order_by_clause_set = [order_by_column_name, order]
                order_by_clause.append(order_by_clause_set)
    db.select_from(table_name, where_clause, order_by_clause)


# Головна програма
if __name__ == "__main__":
    db = Database()
    while True:
        try:
            command = input("> ")
            parse_command(command, db)
        except Exception as e:
            print(f"Error: {e}")
