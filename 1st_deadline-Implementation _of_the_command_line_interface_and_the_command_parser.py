# 1й дедлайн: Реалізація інтерфейсу командного рядка (взаємодія із користувачем) і парсеру команд
# Із реалізацією наступних частин - може удосконалюватись

class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns):
        if name in self.tables:
            raise ValueError(f"Table {name} already exists.")
        table = "Table(name, columns)" # Тут буде команда, що створить таблицю
        self.tables[name] = table
        print(f"Table {name} has been created.")

    def insert_into(self, name, values):
        if name not in self.tables:
            raise ValueError(f"Table {name} does not exist.")
        table = self.tables[name]
        # table.add_row(values) - це майбутня команда додавання рядка
        print(f"1 row has been inserted into {name}.")

    def select_from(self, name, where=None, order_by=None):
        if name not in self.tables:
            raise ValueError(f"Table {name} does not exist.")
        table = self.tables[name]
        result = f"table.select(where_clause={where}, order_by={order_by})" # Це протатим майбутньої команди пошуку
        print(result)


# Парсинг команд
def parse_command(command, db):
    command = command.strip().rstrip(';')
    if command.startswith("CREATE"):
        parse_create(command, db)
    elif command.startswith("INSERT"):
        parse_insert(command, db)
    elif command.startswith("SELECT"):
        parse_select(command, db)
    else:
        print(f"Unknown command: {command}")

def parse_create(command, db):
    parts = command.split(' ', 2)
    table_name = parts[1]
    columns_def = parts[2].strip('()')
    columns = [col.strip().split()[0] for col in columns_def.split(',')]
    db.create_table(table_name, columns)

def parse_insert(command, db):
    parts = command.split(' ', 3)
    table_name = parts[2] if parts[1] == "INTO" else parts[1]
    values = parts[-1].strip('()').split(',')
    values = [v.strip().strip('"') for v in values]
    db.insert_into(table_name, values)

def parse_select(command, db):
    parts = command.split(' ', 3)
    table_name = parts[2]
    where_clause = None
    order_by_clause = None
    
    # Обробка WHERE
    if 'WHERE' in command:
        where_index = command.index('WHERE') + len('WHERE')
        where_end = command.find('ORDER_BY') if 'ORDER_BY' in command else len(command)
        where_part = command[where_index:where_end].strip()
        col, op, val = where_part.split(' ', 2)
        val = val.strip('"')
        where_clause = (col, op, val)
    
    # Обробка ORDER_BY
    if 'ORDER_BY' in command:
        order_by_index = command.index('ORDER_BY') + len('ORDER_BY')
        order_by_part = command[order_by_index:].strip().split(' ')
        order_by_clause = [(order_by_part[i], order_by_part[i + 1]) for i in range(0, len(order_by_part), 2)]
    
    db.select_from(table_name, where=where_clause, order_by=order_by_clause)

# Головна програма
if __name__ == "__main__":
    db = Database()
    while True:
        try:
            command = input("> ")
            parse_command(command, db)
        except Exception as e:
            print(f"Error: {e}")
